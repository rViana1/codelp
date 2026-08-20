from pathlib import Path

from app.runtime import create_configured_application

from .transport import CodelpMCPTransport


def main() -> None:
    application = create_configured_application(Path.cwd(), interface="mcp")
    CodelpMCPTransport(application).run_stdio()


if __name__ == "__main__":
    main()
