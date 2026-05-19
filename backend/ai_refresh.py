"""Claude API integration for intelligent refreshes and data extraction."""
import re
import json
import streamlit as st
import anthropic

_MODEL = "claude-sonnet-4-6"
_SYSTEM = (
    "You are an intelligent assistant for AiPi360, a family command center. "
    "Be concise, practical, and actionable. Focus on what matters most for the family."
)


@st.cache_resource
def _get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY", ""))


def smart_summary(context: str, task: str, max_tokens: int = 512) -> str:
    """Ask Claude to summarise or analyse a context with a given task prompt."""
    client = _get_client()
    resp = client.messages.create(
        model=_MODEL,
        max_tokens=max_tokens,
        system=_SYSTEM,
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nTask: {task}"}],
    )
    return resp.content[0].text


def extract_structured(
    content: str,
    schema: dict,
    file_type: str = "document",
    max_tokens: int = 2048,
) -> dict | list:
    """
    Extract structured data from a file's text content.
    schema: expected JSON shape (used in the prompt).
    Returns parsed dict/list or empty dict on failure.
    """
    client = _get_client()
    prompt = (
        f"Extract structured data from this {file_type}.\n"
        f"Return ONLY valid JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\n"
        f"Content:\n{content}"
    )
    resp = client.messages.create(
        model=_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return {}


def suggest_reminders(section: str, data_summary: str) -> list[dict]:
    """
    Ask Claude to suggest useful reminders for a given section based on current data.
    Returns list of {title, message, suggest_days_before} dicts.
    """
    client = _get_client()
    prompt = (
        f"Section: {section}\nCurrent data summary: {data_summary}\n\n"
        "Suggest 3-5 useful reminders for this section. "
        "Return JSON array: [{\"title\": ..., \"message\": ..., \"suggest_days_before\": ...}]"
    )
    resp = client.messages.create(
        model=_MODEL, max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    m = re.search(r"\[[\s\S]*\]", raw)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return []


def process_upload(file_bytes: bytes, media_type: str, prompt: str) -> str:
    """Send an image (statement screenshot etc.) to Claude vision and return text."""
    import base64
    client = _get_client()
    resp = client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": media_type,
                            "data": base64.standard_b64encode(file_bytes).decode()}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return resp.content[0].text
