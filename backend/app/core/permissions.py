from typing import List


LEVEL = {
    "完全私密": 0,
    "仅AI使用": 1,
    "模糊提醒": 2,
    "降敏摘要": 3,
    "原话分享": 4,
}


ROLE_CHILD = "child"
ROLE_PARENT = "parent"
ROLE_TEACHER = "teacher"
ROLE_ADMIN = "admin"

ALL_ROLES = [ROLE_CHILD, ROLE_PARENT, ROLE_TEACHER, ROLE_ADMIN]


_DEFAULT_MAX_LEVEL_BY_ROLE = {
    ROLE_CHILD: LEVEL["原话分享"],
    ROLE_PARENT: LEVEL["降敏摘要"],
    ROLE_TEACHER: LEVEL["降敏摘要"],
    ROLE_ADMIN: LEVEL["原话分享"],
}


_PURPOSE_MAX_BY_ROLE = {
    "view_memory": {
        ROLE_CHILD: LEVEL["原话分享"],
        ROLE_PARENT: LEVEL["降敏摘要"],
        ROLE_TEACHER: LEVEL["模糊提醒"],
        ROLE_ADMIN: LEVEL["原话分享"],
    },
    "chat_summary": {
        ROLE_CHILD: LEVEL["原话分享"],
        ROLE_PARENT: LEVEL["降敏摘要"],
        ROLE_TEACHER: LEVEL["模糊提醒"],
        ROLE_ADMIN: LEVEL["降敏摘要"],
    },
    "ai_processing": {
        ROLE_CHILD: LEVEL["仅AI使用"],
        ROLE_PARENT: LEVEL["仅AI使用"],
        ROLE_TEACHER: LEVEL["仅AI使用"],
        ROLE_ADMIN: LEVEL["仅AI使用"],
    },
    "default": _DEFAULT_MAX_LEVEL_BY_ROLE,
}


def can_view(
    role: str,
    level: int,
    requester_role: str,
    allowed_roles: List[str],
) -> bool:
    if allowed_roles and requester_role not in allowed_roles:
        return False

    max_allowed = allowed_memories_for_role(requester_role, "view_memory")
    if level > max_allowed:
        return False

    return True


def allowed_memories_for_role(requester_role: str, purpose: str = "default") -> int:
    table = _PURPOSE_MAX_BY_ROLE.get(purpose) or _PURPOSE_MAX_BY_ROLE["default"]
    return int(table.get(requester_role, LEVEL["完全私密"]))


def level_by_name(name: str) -> int:
    if name in LEVEL:
        return LEVEL[name]
    try:
        value = int(name)
        if value in set(LEVEL.values()):
            return value
    except (TypeError, ValueError):
        pass
    return LEVEL["完全私密"]


def is_owner(requester_id: str, owner_id: str) -> bool:
    if not requester_id or not owner_id:
        return False
    return str(requester_id) == str(owner_id)
