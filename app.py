# Deployed by:
# uvicorn app:app --reload --host 0.0.0.0 --port 9001

from __future__ import annotations

from pathlib import Path
import json

from fastapi import FastAPI, Request, Form  # type: ignore
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

from common import get_logger, LoggingMiddleware, generate_random_id


HERE = Path(__file__).parent
log_file_path = HERE / "app.log"
logger = get_logger(__file__, log_file_path)

app = FastAPI()
app.add_middleware(LoggingMiddleware, log=logger.info)

templates = Jinja2Templates(directory="templates", trim_blocks=True, lstrip_blocks=True)

CORRECT_PIN_0 = "0432"
CORRECT_PIN_1 = "0234"
CORRECT_PIN_2 = "0123"
CORRECT_PIN_3 = "0124"

TOKEN_DB_FILE = HERE / "token_db.json"
TOKEN_SESSION_DB_FILE = HERE / "token_session_db.json"

############################ LEVEL 0 ##########################################


@app.get("/")
def main():
    return RedirectResponse(url="/level0")


@app.get("/level0")
async def level_0_get_for_everything(request: Request):
    pin = request.query_params.get("pin", None)
    logger.info(f"GET level0 pin: {pin}")

    if pin == CORRECT_PIN_0:
        return templates.TemplateResponse(
            "success.html",
            {
                "request": request,
                "level": "level 0",
                "next_level": "level1",
                "method": "get",
                "token": None,
            },
        )
    else:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "level": 0, "invalid_pin": pin is not None},
        )


############################ LEVEL 1 ##########################################


def level1_send_index(request: Request, invalid_pin: bool):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "level": 1,
            "invalid_pin": invalid_pin,
            "method": "post",
            "token": None,
        },
    )


@app.get("/level1")
async def level1_get(request: Request):
    return level1_send_index(request, False)


@app.post("/level1")
async def level1_post(request: Request, pin: str = Form(...)):
    logger.info(f"POST level1 pin: {pin}")

    if pin == CORRECT_PIN_1:
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "level": "level 1", "next_level": "level2"},
        )
    else:
        return level1_send_index(request, True)


############################ LEVEL 2 ##########################################


def get_token_db() -> set[str]:
    if not TOKEN_DB_FILE.exists():
        return set()
    with open(TOKEN_DB_FILE, "r") as f:
        return set(json.load(f)["tokens"])


def save_token_db(data: set[str]):
    with open(TOKEN_DB_FILE, "w") as f:
        json.dump({"tokens": list(data)}, f)


def save_new_token(token: str):
    data = get_token_db()
    data.add(token)
    save_token_db(data)


def is_token_valid(token: str) -> bool:
    data = get_token_db()
    return token in data


def delete_token(token: str):
    data = get_token_db()
    if token in data:
        data.remove(token)
    save_token_db(data)


def level2_send_index(request: Request, invalid_pin: bool):
    token = generate_random_id(bytes=10)
    save_new_token(token)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "level": 2,
            "invalid_pin": invalid_pin,
            "method": "post",
            "token": token,
        },
    )


@app.get("/level2")
async def level2_get(request: Request):
    return level2_send_index(request, False)


@app.post("/level2")
async def level2_post_with_token(
    request: Request, pin: str = Form(...), token: str = Form(...)
):
    print("pin", pin)
    logger.info(f"POST level2 pin: {pin}, token: {token}")

    valid_token = is_token_valid(token)
    if valid_token:
        delete_token(token)

    if pin == CORRECT_PIN_2 and valid_token:
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "level": "level 2", "next_level": "level3"},
        )
    else:
        return level2_send_index(request, True)


############################ LEVEL 3 ##########################################


def get_token_session_db() -> dict[str, str]:
    if not TOKEN_SESSION_DB_FILE.exists():
        return {}
    with open(TOKEN_SESSION_DB_FILE, "r") as f:
        return json.load(f)


def save_token_session_db(data: dict[str, str]):
    with open(TOKEN_SESSION_DB_FILE, "w") as f:
        json.dump(data, f)


def save_new_token_session(token: str, session: str):
    data = get_token_session_db()
    data[session] = token
    save_token_session_db(data)


def is_token_session_valid(token: str, session: str) -> bool:
    data = get_token_session_db()
    if session not in data:
        return False
    return data[session] == token


def delete_token_session(session: str):
    data = get_token_session_db()
    del data[session]
    save_token_session_db(data)


def level3_send_index(request: Request, invalid_pin: bool):
    token = generate_random_id(bytes=10)

    session_id = request.cookies.get("session_id")
    if session_id is None or len(session_id) != 20:
        session_id = generate_random_id(bytes=10)

    save_new_token_session(token, session_id)

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "level": 3,
            "invalid_pin": invalid_pin,
            "method": "post",
            "token": token,
        },
    )

    response.set_cookie("session_id", session_id)

    return response


@app.get("/level3")
async def level3_get(request: Request):
    return level3_send_index(request, False)


@app.post("/level3")
async def level3_post_with_token(
    request: Request, pin: str = Form(...), token: str = Form(...)
):
    print("pin", pin)
    logger.info(f"POST level3 pin: {pin}, token: {token}")

    session_id = request.cookies.get("session_id")

    valid_token = session_id is not None and is_token_session_valid(token, session_id)
    if valid_token:
        assert session_id is not None
        delete_token_session(session_id)

    if pin == CORRECT_PIN_3 and valid_token:
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "level": "level 3", "next_level": None},
        )
    else:
        return level3_send_index(request, True)
