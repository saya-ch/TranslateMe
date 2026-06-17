"""
LLM 失败时的本地模板 fallback
确保在无 LLM 情况下也能提供基础功能
"""

from typing import Dict, Any


DRAFT_DEFAULT_TITLE = "孩子想跟你聊聊"
DRAFT_DEFAULT_BODY = "孩子想找个时间和你聊聊。ta 还没准备好讲细节，希望你先表达愿意听，不追问原因。"
DRAFT_DEFAULT_SUGGESTIONS = [
    "可以加入希望谈话的具体时间",
    "可以加入自己当下的状态",
    "可以表达希望对方如何做",
]


def generate_draft_fallback(text: str) -> Dict[str, Any]:
    """降敏摘要草稿的 fallback"""
    return {
        "title": DRAFT_DEFAULT_TITLE,
        "body": DRAFT_DEFAULT_BODY,
        "suggestions": DRAFT_DEFAULT_SUGGESTIONS,
    }


def guard_outgoing_draft(draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    对外草稿的最后一道隐私守门。

    LLM 可用于理解孩子的输入，但默认发给家长/老师的草稿不能自动带出
    学校、睡眠、家人冲突等具体细节。孩子若想分享细节，应在预览卡中主动编辑加入。
    """
    suggestions = draft.get("suggestions")
    safe_suggestions = suggestions if isinstance(suggestions, list) and suggestions else DRAFT_DEFAULT_SUGGESTIONS
    return {
        "title": DRAFT_DEFAULT_TITLE,
        "body": DRAFT_DEFAULT_BODY,
        "suggestions": safe_suggestions[:3],
    }


def generate_parent_guide_fallback(question: str) -> Dict[str, Any]:
    """家长建议的 fallback"""
    return {
        "firewall_note": "未经孩子同意，我不能透露具体内容，也不能暗示孩子经历了什么。以下是通用沟通建议。",
        "icebreaker": "先不要追问具体原因，先表达你愿意听。孩子愿意开口需要安全感。可以先问：'你什么时候想说都可以，我先听。'",
        "say_three": [
            "我先听你说完，不急着评价。",
            "你可以慢慢说，不用一次说完。",
            "不管是什么事，我都愿意先听。",
        ],
        "not_say_three": [
            "别想那么多，没什么大不了的。",
            "你就是太矫情/太敏感了。",
            "别人家孩子不都好好的吗？",
        ],
        "next_step": "先听孩子说完，约定一个不被打扰的谈话时间；观察接下来几天的状态；如果持续低落或提到伤害自己，联系学校心理老师。",
        "reply_draft": "我注意到你最近不太开心，我不会逼你说，但如果你愿意，我可以先听你讲十分钟。什么时候方便都可以，我等你。",
    }


def generate_teacher_guide_fallback(observation: str) -> Dict[str, Any]:
    """老师建议的 fallback"""
    return {
        "summary": "学生表现出需要沟通的信号，建议私下安排时间谈话。",
        "privacy_note": "请保护学生隐私，不要在班级公开讨论，避免让同学知道。",
        "talk_advice": [
            "找一个不被同学听见的时间和地点",
            "先听不评价",
            "不要追问具体原因",
        ],
        "observe_points": [
            "持续观察到校情况",
            "睡眠状态",
            "同伴关系",
            "学业压力变化",
        ],
        "referral_advice": "如果持续出现危险信号，联系学校心理老师或家长。",
    }


PARENT_SUBJECT_KEYWORDS = ["孩子", "儿子", "女儿", "他", "她", "ta"]

PARENT_FIREWALL_KEYWORDS = [
    "原话",
    "具体内容",
    "具体细节",
    "详细内容",
    "详细细节",
    "说了什么",
    "跟你说什么",
    "跟你聊了什么",
    "发生了什么",
    "经历了什么",
    "什么事",
    "怎么回事",
    "到底怎么了",
    "真正原因",
    "真实原因",
    "告诉我具体",
    "告诉我内容",
    "告诉我细节",
    "告诉我原话",
    "透露",
]


def is_firewall_probing(question: str) -> bool:
    """检测家长是否在追问孩子未授权的具体内容"""
    if not question:
        return False
    normalized = question.replace(" ", "").replace("\t", "").replace("\n", "").strip().lower()
    if not any(kw in normalized for kw in PARENT_SUBJECT_KEYWORDS):
        return False
    return any(kw in normalized for kw in PARENT_FIREWALL_KEYWORDS)


SAFETY_RESOURCES = {
    "escalation": {
        "message": "如果你或身边的人正处于立即危险中，请立刻联系身边可信成年人、紧急联系人、学校心理老师。如存在立即人身危险，请拨打 110 / 120。",
        "support_lines": [
            "12355 青少年服务热线（心理支持与求助咨询）",
            "12356 心理援助热线（心理支持与求助咨询）",
        ],
    },
    "unsafe_support": {
        "message": "这可能需要真人支持。以下是一些可以联系的资源。",
        "support_lines": [
            "12355 青少年服务热线",
            "12356 心理援助热线",
            "学校心理老师",
            "身边可信成年人",
        ],
    },
}
