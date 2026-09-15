from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from poc.synapse import ContinuityKernel


def _object(value: str) -> dict[str, Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("expected a JSON object")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project Synapse v0.1 PoC")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create a Lineage state file")
    init.add_argument("path", type=Path)
    init.add_argument("--lineage", required=True)
    init.add_argument("--root", default="operator")

    for name in ("status", "verify"):
        command = commands.add_parser(name)
        command.add_argument("path", type=Path)

    grant = commands.add_parser("grant", help="grant one capability")
    grant.add_argument("path", type=Path)
    grant.add_argument("--actor", default="operator")
    grant.add_argument("--operation", required=True)
    grant.add_argument("--to", required=True)

    propose = commands.add_parser("propose", help="commit a domain event")
    propose.add_argument("path", type=Path)
    propose.add_argument("--actor", required=True)
    propose.add_argument("--type", required=True)
    propose.add_argument("--payload", required=True, type=_object)

    transition = commands.add_parser("transition", help="create a checkpoint")
    transition.add_argument("path", type=Path)
    transition.add_argument("--actor", default="operator")
    transition.add_argument("--state", required=True, type=_object)
    transition.add_argument("--accounting", required=True, type=_object)
    transition.add_argument("--from-checkpoint")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "init":
        if args.path.exists():
            raise SystemExit(f"state file already exists: {args.path}")
        kernel = ContinuityKernel(args.lineage, args.root)
        kernel.save(args.path)
        result = {"lineage": kernel.lineage_id, "checkpoint": kernel.current_checkpoint}
    elif args.command == "verify":
        ContinuityKernel.verify_export(args.path.read_text(encoding="utf-8"))
        result = {"verified": True}
    else:
        kernel = ContinuityKernel.load(args.path)
        if args.command == "status":
            result = {
                "lineage": kernel.lineage_id,
                "status": kernel.status,
                "checkpoint": kernel.current_checkpoint,
                "records": len(kernel.records),
            }
        elif args.command == "grant":
            record_id = kernel.grant(args.actor, args.operation, args.to)
            if not record_id:
                raise SystemExit("grant denied")
            kernel.save(args.path)
            result = {"grant": record_id}
        elif args.command == "propose":
            record_id = kernel.record_domain_event(args.actor, args.type, args.payload)
            if not record_id:
                raise SystemExit("proposal denied")
            kernel.save(args.path)
            result = {"event": record_id}
        else:
            previous = args.from_checkpoint or kernel.current_checkpoint
            status, checkpoint = kernel.transition(
                args.actor, previous, args.state, args.accounting
            )
            if checkpoint:
                kernel.save(args.path)
            result = {"status": status, "checkpoint": checkpoint}

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
