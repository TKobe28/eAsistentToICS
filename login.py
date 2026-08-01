import requests
import parse_timetable
from types import FunctionType
from copy import copy
from exceptions import *
from config import get_config


class AuthSession(requests.Session):
    def __init__(self, username: str, password: str, login: bool = True):
        super().__init__()
        self.username = username
        self.password = password

        # todo: add proxies 

        if login:
            self.login()

    def __repr__(self) -> str:
        return f"AuthSession(username={self.username}, session_key={self.cookies.get('ses')})"

    @property
    def logged_in(self) -> bool:
        return self.cookies.get("ses") is not None

    def login(self):
        r = self.post(
            "https://www.easistent.com/p/ajax_prijava",
            files={
                "uporabnik": (None, self.username),
                "geslo": (None, self.password),
                "pin": (None, ""),
                "koda": (None, ""),
                "force_sms": (None, "0"),
            },
        )
        data = r.json()
        if data["status"] != "ok":
            raise LoginError(data)
        if data["data"]["require_captcha"]:
            raise CaptchaRequired()

        r = self.get("https://www.easistent.com/", allow_redirects=False)
        while r.is_redirect:
            r = self.get(r.headers["Location"], allow_redirects=False)
            if "ses" in self.cookies:
                print(f"Logged in user {self.username}. ")
                return
        raise LoginError("Authentication completed but no session cookie was issued.")

    def login_required(func: FunctionType, tries=2):  # noqa
        def inner(self: "AuthSession", *args, **kwargs):
            if self.cookies.get("ses") is None:
                self.login()
            maybe_exception = Exception()
            for i in range(tries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    maybe_exception = copy(e)
                    print(f"Failed running {func.__name__} for user {self.username}: {e}. {'Retrying login.' if i + 1 < tries else 'Not retrying anymore.'}")
            raise maybe_exception
        return inner

    @login_required
    def fetch_week(self, _date: str, verbose: bool = False) -> dict:
        """
        :param _date: must be in YYYY-MM-DD format!
        :param verbose
        :return:
        """
        if not self.cookies.get("ses"):
            self.login()

        payload = f'["{_date}"]'

        response = self.post(
            "https://moj.easistent.com/timetable",
            data=payload,
            headers={
                "next-action": "40c2ee8acc4d66a17c62baed77a8fac56e2b2e0074"
            }
        )

        print(response.content.decode())
        print(response.status_code, response.reason)
        response.raise_for_status()

        return parse_timetable.parse_raw(response.content.decode())


if __name__ == "__main__":
    config = get_config()
    print(AuthSession(config.users[0].username, config.users[0].password, login=True))
