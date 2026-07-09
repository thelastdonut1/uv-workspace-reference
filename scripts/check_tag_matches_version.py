"""
Pre-push guard: a release tag on HEAD must match every pyproject version.

Runs as a prek pre-push hook. If HEAD carries a tag like v1.2.3, every
pyproject.toml in the workspace (root and members) must declare that same
version; otherwise the push is rejected. No release tag on HEAD means
nothing to check.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

TAG_PATTERN = re.compile(r"v(\d+\.\d+\.\d+)")


def release_versions_at_head() -> set[str]:
    result = subprocess.run(
        ["git", "tag", "--points-at", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    versions = set()
    for tag in result.stdout.split():
        match = TAG_PATTERN.fullmatch(tag)
        if match:
            versions.add(match.group(1))
    return versions


def pyproject_versions() -> dict[Path, str]:
    paths = [Path("pyproject.toml"), *sorted(Path("packages").glob("*/pyproject.toml"))]
    versions = {}
    for path in paths:
        with path.open("rb") as f:
            data = tomllib.load(f)
        versions[path] = data["project"]["version"]
    return versions


def main() -> int:
    tagged = release_versions_at_head()
    if not tagged:
        return 0
    if len(tagged) > 1:
        print(f"Multiple release tags on HEAD disagree: {sorted(tagged)}", file=sys.stderr)
        return 1

    expected = tagged.pop()
    mismatches = {path: version for path, version in pyproject_versions().items() if version != expected}
    if not mismatches:
        return 0

    print(f"HEAD is tagged v{expected}, but these pyproject versions disagree:", file=sys.stderr)
    for path, version in mismatches.items():
        print(f"  {path}: {version}", file=sys.stderr)
    print(
        "Bump the versions (uv version --bump ... per package) or retag, then push again.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
