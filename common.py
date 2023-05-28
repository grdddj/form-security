from __future__ import annotations

import logging
import secrets
import time
from pathlib import Path
from typing import Any, Callable

from fastapi import Request  # type: ignore
from starlette.types import ASGIApp, Receive, Scope, Send


def get_logger(name: str, log_file_path: str | Path) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    log_handler = logging.FileHandler(log_file_path)
    log_formatter = logging.Formatter("%(asctime)s %(message)s")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    return logger


def get_client_ip(request: Request) -> str:
    if request.client is None:
        return "ghost"
    return request.client.host


def generate_random_id(bytes: int = 5):
    return secrets.token_hex(bytes)


class LoggingMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        log: Callable[[str], None],
    ) -> None:
        self.app = app
        self.log = log

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        start_time = time.time()

        request_id = generate_random_id()
        default = "unknown"
        path = scope.get("path", default)
        port = scope.get("server", ["", ""])[1]
        method = scope.get("method", default)
        query = scope.get("query_string", b"default").decode("utf-8")
        ip = scope.get("client", [default])[0]
        self.log(
            f"req_id: {request_id}, HOST: {ip}, path: {method} {path}, port: {port}, query: {query}"
        )

        await self.app(scope, receive, send)

        process_time = round(time.time() - start_time, 3)
        self.log(f"req_id: {request_id}: request finished in {process_time} s")
