from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import app.settings as settings


class SupabaseAuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class SupabaseAuthClient:
    def __init__(self, url: str, anon_key: str):
        self.base_url = url.rstrip("/") + "/"
        self.anon_key = anon_key

    def sign_in_with_password(self, email: str, password: str) -> dict:
        return self._request(
            "auth/v1/token?grant_type=password",
            method="POST",
            body={"email": email, "password": password},
        )

    def sign_up(self, email: str, password: str, username: str) -> dict:
        return self._request(
            "auth/v1/signup",
            method="POST",
            body={
                "email": email,
                "password": password,
                "data": {"username": username},
            },
        )

    def get_user(self, token: str) -> dict:
        return self._request(
            "auth/v1/user",
            method="GET",
            bearer_token=token,
        )

    def _request(
        self,
        path: str,
        method: str,
        body: dict | None = None,
        bearer_token: str | None = None,
    ) -> dict:
        headers = {
            "apikey": self.anon_key,
            "Content-Type": "application/json",
        }
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            urljoin(self.base_url, path),
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=10) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = _extract_error_detail(exc)
            raise SupabaseAuthError(detail, exc.code) from exc
        except URLError as exc:
            raise SupabaseAuthError(f"Supabase Auth unavailable: {exc.reason}", 503) from exc

        return json.loads(response_body) if response_body else {}


def is_supabase_auth_enabled() -> bool:
    return bool(
        settings.SUPABASE_AUTH_ENABLED
        and settings.SUPABASE_URL
        and settings.SUPABASE_ANON_KEY
    )


def get_supabase_auth_client() -> SupabaseAuthClient:
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise SupabaseAuthError("Supabase Auth is not configured", 500)
    return SupabaseAuthClient(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def _extract_error_detail(exc: HTTPError) -> str:
    raw = exc.read().decode("utf-8")
    if not raw:
        return exc.reason
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    return (
        payload.get("msg")
        or payload.get("message")
        or payload.get("error_description")
        or payload.get("error")
        or exc.reason
    )
