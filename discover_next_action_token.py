"""
I admit, I used Claude for this.
Pls don't judge me, I hate regex, UwU
"""
import re
from typing import Optional
from urllib.parse import urljoin
import requests


def _extract_chunk_urls(html: str, base_url: str) -> list[str]:
    """Pull every /_next/static/... .js script src out of the page HTML."""
    urls = re.findall(r'src="(/_next/static/[^"]+\.js)"', html)
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(urljoin(base_url, u))
    return out


def _find_action_id(js_text: str, action_name: str) -> Optional[str]:
    """
    Look for createServerReference("<id>", ..., "<action_name>").
    The hex id and the trailing debug name are string literals, so they
    survive minification even though variable names (eo, ei, ...) don't.
    """
    pattern = re.compile(
        r'createServerReference\)?\("([0-9a-f]+)"[^)]*?"' + re.escape(action_name) + r'"\)'
    )
    m = pattern.search(js_text)
    return m.group(1) if m else None


def discover_action_id(session: requests.Session, page_url: str = "https://moj.easistent.com/timetable", action_name: str = "getWeekTimetable") -> str:
    """Fetch the page, walk its JS chunks, return the action's current id."""
    page = session.get(page_url)
    page.raise_for_status()

    for chunk_url in _extract_chunk_urls(page.text, page_url):
        js = session.get(chunk_url)
        if js.status_code != 200:
            continue
        action_id = _find_action_id(js.text, action_name)
        if action_id:
            return action_id

    raise RuntimeError(f"could not locate action id for {action_name!r} on {page_url}")
