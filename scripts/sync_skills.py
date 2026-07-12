"""sync_skills.py — mirror skills/tech/* into .claude/skills/* (Windows-safe copy, no symlinks).

Usage:
  python scripts/sync_skills.py           # copy skills/tech/<name>/ -> .claude/skills/<name>/
  python scripts/sync_skills.py --check   # exit 1 if .claude/skills is out of sync (CI/test mode)

skills/tech/ is the canonical location (read by all harnesses via Rule Zero);
.claude/skills/ exists so Claude Code auto-discovers the same skills. Never edit
.claude/skills directly — edit skills/tech and re-run this script.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "skills" / "tech"
DST = ROOT / ".claude" / "skills"


def pairs():
    for src_dir in sorted(p for p in SRC.iterdir() if p.is_dir()):
        yield src_dir, DST / src_dir.name


def out_of_sync() -> list[str]:
    problems = []
    src_names = {p.name for p in SRC.iterdir() if p.is_dir()} if SRC.exists() else set()
    dst_names = {p.name for p in DST.iterdir() if p.is_dir()} if DST.exists() else set()
    for name in sorted(src_names - dst_names):
        problems.append(f"missing in .claude/skills: {name}")
    for name in sorted(dst_names - src_names):
        problems.append(f"orphan in .claude/skills (no skills/tech source): {name}")
    for src_dir, dst_dir in pairs():
        if not dst_dir.exists():
            continue
        for src_file in src_dir.rglob("*"):
            if not src_file.is_file():
                continue
            rel = src_file.relative_to(src_dir)
            dst_file = dst_dir / rel
            if not dst_file.exists():
                problems.append(f"missing file: .claude/skills/{src_dir.name}/{rel}")
            elif not filecmp.cmp(src_file, dst_file, shallow=False):
                problems.append(f"differs: .claude/skills/{src_dir.name}/{rel}")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify parity, change nothing")
    args = parser.parse_args(argv)

    if not SRC.exists():
        print(f"[OK] nothing to sync ({SRC} does not exist yet)")
        return 0

    if args.check:
        problems = out_of_sync()
        if problems:
            print(f"[OUT OF SYNC] {len(problems)} problem(s) — run: python scripts/sync_skills.py")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("[OK] .claude/skills matches skills/tech")
        return 0

    DST.mkdir(parents=True, exist_ok=True)
    synced = 0
    for src_dir, dst_dir in pairs():
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        synced += 1
    # Remove orphans so deletions propagate too.
    src_names = {p.name for p in SRC.iterdir() if p.is_dir()}
    for dst_dir in DST.iterdir():
        if dst_dir.is_dir() and dst_dir.name not in src_names:
            shutil.rmtree(dst_dir)
            print(f"[OK] removed orphan {dst_dir.name}")
    print(f"[OK] synced {synced} skill(s) -> .claude/skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
