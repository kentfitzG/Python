#!/usr/bin/env python3
"""Find files larger than a configurable size and print their full paths."""

import argparse
from datetime import datetime
import os
from pathlib import Path


def find_large_files(root: str, minimum_bytes: int) -> tuple[list[tuple[int, str]], list[str]]:
    matches = []
    warnings = []

    def report_walk_error(error: OSError) -> None:
        warnings.append(f"Skipping {error.filename}: {error.strerror}")

    for directory, _, filenames in os.walk(root, onerror=report_walk_error):
        for filename in filenames:
            path = os.path.join(directory, filename)
            try:
                size = os.stat(path, follow_symlinks=False).st_size
            except OSError as error:
                warnings.append(f"Skipping {path}: {error.strerror}")
                continue

            if size > minimum_bytes:
                matches.append((size, os.path.abspath(path)))

    return sorted(matches, reverse=True), warnings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find files larger than a size threshold and print their full paths."
    )
    parser.add_argument(
        "--root",
        default="/",
        help="directory to scan (default: /, the whole filesystem)",
    )
    parser.add_argument(
        "--min-gb",
        type=float,
        default=1.0,
        help="minimum file size in decimal gigabytes (default: 1.0 GB)",
    )
    args = parser.parse_args()

    if args.min_gb < 0:
        parser.error("--min-gb must be zero or greater")

    root = os.path.abspath(os.path.expanduser(args.root))
    if not os.path.isdir(root):
        parser.error(f"scan root is not a directory: {root}")

    minimum_bytes = int(args.min_gb * 1_000_000_000)
    output_path = Path.home() / "Desktop" / "big.txt"
    print(f"Scanning {root} for files larger than {args.min_gb:g} GB...")
    matches, warnings = find_large_files(root, minimum_bytes)

    with output_path.open("w", encoding="utf-8") as report:
        report.write(f"Large file scan report: {datetime.now().astimezone().isoformat()}\n")
        report.write(f"Scanned directory: {root}\n")
        report.write(f"Minimum size: {args.min_gb:g} GB ({minimum_bytes} bytes)\n\n")

        report.write("Matching files:\n")
        if matches:
            for size, path in matches:
                report.write(f"{size / 1_000_000_000:.2f} GB\t{path}\n")
        else:
            report.write("No matching files found.\n")

        report.write(f"\nFound {len(matches)} file(s).\n")
        report.write(f"Skipped paths: {len(warnings)}\n")
        if warnings:
            report.write("\nWarnings:\n")
            for warning in warnings:
                report.write(f"{warning}\n")

    print(f"Found {len(matches)} file(s). Report saved to {output_path}")


if __name__ == "__main__":
    main()
