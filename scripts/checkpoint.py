"""checkpoint.py — pipeline state persistence, gate enforcement, decision log.

Commands:
  init <slug> [--title T] [--dry-run]
  write <slug> <stage> --status S [--approved] [--artifact name=path]...
        [--unit-done ID]... [--unit NAME] [--total-units N] [--note TEXT] [--cost USD]
  read <slug> [stage]
  next <slug>
  status <slug>
  log-decision <slug> --stage S --category C --subject SUBJ --selected SEL --reason R
        [--option "label::reason"]... [--decided-by user|agent]

Exit codes: 0 ok · 1 usage/validation error · 2 GATE VIOLATION.

Gate rule (binding): a stage with human_approval_default=true in pipeline.yaml cannot be
written status=completed without --approved. There is no override flag on purpose.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import favs_lib as lib  # noqa: E402

ASSET_SUBDIRS = ["characters", "environments", "voices", "storyboards", "clips", "music", "sfx"]


def cmd_init(args) -> int:
    pdir = lib.project_dir(args.slug)
    if (pdir / "project.json").exists():
        print(f"[ERROR] project {args.slug!r} already exists at {pdir}")
        return 1
    manifest = lib.load_manifest()
    for sub in ["artifacts", "history", "gallery", "renders"]:
        (pdir / sub).mkdir(parents=True, exist_ok=True)
    for sub in ASSET_SUBDIRS:
        (pdir / "assets" / sub).mkdir(parents=True, exist_ok=True)
    lib.write_json(pdir / "project.json", {
        "project_id": args.slug,
        "title": args.title or args.slug,
        "pipeline": manifest["name"],
        "created_at": lib.now_iso(),
        "dry_run": bool(args.dry_run),
    })
    lib.write_json(pdir / "decision_log.json", {
        "version": "1.0",
        "project_id": args.slug,
        "decisions": [],
    })
    mode = "DRY-RUN" if args.dry_run else "live"
    print(f"[OK] initialized {mode} project {args.slug!r} at {pdir}")
    print(f"     next stage: {lib.stage_names(manifest)[0]}")
    return 0


def _parse_artifact_args(pairs: list[str]) -> dict[str, str]:
    out = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise SystemExit(f"[ERROR] --artifact expects name=path, got {pair!r}")
        name, path = pair.split("=", 1)
        out[name.strip()] = path.strip().replace("\\", "/")
    return out


def cmd_write(args) -> int:
    pdir = lib.project_dir(args.slug)
    if not (pdir / "project.json").exists():
        print(f"[ERROR] no project {args.slug!r} — run: checkpoint.py init {args.slug}")
        return 1
    manifest = lib.load_manifest()
    try:
        stage = lib.get_stage(args.stage, manifest)
    except KeyError as e:
        print(f"[ERROR] {e}")
        return 1
    if args.status not in lib.CHECKPOINT_STATUSES:
        print(f"[ERROR] status must be one of {lib.CHECKPOINT_STATUSES}")
        return 1

    # 'skipped' is reserved for optional stages, and skipping is a Director ruling.
    if args.status == "skipped":
        if not stage.get("optional"):
            print(f"[ERROR] stage {args.stage!r} is not optional — it cannot be skipped")
            return 1
        if not args.approved:
            print(f"[GATE VIOLATION] skipping optional stage {args.stage!r} requires the Director's explicit decision (--approved).")
            return 2

    # ── GATE ENFORCEMENT (binding — see AGENT_GUIDE.md) ──────────────────────
    if args.status == "completed" and stage["human_approval_default"] and not args.approved:
        print(f"[GATE VIOLATION] stage {args.stage!r} requires Director approval.")
        print("  Write status=awaiting_human, present the artifacts, END YOUR TURN,")
        print("  and only after the Director approves re-run with --status completed --approved.")
        return 2

    previous = lib.read_checkpoint(args.slug, args.stage)
    checkpoint = {
        "version": "1.0",
        "project_id": args.slug,
        "stage": args.stage,
        "status": args.status,
        "timestamp": lib.now_iso(),
        "pipeline": manifest["name"],
        "artifacts": dict((previous or {}).get("artifacts", {})),
        "artifact_hashes": dict((previous or {}).get("artifact_hashes", {})),
        "metadata": dict((previous or {}).get("metadata", {})),
    }
    if args.approved:
        checkpoint["human_approved"] = True
    elif previous and previous.get("human_approved") and args.status == "completed":
        checkpoint["human_approved"] = True

    # Attach + validate artifacts.
    new_artifacts = _parse_artifact_args(args.artifact)
    known = lib.artifact_schema_names()
    for name, rel_path in new_artifacts.items():
        if name not in known:
            print(f"[ERROR] {name!r} is not a known artifact (known: {', '.join(known)})")
            return 1
        if name not in stage["produces"]:
            print(f"[WARN] artifact {name!r} is not in stage {args.stage!r} produces list {stage['produces']}")
        full = pdir / rel_path
        if not full.exists():
            print(f"[ERROR] artifact file not found: {full}")
            return 1
        try:
            instance = lib.read_json(full)
        except json.JSONDecodeError as e:
            print(f"[ERROR] {rel_path} is not valid JSON: {e}")
            return 1
        errors = lib.validation_errors(instance, name)
        if errors:
            print(f"[ERROR] {rel_path} fails {name} schema ({len(errors)} error(s)):")
            for err in errors[:20]:
                print(f"  - {err}")
            return 1
        if instance.get("project_id") != args.slug:
            print(f"[WARN] {rel_path}: project_id {instance.get('project_id')!r} != slug {args.slug!r}")
        checkpoint["artifacts"][name] = rel_path
        checkpoint["artifact_hashes"][name] = lib.sha256_file(full)

    # Partial progress (resume support for long stages).
    if args.unit_done or args.unit or args.total_units is not None:
        pp = checkpoint["metadata"].setdefault("partial_progress", {"completed_unit_ids": []})
        if args.unit:
            pp["unit"] = args.unit
        elif "unit" not in pp and stage.get("resume_unit"):
            pp["unit"] = stage["resume_unit"]
        if args.total_units is not None:
            pp["total_units"] = args.total_units
        for uid in args.unit_done or []:
            if uid not in pp["completed_unit_ids"]:
                pp["completed_unit_ids"].append(uid)
    if args.note:
        checkpoint["metadata"]["note"] = args.note
    if args.cost is not None:
        snap = checkpoint["metadata"].setdefault("cost_snapshot", {})
        snap["stage_cost_usd"] = args.cost

    if not checkpoint["metadata"]:
        del checkpoint["metadata"]
    if not checkpoint["artifacts"]:
        del checkpoint["artifacts"]
        checkpoint.pop("artifact_hashes", None)

    try:
        lib.validate_or_raise(checkpoint, "checkpoint", f"checkpoint_{args.stage}")
    except lib.ValidationFailure as e:
        print(f"[ERROR] {e}")
        for err in e.errors:
            print(f"  - {err}")
        return 1

    # Archive the superseded checkpoint, then write.
    cp_path = lib.checkpoint_path(args.slug, args.stage)
    if cp_path.exists():
        archived = lib.archive_file(args.slug, cp_path)
        print(f"[OK] archived previous checkpoint -> history/{archived.name}")
    lib.write_json(cp_path, checkpoint)
    gate = " (gated)" if stage["human_approval_default"] else ""
    print(f"[OK] checkpoint_{args.stage}.json written: status={args.status}{gate}")
    return 0


def cmd_read(args) -> int:
    if args.stage:
        cp = lib.read_checkpoint(args.slug, args.stage)
        if cp is None:
            print(f"[ERROR] no checkpoint for stage {args.stage!r}")
            return 1
        print(json.dumps(cp, indent=2, ensure_ascii=False))
        return 0
    for name in lib.stage_names():
        cp = lib.read_checkpoint(args.slug, name)
        if cp:
            print(json.dumps(cp, indent=2, ensure_ascii=False))
    return 0


def cmd_next(args) -> int:
    pdir = lib.project_dir(args.slug)
    if not (pdir / "project.json").exists():
        print(f"[ERROR] no project {args.slug!r}")
        return 1
    manifest = lib.load_manifest()
    optional_available = []
    for stage in manifest["stages"]:
        cp = lib.read_checkpoint(args.slug, stage["name"])
        status = cp["status"] if cp else "not_started"
        if status in ("completed", "skipped"):
            continue
        # An untouched optional stage never blocks the pipeline; once entered, it gates like any stage.
        if stage.get("optional") and status == "not_started":
            optional_available.append(stage)
            continue
        print(f"next stage: {stage['name']} [{status}]")
        print(f"  skill: {stage['skill']}")
        if status == "awaiting_human":
            print("  action: present the checkpointed artifacts to the Director; do NOT proceed without approval")
        pp = (cp or {}).get("metadata", {}).get("partial_progress")
        if pp:
            done = len(pp.get("completed_unit_ids", []))
            total = pp.get("total_units", "?")
            print(f"  resume: {done}/{total} {pp.get('unit', 'units')} done -> continue from the next one")
            print(f"  completed: {', '.join(pp.get('completed_unit_ids', [])) or '-'}")
        return 0
    if optional_available:
        names = ", ".join(s["name"] for s in optional_available)
        print(f"pipeline complete: all required stages completed (optional available: {names})")
        for s in optional_available:
            print(f"  optional: {s['name']} — skill: {s['skill']} (Director may run or skip it)")
    else:
        print("pipeline complete: all stages completed")
    return 0


def cmd_status(args) -> int:
    pdir = lib.project_dir(args.slug)
    if not (pdir / "project.json").exists():
        print(f"[ERROR] no project {args.slug!r}")
        return 1
    project = lib.read_json(pdir / "project.json")
    mode = " [DRY-RUN]" if project.get("dry_run") else ""
    print(f"project: {args.slug}{mode} — {project.get('title')}")
    print(f"{'stage':<20} {'status':<16} {'approved':<9} artifacts")
    for name in lib.stage_names():
        cp = lib.read_checkpoint(args.slug, name)
        if not cp:
            print(f"{name:<20} {'not_started':<16} {'-':<9} -")
            continue
        approved = "yes" if cp.get("human_approved") else "-"
        arts = ", ".join(cp.get("artifacts", {}).keys()) or "-"
        print(f"{name:<20} {cp['status']:<16} {approved:<9} {arts}")
    return 0


def cmd_log_decision(args) -> int:
    pdir = lib.project_dir(args.slug)
    log_path = pdir / "decision_log.json"
    if not log_path.exists():
        print(f"[ERROR] no project {args.slug!r}")
        return 1
    log = lib.read_json(log_path)
    options = []
    for raw in args.option or []:
        label, _, reason = raw.partition("::")
        options.append({"label": label.strip(), "reason": reason.strip() or "n/a"})
    entry = {
        "decision_id": f"d-{len(log['decisions']) + 1:03d}",
        "stage": args.stage,
        "category": args.category,
        "subject": args.subject,
        "selected": args.selected,
        "reason": args.reason,
        "decided_by": args.decided_by,
        "timestamp": lib.now_iso(),
    }
    if options:
        entry["options_considered"] = options
    log["decisions"].append(entry)
    try:
        lib.validate_or_raise(log, "decision_log", "decision_log")
    except lib.ValidationFailure as e:
        print(f"[ERROR] {e}")
        for err in e.errors:
            print(f"  - {err}")
        return 1
    lib.write_json(log_path, log)
    print(f"[OK] {entry['decision_id']} logged: [{args.category}] {args.subject} -> {args.selected}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="checkpoint.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init", help="create a production workspace")
    sp.add_argument("slug")
    sp.add_argument("--title")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("write", help="write/refresh a stage checkpoint (validates artifacts, enforces gates)")
    sp.add_argument("slug")
    sp.add_argument("stage")
    sp.add_argument("--status", required=True)
    sp.add_argument("--approved", action="store_true", help="the Director explicitly approved this stage")
    sp.add_argument("--artifact", action="append", metavar="NAME=PATH")
    sp.add_argument("--unit-done", action="append", metavar="ID")
    sp.add_argument("--unit", help="unit label for partial progress (defaults to stage resume_unit)")
    sp.add_argument("--total-units", type=int)
    sp.add_argument("--note")
    sp.add_argument("--cost", type=float, help="stage cost so far, USD")
    sp.set_defaults(func=cmd_write)

    sp = sub.add_parser("read", help="print checkpoint(s)")
    sp.add_argument("slug")
    sp.add_argument("stage", nargs="?")
    sp.set_defaults(func=cmd_read)

    sp = sub.add_parser("next", help="report the next stage to work on + resume info")
    sp.add_argument("slug")
    sp.set_defaults(func=cmd_next)

    sp = sub.add_parser("status", help="stage-by-stage progress table")
    sp.add_argument("slug")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("log-decision", help="append to the decision log")
    sp.add_argument("slug")
    sp.add_argument("--stage", required=True)
    sp.add_argument("--category", required=True)
    sp.add_argument("--subject", required=True)
    sp.add_argument("--selected", required=True)
    sp.add_argument("--reason", required=True)
    sp.add_argument("--option", action="append", metavar='"LABEL::REASON"')
    sp.add_argument("--decided-by", choices=["user", "agent"], default="agent")
    sp.set_defaults(func=cmd_log_decision)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
