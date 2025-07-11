"""Entry point for the teleprompter backend server."""

import argparse

import uvicorn


def main():
    """Run the backend server."""
    parser = argparse.ArgumentParser(description="CueBird Teleprompter Backend Server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--no-container",
        action="store_true",
        help="Skip container configuration (for testing)",
    )

    args = parser.parse_args()

    # Configure container if not skipped
    if not args.no_container:
        try:
            from teleprompter.core.container import configure_container
            configure_container()
        except ImportError:
            print("Warning: Could not configure container (Qt dependencies may be missing)")

    # Run the server
    uvicorn.run(
        "teleprompter.backend.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
