from typing import Tuple


_CHILD_CLARIFY_SYSTEM = (
    "你是负责帮孩子整理表达的助手。你会读取孩子的一段话，然后生成可以让家长温和理解、但不透露过激用词的草稿。"
    "\n输出严格 JSON: {\"title\": \"...\", \"body\": \"...\", \"level\": 3}"
)


_PARENT_GUIDE_SYSTEM = (
    "你是亲子沟通顾问。家长向你提问，请给出通用沟通建议。"
    "注意：不要猜测孩子具体说了什么、不要透露孩子的私密内容。"
    "\n输出严格 JSON: "
    "{\"ice_breaker\": \"...\", \"say_three\": [\"...\",\"...\",\"...\"], "
    "\"not_say_three\": [\"...\",\"...\",\"...\"], \"next_step\": \"...\", \"reply_draft\": \"...\"}"
)


_TEACHER_GUIDE_SYSTEM = (
    "你是学校心理咨询教师。根据记录的观察信息，帮老师整理谈话建议和转介建议。"
    "不要判断严重程度，不要用诊断词。"
    "\n输出严格 JSON: "
    "{\"summary\": \"...\", \"privacy_note\": \"...\", \"talk_advice\": [\"...\",\"...\",\"...\"], "
    "\"observe_points\": [\"...\",\"...\",\"...\"], \"referral\": \"...\"}"
)


def child_clarify(original: str) -> Tuple[str, str]:
    safe_original = (original or "").strip()
    system = _CHILD_CLARIFY_SYSTEM
    user = (
        f"孩子说: {safe_original}\n\n"
        "请生成一段可以发给家长的降敏摘要草稿，150字以内。"
    )
    return system, user


def parent_guide(question: str) -> Tuple[str, str]:
    safe_question = (question or "").strip()
    system = _PARENT_GUIDE_SYSTEM
    user = (
        f"家长提问: {safe_question}\n\n"
        "请给出通用沟通建议（破冰句、可以说的三句话、避免说的三句话、下一步行动、回复草稿）。"
    )
    return system, user


def teacher_guide(input_text: str) -> Tuple[str, str]:
    safe_input = (input_text or "").strip()
    system = _TEACHER_GUIDE_SYSTEM
    user = (
        f"观察/记录信息: {safe_input}\n\n"
        "请整理谈话建议、观察要点和转介建议。不要使用诊断词。"
    )
    return system, user


def build_prompt(kind: str, text: str) -> Tuple[str, str]:
    if kind == "child_clarify":
        return child_clarify(text)
    if kind == "parent_guide":
        return parent_guide(text)
    if kind == "teacher_guide":
        return teacher_guide(text)
    raise ValueError(f"Unknown prompt kind: {kind}")
