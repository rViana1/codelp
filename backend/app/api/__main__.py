from pathlib import Path

import uvicorn

from app.runtime import create_configured_application

from .application import create_rest_api


def main() -> None:
    runtime = create_configured_application(Path.cwd())
    uvicorn.run(create_rest_api(runtime), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
