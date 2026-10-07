import os
import time

import numpy as np
import onnxruntime as ort
import onnxruntime_qnn as qnn

model_path = "resnet18_local.onnx"
warmup_iterations = 10
iterations_per_round = 100
rounds = 3


def benchmark(session, input_feed, iterations):
    # Exclude session creation and measure only repeated inference calls.
    start_time = time.perf_counter()
    for _ in range(iterations):
        session.run(None, input_feed)
    return time.perf_counter() - start_time


try:
    # Keep the DLL search path available while ONNX Runtime loads QNN libraries.
    qnn_dll_directory = os.add_dll_directory(qnn.LIB_DIR_FULL_PATH)
    ort.register_execution_provider_library(qnn.get_ep_name(), qnn.get_library_path())

    qnn_devices = [
        device
        for device in ort.get_ep_devices()
        if device.ep_name == qnn.get_ep_name()
    ]
    if not qnn_devices:
        raise RuntimeError("No QNN execution devices were reported by ONNX Runtime.")

    cpu_session = ort.InferenceSession(
        model_path,
        providers=["CPUExecutionProvider"],
    )

    # Disable CPU fallback so this session cannot silently benchmark on the CPU.
    qnn_session_options = ort.SessionOptions()
    qnn_session_options.add_session_config_entry(
        "session.disable_cpu_ep_fallback", "1"
    )
    qnn_session_options.add_provider_for_devices(
        qnn_devices,
        {"backend_path": qnn.get_qnn_htp_path()},
    )
    qnn_session = ort.InferenceSession(
        model_path,
        sess_options=qnn_session_options,
    )

    qnn_name = qnn.get_ep_name()
    active_providers = qnn_session.get_providers()
    if qnn_name not in active_providers:
        raise RuntimeError(
            f"{qnn_name} is not active. Active providers: {active_providers}"
        )

    model_input = cpu_session.get_inputs()[0]
    input_shape = tuple(
        dimension if isinstance(dimension, int) else 1
        for dimension in model_input.shape
    )
    input_feed = {
        model_input.name: np.random.randn(*input_shape).astype(np.float32)
    }
    total_iterations = iterations_per_round * rounds
    total_samples = total_iterations * input_shape[0]

    # Warm both sessions before timing to reduce one-time setup effects.
    for session in (cpu_session, qnn_session):
        for _ in range(warmup_iterations):
            session.run(None, input_feed)

    cpu_total = 0.0
    qnn_total = 0.0
    # Run paired rounds so both devices process the same number of inferences.
    for _ in range(rounds):
        cpu_total += benchmark(cpu_session, input_feed, iterations_per_round)
        qnn_total += benchmark(qnn_session, input_feed, iterations_per_round)

    cpu_latency = cpu_total / total_iterations
    qnn_latency = qnn_total / total_iterations

    print(f"Model: {model_path}")
    print(f"Input shape: {input_shape}")
    print(f"QNN active providers: {active_providers}")
    print("CPU fallback for QNN: disabled")
    print(
        f"Measured {total_iterations} batches ({total_samples} samples) per device "
        f"({rounds} rounds, {warmup_iterations} warm-up runs each)."
    )
    print()
    print(f"CPU total:          {cpu_total:.4f} seconds")
    print(f"CPU average:        {cpu_latency * 1000:.4f} ms per batch")
    print(f"CPU throughput:     {total_samples / cpu_total:.2f} samples per second")
    print()
    print(f"QNN/NPU total:      {qnn_total:.4f} seconds")
    print(f"QNN/NPU average:    {qnn_latency * 1000:.4f} ms per batch")
    print(f"QNN/NPU throughput: {total_samples / qnn_total:.2f} samples per second")
    print()
    if qnn_total < cpu_total:
        print(f"QNN/NPU speedup:    {cpu_total / qnn_total:.2f}x faster")
    else:
        print(f"CPU speedup:        {qnn_total / cpu_total:.2f}x faster")
except Exception as error:
    print(f"Failed to compare CPU and QNN benchmark: {error}")
