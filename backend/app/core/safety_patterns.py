"""
安全检测模块 - 检测自杀/自残/伤害他人等高风险表达
"""

import hashlib
from typing import List, Tuple

HIGH_RISK_PATTERNS: List[Tuple[str, List[str]]] = [
    ("suicide", ["想死", "不想活", "自杀", "结束自己", "结束一切", "永远消失", "结束生命"]),
    ("self_harm", ["自残", "伤害自己", "自伤", "割腕", "想跳楼"]),
    ("harm_others", ["伤害别人", "想杀", "想害死", "想杀掉"]),
    ("hopeless", ["活着没意思", "撑不下去", "撑不住了", "活着没意义", "活着有什么意思"]),
]


def needs_safety_check(text: str) -> bool:
    """检测文本是否包含高风险表达"""
    if not text:
        return False
    normalized = text.replace(" ", "").replace("\t", "").replace("\n", "").strip().lower()
    for _, keywords in HIGH_RISK_PATTERNS:
        for kw in keywords:
            if kw in normalized:
                return True
    return False


def detect_patterns(text: str) -> List[str]:
    """返回命中的 pattern 名称（不含原文）"""
    if not text:
        return []
    normalized = text.replace(" ", "").replace("\t", "").replace("\n", "").strip().lower()
    matched: List[str] = []
    for name, keywords in HIGH_RISK_PATTERNS:
        if any(kw in normalized for kw in keywords):
            matched.append(name)
    return matched


def text_hash(text: str) -> str:
    """生成文本哈希，仅用于去重/跟踪，不暴露原文"""
    normalized = text.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()
