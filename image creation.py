from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

# ---------- Spec data structures ----------

Side = Literal["left", "right"]

@dataclass
class ProstheticSpec:
    limb_side: Side              # "right" or "left"
    level: Literal["above_knee", "below_knee"]
    style: str                   # e.g. "carbon_fiber_sport"
    knee_type: str               # e.g. "mechanical", "microprocessor"
    foot_style: str              # e.g. "athletic_shoe_black"

@dataclass
class BodySpec:
    age: int
    sex: Literal["male", "female"]
    build: Literal["fit", "average", "heavy"]
    skin_tone: str
    hair_style: str
    hair_color: str
    beard_style: str

@dataclass
class PoseSpec:
    posture: Literal["seated", "standing"]
    support_device: Literal["wheelchair_sport", "none"]
    environment: str             # e.g. "riverside_path_golden_hour"
    facing_camera: bool

@dataclass
class CameraSpec:
    position: Tuple[float, float, float]   # x, y, z in world frame
    target: Tuple[float, float, float]     # look-at point
    fov_deg: float


# ---------- Parsing prompt into structured spec ----------

def parse_prompt_to_spec(prompt: str) -> tuple[BodySpec, ProstheticSpec, PoseSpec, CameraSpec]:
    """
    In a real system, this would use an LLM or rule-based parser.
    Here we hard-code for clarity.
    """
    # Example: "61-year-old fit man with right above-knee prosthesis,
    # seated in sporty wheelchair by a river, facing the camera at golden hour."
    side = "right"
    lower = prompt.lower()
    if "left" in lower and "right" not in lower:
        side = "left"
    elif "right" in lower and "left" not in lower:
        side = "right"

    body = BodySpec(
        age=61,
        sex="male",
        build="fit",
        skin_tone="light_tan",
        hair_style="short_neat",
        hair_color="silver",
        beard_style="salt_pepper_trimmed",
    )

    prosthetic = ProstheticSpec(
        limb_side=side,
        level="above_knee",
        style="carbon_fiber_sport",
        knee_type="mechanical",
        foot_style="athletic_shoe_black",
    )

    pose = PoseSpec(
        posture="seated",
        support_device="wheelchair_sport",
        environment="riverside_path_golden_hour",
        facing_camera=True,
    )

    camera = CameraSpec(
        position=(0.0, 1.6, 3.0),   # in front of subject, slightly above eye level
        target=(0.0, 1.4, 0.0),     # looking at chest/face
        fov_deg=35.0,
    )

    return body, prosthetic, pose, camera


# ---------- Anatomical model & constraints ----------

class AnatomicalModel:
    def __init__(self, body_spec: BodySpec, prosthetic_side: Side = "right"):
        self.body_spec = body_spec
        self.prosthetic_side = prosthetic_side
        self.joints = self._init_skeleton()
        self.limb_ids = {"left_leg": None, "right_leg": None}
        self._label_limbs()

    def _init_skeleton(self):
        # Placeholder: build a parametric skeleton (e.g. SMPL-like)
        return {}

    def _label_limbs(self):
        # Explicitly label left/right legs
        self.limb_ids["left_leg"] = "joint_left_hip"
        self.limb_ids["right_leg"] = "joint_right_hip"

    def attach_prosthetic(self, prosthetic_spec: ProstheticSpec):
        limb_key = f"{prosthetic_spec.limb_side}_leg"
        hip_joint = self.limb_ids[limb_key]

        # Create prosthetic components and attach to the correct limb
        # This is where we guarantee side correctness.
        self._create_prosthetic_chain(hip_joint, prosthetic_spec)

    def _create_prosthetic_chain(self, hip_joint_id: str, prosthetic_spec: ProstheticSpec):
        # Build socket, knee, pylon, foot with explicit transforms
        # and attach them to the right hip joint.
        pass

    def apply_pose(self, pose_spec: PoseSpec):
        # Solve joint angles for seated posture in wheelchair, facing camera.
        # Use inverse kinematics with constraints.
        pass


# ---------- Environment & camera ----------

class Environment:
    def __init__(self, pose_spec: PoseSpec):
        self.pose_spec = pose_spec
        self.objects = []
        self._build_environment()

    def _build_environment(self):
        if self.pose_spec.support_device == "wheelchair_sport":
            self.objects.append("sport_wheelchair_model")
        # Add river, path, bench, trees, etc.
        self.objects.append("riverside_path_scene")

class Camera:
    def __init__(self, camera_spec: CameraSpec):
        self.position = camera_spec.position
        self.target = camera_spec.target
        self.fov_deg = camera_spec.fov_deg

    def project(self, model: AnatomicalModel):
        # Project 3D model to 2D image plane.
        # Critically: we can check that the prosthetic (right leg)
        # appears on the left side of the image if requested.
        pass


# ---------- Rendering pipeline ----------

def render_image(body_spec: BodySpec, prosthetic_spec: ProstheticSpec,
                 pose_spec: PoseSpec, camera_spec: CameraSpec):
    # 1. Build anatomical model
    model = AnatomicalModel(body_spec, prosthetic_spec.limb_side)
    model.attach_prosthetic(prosthetic_spec)
    model.apply_pose(pose_spec)

    # 2. Build environment
    env = Environment(pose_spec)

    # 3. Set up camera
    cam = Camera(camera_spec)

    # 4. Project and render
    # Here we would call a renderer (e.g. PyTorch3D, Blender, or a neural renderer)
    # that respects the 3D geometry and constraints.
    image = _render_with_pbr(model, env, cam)

    # 5. Optional: pass image through a diffusion refiner that is NOT allowed
    # to change limb side or prosthetic attachment (only texture, lighting, minor details).
    refined_image = _refine_with_locked_geometry(image)

    return refined_image


def _render_with_pbr(model: AnatomicalModel, env: Environment, cam: Camera):
    """Create a simple placeholder render and return an actual image object."""
    if Image is None or ImageDraw is None:
        raise RuntimeError(
            "Pillow is required to display the generated image. Install it with: pip install pillow"
        )

    width, height = 1200, 800
    image = Image.new("RGB", (width, height), (235, 220, 200))
    draw = ImageDraw.Draw(image)

    # Background sky and ground
    draw.rectangle((0, 0, width, height // 2), fill=(135, 206, 235))
    draw.rectangle((0, height // 2, width, height), fill=(110, 160, 95))

    # Wheelchair
    draw.rectangle((250, 420, 660, 470), fill=(70, 75, 80))
    draw.rectangle((300, 350, 390, 430), fill=(80, 80, 85))
    draw.rectangle((500, 350, 590, 430), fill=(80, 80, 85))
    draw.rectangle((260, 470, 320, 570), fill=(60, 60, 60))
    draw.rectangle((590, 470, 650, 570), fill=(60, 60, 60))

    # Person facing forward
    face_center_x = 600
    draw.ellipse((470, 140, 730, 330), fill=(230, 190, 160))
    draw.ellipse((525, 190, 555, 220), fill=(30, 30, 30))
    draw.ellipse((645, 190, 675, 220), fill=(30, 30, 30))
    draw.line((600, 215, 600, 250), fill=(130, 90, 70), width=4)
    draw.arc((560, 235, 640, 295), 180, 360, fill=(120, 80, 70), width=4)

    # Torso and arms, centered for a forward-facing pose
    draw.rectangle((540, 300, 660, 420), fill=(220, 180, 150))
    draw.rectangle((510, 320, 540, 430), fill=(220, 180, 150))
    draw.rectangle((660, 320, 690, 430), fill=(220, 180, 150))
    draw.rectangle((560, 420, 590, 500), fill=(220, 180, 150))
    draw.rectangle((610, 420, 640, 500), fill=(220, 180, 150))

    # Anatomical mapping: when the figure faces the camera, the person's right leg
    # appears on the viewer's left side of the image, and the left leg appears on the
    # viewer's right side.
    if model.prosthetic_side == "right":
        prosthetic_x = 548    # viewer's left side of the body
        normal_leg_x = 615    # viewer's right side of the body
    else:
        prosthetic_x = 615    # viewer's right side of the body
        normal_leg_x = 548    # viewer's left side of the body

    draw.rectangle((normal_leg_x, 500, normal_leg_x + 35, 610), fill=(220, 180, 150))
    draw.rectangle((normal_leg_x + 5, 610, normal_leg_x + 35, 645), fill=(60, 60, 60))
    draw.ellipse((normal_leg_x, 640, normal_leg_x + 40, 660), fill=(30, 30, 30))

    draw.rectangle((prosthetic_x, 500, prosthetic_x + 40, 610), fill=(80, 120, 180))
    draw.rectangle((prosthetic_x + 10, 610, prosthetic_x + 55, 650), fill=(60, 60, 60))
    draw.ellipse((prosthetic_x + 5, 642, prosthetic_x + 60, 660), fill=(30, 30, 30))

    # River in the background
    draw.ellipse((760, 340, 1060, 520), fill=(60, 140, 180), outline=(30, 90, 130), width=4)

    return image


def _refine_with_locked_geometry(image):
    # Placeholder: a diffusion model that operates in screen space
    # but is constrained by a geometry mask so it cannot move or remove the prosthetic.
    return image


# ---------- End-to-end example ----------

def main():
    side_choice = input("Which leg should the prosthesis be on? (left/right): ").strip().lower()
    while side_choice not in {"left", "right"}:
        print("Please enter 'left' or 'right'.")
        side_choice = input("Which leg should the prosthesis be on? (left/right): ").strip().lower()

    prompt = (
        f"61-year-old fit man with a {side_choice} above-knee prosthesis, "
        "seated in a sporty wheelchair facing the camera."
    )

    body_spec, prosthetic_spec, pose_spec, camera_spec = parse_prompt_to_spec(prompt)
    if prosthetic_spec.limb_side != side_choice:
        prosthetic_spec.limb_side = side_choice

    final_image = render_image(body_spec, prosthetic_spec, pose_spec, camera_spec)

    output_path = Path(__file__).with_name("prosthetic_render.png")
    final_image.save(output_path)

    try:
        final_image.show()
        print(f"Displayed image: {output_path}")
    except Exception:
        if hasattr(__import__("os"), "startfile"):
            __import__("os").startfile(str(output_path))
        print(f"Saved image to: {output_path}")

    return final_image


if __name__ == "__main__":
    main()
