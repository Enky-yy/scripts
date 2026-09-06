from pathlib import Path
import re
import sys


INPUT_FILE = Path("requirements.txt")
OUTPUT_FILE = Path("requirements_cleaned.txt")


# Lines containing paths created by Conda builds, e.g.
# /home/task_xxx/conda-bld/package_xxx/work
CONDA_BUILD_PATTERNS = [
    r"/conda-bld/",
    r"/home/task_[^/\s]*/",
    r"[/\\]work\s*$",
]


def is_conda_build_path(line: str) -> bool:
    """Return True if the line looks like a temporary Conda build path."""
    return any(re.search(pattern, line) for pattern in CONDA_BUILD_PATTERNS)


def clean_line(line: str):
    """
    Clean one requirements.txt line.

    Returns:
        cleaned line, or None if the line should be removed.
    """
    stripped = line.strip()

    # Keep blank lines and comments
    if not stripped or stripped.startswith("#"):
        return line.rstrip()

    # Remove temporary Conda build paths
    if is_conda_build_path(stripped):
        print(f"REMOVED: {stripped}")
        return None

    return stripped


def main():
    if not INPUT_FILE.exists():
        print(f"ERROR: {INPUT_FILE} not found.")
        print(f"Run this script from the directory containing {INPUT_FILE}.")
        sys.exit(1)

    lines = INPUT_FILE.read_text(encoding="utf-8").splitlines()

    cleaned = []
    removed = 0

    for line in lines:
        result = clean_line(line)

        if result is None:
            removed += 1
        else:
            cleaned.append(result)

    # Remove duplicate package entries while preserving order
    seen = set()
    unique = []

    for line in cleaned:
        if not line or line.startswith("#"):
            unique.append(line)
            continue

        # Normalize package name for duplicate detection.
        # Examples:
        #   numpy==2.0.0
        #   numpy>=1.0
        #   numpy
        match = re.match(r"^([A-Za-z0-9_.-]+)", line)

        if match:
            package = match.group(1).lower().replace("_", "-")

            if package in seen:
                print(f"DUPLICATE REMOVED: {line}")
                continue

            seen.add(package)

        unique.append(line)

    OUTPUT_FILE.write_text(
        "\n".join(unique) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("Cleaning complete")
    print("=" * 60)
    print(f"Input :  {INPUT_FILE}")
    print(f"Output:  {OUTPUT_FILE}")
    print(f"Removed Conda paths: {removed}")
    print(f"Original lines: {len(lines)}")
    print(f"Final lines: {len(unique)}")
    print()
    print("Next:")
    print(f"    python -m pip install -r {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
