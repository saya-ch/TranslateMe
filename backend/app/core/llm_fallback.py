def draft_clarify_fallback(original: str) -> dict:
    return {
        "title": "孩子想聊聊最近的状态",
        "body": (
            "孩子想和你聊聊 ta 最近的状态。ta 希望你能先听 ta 说完，不急着评价。"
            "建议你找一个不被打扰的时间，用十分钟先听 ta 说。"
        ),
        "level": 3,
    }


def parent_guide_fallback(question: str) -> dict:
    return {
        "ice_breaker": (
            "先不要追问具体原因。可以先发一句："
            "'我注意到你最近不太开心，我不会逼你说，但如果你愿意，我可以先听你讲。'"
        ),
        "say_three": [
            "我先听你说完，不急着评价。",
            "谢谢你愿意告诉我。",
            "我们慢慢来，不用一次说完。",
        ],
        "not_say_three": [
            "别想那么多，没什么大不了的。",
            "别人家孩子不也好好的吗。",
            "你就是太矫情了。",
        ],
        "next_step": (
            "先听孩子说完，约定一个不被打扰的谈话时间；"
            "观察接下来几天的状态；"
            "如果持续低落或提到伤害自己，联系学校心理老师。"
        ),
        "reply_draft": (
            "我注意到你最近不太开心，我不会逼你说，但如果你愿意，我可以先听你讲十分钟。"
            "什么时候方便都可以，我等你。"
        ),
    }


def teacher_guide_fallback(input_text: str) -> dict:
    return {
        "summary": "学生最近学习/情绪状态需要关注。",
        "privacy_note": "谈话时请确保在学生听不见的时间和地点进行，不要在班级公开谈论。",
        "talk_advice": [
            "先表达关心，不追问。",
            "留时间让学生自己讲。",
            "如果学生不愿意讲，也不要勉强。",
        ],
        "observe_points": [
            "持续观察学生到校情况。",
            "观察睡眠、同伴关系、学业压力。",
            "观察家庭沟通与反馈。",
        ],
        "referral": "如果持续出现或者学生提到危险想法，联系学校心理老师和家长。",
    }


def fallback_for(kind: str, text: str) -> dict:
    if kind == "child_clarify":
        return draft_clarify_fallback(text)
    if kind == "parent_guide":
        return parent_guide_fallback(text)
    if kind == "teacher_guide":
        return teacher_guide_fallback(text)
    raise ValueError(f"Unknown fallback kind: {kind}")
