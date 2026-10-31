import re

HASHTAG_RE = re.compile(r"\B#(\w+)")
MENTION_RE = re.compile(r"\B@(\w+)")


def _unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def tags(text: str) -> dict[str, list[str]]:
    hashtags = [h.lower() for h in HASHTAG_RE.findall(text)]
    mentions = MENTION_RE.findall(text)
    return {"hashtags": _unique(hashtags), "mentions": _unique(mentions)}
