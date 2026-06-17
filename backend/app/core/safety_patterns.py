import hashlib


HIGH_RISK_KEYWORDS = [
    "想死",
    "不想活",
    "自杀",
    "自残",
    "伤害自己",
    "伤害别人",
    "结束一切",
    "永远消失",
    "活着没意思",
    "撑不下去",
    "跳楼",
    "割腕",
]


def _normalize(text: str) -> str:
    if not text:
        return ""
    return text.lower().replace(" ", "")


def needs_safety_check(text: str) -> dict:
    normalized = _normalize(text)
    patterns_hit: list[str] = []

    if normalized:
        for kw in HIGH_RISK_KEYWORDS:
            if kw in normalized:
                patterns_hit.append(kw)

    original = text or ""
    trigger_hash = hashlib.sha256(original.encode("utf-8")).hexdigest()

    return {
        "needs_check": len(patterns_hit) > 0,
        "patterns": patterns_hit,
        "trigger_hash": trigger_hash,
    }
