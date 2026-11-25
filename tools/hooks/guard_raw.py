#!/usr/bin/env python3
"""Claude Code PreToolUse hook: keep projects/<p>/raw/ source footage read-only.

Wired in .claude/settings.json for Bash, Write, Edit and NotebookEdit. Reads
the hook payload on stdin and prints a permission decision:

  deny  - deleting, moving/renaming, truncating, in-place editing, or
          redirecting/ffmpeg-writing into raw/; `git clean -x/-X` (raw/ is
          gitignored, so it would be wiped); rm of a folder that contains a
          raw/ dir; Write/Edit of any file under raw/.
  ask   - copying NEW footage into raw/ (cp/rsync/ditto/mv-into/ln/touch/
          chmod), so ingest still works but you confirm each time.
  (none)- everything else, including reading raw/ (ffmpeg -i, probe, tools).

The python tools in tools/ also refuse raw/ output paths themselves
(_media.assert_not_raw), so this hook only has to cover the shell.

Test:  echo '{"tool_name":"Bash","tool_input":{"command":"rm projects/x/raw/a.mp4"}}' | python3 tools/hooks/guard_raw.py
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

RAW_RE = re.compile(r"(^|/)raw(/|$)")
SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")", "|&"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", "1>", "2>", "1>>", "2>>"}
DESTRUCTIVE = {"rm", "rmdir", "unlink", "shred", "srm", "truncate", "trash"}
COPY_LIKE = {"cp", "ditto", "rsync", "scp", "ln", "install", "gcp"}
META_CHANGE = {"touch", "chmod", "chown", "chflags", "xattr", "setfile", "SetFile"}
IN_PLACE = {"sed", "gsed", "perl"}
WRAPPERS = {"sudo", "command", "nice", "nohup", "time", "env", "xargs", "exec"}


def decide(decision: str, reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": f"raw/ guard: {reason}",
    }}))
    sys.exit(0)


def is_raw(tok: str, raw_cwd: bool) -> bool:
    if RAW_RE.search(tok):
        return True
    # relative path while cd'd into a raw/ folder earlier in the same command
    return raw_cwd and not tok.startswith(("-", "/", "~")) and tok not in ("", ".")


def contains_raw_dir(tok: str, cwd: Path) -> bool:
    """rm -rf projects/<p> (or projects/) would take raw/ with it."""
    p = Path(os.path.expanduser(tok))
    p = p if p.is_absolute() else cwd / p
    try:
        if not p.is_dir():
            return False
        return (p / "raw").is_dir() or any(p.glob("*/raw")) or any(p.glob("projects/*/raw"))
    except OSError:
        return False


def tokenize(cmd: str) -> list[str]:
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>")
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:  # unbalanced quotes: fall back to a crude split
        return cmd.split()


def segments(tokens: list[str]):
    """Yield (argv, redirect_targets) per simple command."""
    argv, redirs, i = [], [], 0
    while i < len(tokens):
        t = tokens[i]
        if t in SEPARATORS:
            if argv or redirs:
                yield argv, redirs
            argv, redirs = [], []
        elif t in REDIRECTS or (t.endswith(">") and t.rstrip(">").isdigit()):
            if i + 1 < len(tokens):
                redirs.append(tokens[i + 1])
                i += 1
        elif t in ("<", "<<", "<<<"):
            i += 1  # skip input redirect source
        else:
            argv.append(t)
        i += 1
    if argv or redirs:
        yield argv, redirs


def check_bash(cmd: str, cwd: Path) -> None:
    tokens = tokenize(cmd)
    raw_cwd = False
    for argv, redirs in segments(tokens):
        while argv and (argv[0] in WRAPPERS or re.match(r"^[A-Za-z_]+=", argv[0])):
            argv = argv[1:]
        name = os.path.basename(argv[0]) if argv else ""
        args = argv[1:]

        if name == "git" and args and args[0] == "clean" and any(
                a.startswith("-") and not a.startswith("--") and ("x" in a or "X" in a) for a in args[1:]):
            decide("deny", "`git clean -x/-X` deletes gitignored files, which includes every projects/*/raw/ folder.")

        if name == "cd":
            raw_cwd = bool(args) and is_raw(args[0], False)
            continue

        for r in redirs:
            if is_raw(r, raw_cwd) and r != "/dev/null":
                decide("deny", f"redirecting output into raw/ ({r}) would overwrite source footage.")

        raw_args = [a for a in args if not a.startswith("-") and is_raw(a, raw_cwd)]

        if name in DESTRUCTIVE:
            if raw_args:
                decide("deny", f"`{name}` on raw/ source footage ({raw_args[0]}). raw/ is read-only.")
            big = [a for a in args if not a.startswith("-") and contains_raw_dir(a, cwd)]
            if big:
                decide("deny", f"`{name} {big[0]}` would delete a folder containing raw/ footage.")
            continue

        if not raw_args:
            continue
        positional = [a for a in args if not a.startswith("-")]

        if name == "mv":
            if any(is_raw(a, raw_cwd) for a in positional[:-1]):
                decide("deny", "moving or renaming files out of raw/ is not allowed; copy them instead.")
            decide("ask", f"this moves new footage into raw/ ({positional[-1]}). Confirm nothing there gets overwritten.")
        if name in COPY_LIKE:
            if name == "rsync" and any(a.startswith("--delete") or a.startswith("--remove-source") for a in args):
                decide("deny", "rsync --delete/--remove-source-files touching raw/.")
            if positional and is_raw(positional[-1], raw_cwd):
                decide("ask", f"`{name}` writes into raw/ ({positional[-1]}). OK for ingesting new footage; confirm it won't overwrite an original.")
            continue
        if name in IN_PLACE and any(a.startswith("-i") or a == "--in-place" or a.startswith("-pi") for a in args):
            decide("deny", f"in-place edit of a file in raw/ ({raw_args[0]}).")
        if name == "tee":
            decide("deny", f"tee writes into raw/ ({raw_args[0]}).")
        if name == "find" and ("-delete" in args or any(a in ("rm", "mv", "unlink") for a in args)):
            decide("deny", "find with -delete / -exec rm|mv over raw/.")
        if name in ("ffmpeg", "magick", "convert", "exiftool", "exiv2", "sips", "SetFile") and positional:
            if name == "ffmpeg" and is_raw(args[-1], raw_cwd):
                decide("deny", f"ffmpeg output path is inside raw/ ({args[-1]}). Write to edit/ or exports/.")
            if name in ("exiftool", "exiv2", "sips") or (name in ("magick", "convert") and is_raw(args[-1], raw_cwd)):
                decide("deny", f"`{name}` would modify files in raw/ ({raw_args[0]}).")
        if name in META_CHANGE:
            decide("ask", f"`{name}` changes files in raw/ ({raw_args[0]}).")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or os.getcwd())
    if tool == "Bash":
        cmd = inp.get("command") or ""
        if "raw" in cmd or "git" in cmd or "rm" in cmd:
            check_bash(cmd, cwd)
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        if RAW_RE.search(path) and "/projects/" in "/" + str(Path(path)):
            decide("deny", f"{tool} of {path}: raw/ source footage is read-only.")
    sys.exit(0)


if __name__ == "__main__":
    main()
