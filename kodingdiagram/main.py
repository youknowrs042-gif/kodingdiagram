"""KodingDiagram — main entry point and CLI."""

from __future__ import annotations

import argparse
import sys


def cli():
    """CLI entry point for KodingDiagram."""
    parser = argparse.ArgumentParser(
        prog="kodingdiagram",
        description="KodingDiagram — Qualitative Data Analysis Toolkit",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind the server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server (default: 8000)"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required. Install with: pip install uvicorn[standard]")
        sys.exit(1)

    print(f"Starting KodingDiagram API server on {args.host}:{args.port}")
    print(f"Docs available at http://{args.host}:{args.port}/docs")

    uvicorn.run(
        "kodingdiagram.api.app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True,
    )


# Allow `python -m kodingdiagram`
if __name__ == "__main__":
    cli()
