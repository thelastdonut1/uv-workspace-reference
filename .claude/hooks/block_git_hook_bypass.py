"""
PreToolUse hook: deny shell commands that bypass git pre-commit hooks.

Reads the tool-call JSON from stdin. If the command tries to skip or disable
git hooks, prints a "deny" permission decision; otherwise stays silent.
Errs on the side of blocking: a rare false positive costs a rephrased
command, a false negative defeats the policy in CLAUDE.md (Git Hygiene).
"""

import json
import re
import sys

BYPASS_PATTERNS: list[tuple[str, str]] = [
    (
        r"(?s)\bgit\b.*--no-verify",
        "git --no-verify skips pre-commit/pre-push hooks",
    ),
    (
        r"(?s)\bgit\b.*\bcommit\b.*(^|\s)-[a-zA-Z]*n[a-zA-Z]*\b",
        "git commit -n (bundled or bare) is shorthand for --no-verify",
    ),
    (
        r"(?i)core\.hookspath",
        "overriding core.hooksPath disables the installed hooks",
    ),
    (
        r"\.git[/\\]hooks",
        "modifying .git/hooks directly can remove or neuter the hook shim",
    ),
    (
        r"\b(prek|pre-commit)\s+uninstall\b",
        "uninstalling the hook manager deactivates the hooks",
    ),
]

DENY_MESSAGE = (
    "Blocked by .claude/hooks/block_git_hook_bypass.py: {reason}. "
    "CLAUDE.md (Git Hygiene) forbids bypassing pre-commit hooks - fix the "
    "underlying issue instead. If this is a false positive, rephrase the "
    "command to avoid the flagged pattern."
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return  # malformed input: don't break unrelated tool calls

    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str) or not command:
        return

    for pattern, reason in BYPASS_PATTERNS:
        if re.search(pattern, command):
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": DENY_MESSAGE.format(reason=reason),
                        }
                    }
                )
            )
            return


if __name__ == "__main__":
    main()
