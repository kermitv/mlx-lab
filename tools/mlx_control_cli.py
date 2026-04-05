"""Minimal repo-local CLI for read-only ``mlx_control`` status inspection."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from mlx_control import MLXController

from tools.integrations.mlx_control import (
    build_status_view,
    load_controller_from_repo_local_context,
    render_status_view,
)
from tools.integrations.opencode_mlx_control import (
    build_opencode_status_view,
    render_opencode_readiness,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the minimal parser for the approved Phase 3A command surface."""

    parser = argparse.ArgumentParser(prog="mlx-control")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument(
        "--connectivity-path",
        type=Path,
        default=None,
        help="optional path to a repo-local local-connectivity.json artifact",
    )
    return parser


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    controller: Optional[MLXController] = None,
) -> int:
    """Run the CLI for the approved read-only command set."""

    args = build_parser().parse_args(argv)
    active_controller = controller or load_controller_from_repo_local_context(
        connectivity_path=args.connectivity_path,
    )

    if args.command == "status":
        status_view = build_status_view(active_controller)
        opencode_view = build_opencode_status_view(active_controller)
        output = render_status_view(status_view)
        output += render_opencode_readiness(opencode_view) + "\n"
        print(output, end="")
        return 0

    raise ValueError("unsupported command %s" % args.command)


if __name__ == "__main__":
    raise SystemExit(main())
