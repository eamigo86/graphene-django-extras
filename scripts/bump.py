#!/usr/bin/env python3

from pathlib import Path
import argparse
import re
import toml


def get_args():
    """Set up CLI args"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--major",
        type=int,
        nargs="*",
        help="Major version bump. Empty flag will auto bump current version.",
    )
    parser.add_argument(
        "--minor",
        type=int,
        nargs="*",
        help="Minor version bump. Empty flag will auto bump current version.",
    )
    parser.add_argument(
        "--patch",
        type=int,
        nargs="*",
        help="Patch version bump. Empty flag will auto bump current version.",
    )
    parser.add_argument(
        "--dry-run", type=str, default="yes", choices=["yes", "no"], help="Dry run"
    )

    return parser.parse_args()


def get_version(pyproject_file_path):
    """Function returns tuple that elements follow semantic versioning order"""
    with open(pyproject_file_path) as file:
        pyproject = toml.loads(file.read())
        current_version = pyproject["tool"]["poetry"]["version"]

    validate_version(current_version)

    # Normalize version to tuple
    if current_version.count(".") == 0:
        return tuple(int(current_version))

    return tuple(int(v) for v in current_version.split("."))


def validate_version(current_version, pattern=r"^\d+\.\d+\.\d+$"):
    """
    Validate that extracted version follows "MAJOR.MINOR.PATCH" pattern
    """
    match = re.search(pattern, current_version)
    if not match:
        print(
            f'Error: Package version {current_version} is not following semantic versioning "MAJOR.MINOR.PATCH"'
        )
        exit(1)


def bump_major(version):
    if not version:
        return CURRENT_VERSION[0] + 1

    return version[0]


def bump_minor(version):
    if not version:
        return CURRENT_VERSION[1] + 1

    return version[0]


def bump_patch(version):
    if not version:
        return CURRENT_VERSION[2] + 1

    return version[0]


def bump_version(major, minor, patch):
    if major or type(major) == list:
        major = bump_major(major)

    if minor or type(minor) == list:
        minor = bump_minor(minor)

    if (type(patch) == list) or all(v is None for v in (major, minor, patch)):
        patch = bump_patch(patch)

    # Construct bump from new version and current version
    bump = []
    new_versions = (major, minor, patch)
    for index in range(len(new_versions)):
        if new_versions[index] is None:
            bump.append(CURRENT_VERSION[index])
        else:
            bump.append(new_versions[index])

    return tuple(bump)


if __name__ == "__main__":
    args = get_args()

    # Obtain 'pyproject.toml' file path
    current_file_path = str(Path(__file__).resolve())
    pyproject_file_path = current_file_path.replace(current_file_path, "pyproject.toml")

    # Bump and normalize current version
    CURRENT_VERSION = get_version(pyproject_file_path)
    NEW_VERSION = bump_version(args.major, args.minor, args.patch)
    CURRENT_VERSION = ".".join(map(str, CURRENT_VERSION))
    NEW_VERSION = ".".join(map(str, NEW_VERSION))

    # Print version check
    if args.dry_run == "yes":
        print(f"Current version: {CURRENT_VERSION}")
        print(f"New version: {NEW_VERSION}")
    else:
        with open(pyproject_file_path, "r") as file:
            content = file.read()

        with open(pyproject_file_path, "w") as file:
            CV = f'version = "{CURRENT_VERSION}"'
            NV = f'version = "{NEW_VERSION}"'
            content = content.replace(CV, NV)
            file.write(content)
            print(
                f"Successfully updated package version from {CURRENT_VERSION} to {NEW_VERSION}"
            )
