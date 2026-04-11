#!/usr/bin/env python3
from __future__ import annotations
import os
import logging
import uvicorn
import app.settings


def main():
    uvicorn.run(
        "app:asgi_app",
        host=app.settings.SERVER_HOST,
        port=app.settings.SERVER_PORT,
        log_level=logging.WARNING,
        workers=4,
        reload=app.settings.DEBUG,
    )

    return 0


if __name__ == "__main__":
    os._exit(main())
