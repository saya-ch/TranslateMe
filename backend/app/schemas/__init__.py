from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

config = ConfigDict(from_attributes=True, extra="ignore")


# ========== Auth ==========

class RegisterRequest(BaseModel):
    model_config = config
    username: str = Field(min_length=3, max_length=64)
    display_name: str = Field(min_length=1, max_length=64)
    role: str = Field(pattern="^(child|parent|teacher|counselor)$")
    password: str = Field(min_length=6, max_length=255)


class LoginRequest(BaseModel):
    model_config = config
    username: str
    password: str


class TokenResponse(BaseModel):
    model_config = config
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    model_config = config
    id: str
    username: str
    display_name: str
    role: str


class MeResponse(BaseModel):
    model_config = config
    user: UserInfo
    child_profiles: List[Dict[str, Any]] = []


# ========== Chat ==========

class ChatRequest(BaseModel):
    model_config = config
    conversation_id: Optional[str] = None
    child_id: str
    text: str = Field(min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    model_config = config
    message_id: str
    conversation_id: str
    needs_safety_check: bool = False
    safety_event_id: Optional[str] = None
    draft: Optional[Dict[str, Any]] = None
    source: str = "fallback"


# ========== Drafts ==========

class DraftPreview(BaseModel):
    model_config = config
    draft_id: str
    title: str
    body: str
    level: int
    scope: str


class DraftConfirmRequest(BaseModel):
    model_config = config
    to_role: str
    level: int


class DraftConfirmResponse(BaseModel):
    model_config = config
    share_id: str
    inbox_message_id: str
    delivered_to: str
    title: str
    body: str


# ========== Inbox ==========

class InboxItem(BaseModel):
    model_config = config
    id: str
    child_id: str
    from_role: str
    title: str
    body: str
    level: int
    read: bool
    delivered_at: datetime
    status: str


class InboxListResponse(BaseModel):
    model_config = config
    items: List[InboxItem]
    total: int


class ReplyRequest(BaseModel):
    model_config = config
    child_id: str
    to_role: str = Field(pattern="^(child|parent|teacher|counselor)$")
    body: str = Field(min_length=1, max_length=5000)
    source_inbox_id: Optional[str] = None


class ReplyResponse(BaseModel):
    model_config = config
    reply_id: str
    inbox_message_id: str


class ShareRevokeResponse(BaseModel):
    model_config = config
    revoked: bool
    affected_inbox_ids: List[str]


# ========== Memory ==========

class MemorySummaryItem(BaseModel):
    model_config = config
    id: str
    type: str
    explainable_summary: Optional[str] = None
    level: int
    status: str


class MemoryListResponse(BaseModel):
    model_config = config
    items: List[MemorySummaryItem]


class MemoryDeleteResponse(BaseModel):
    model_config = config
    deleted: bool
    memory_id: str


class MemoryApproveResponse(BaseModel):
    model_config = config
    memory_id: str
    level: int
    approved: bool


# ========== Consent ==========

class ConsentCreate(BaseModel):
    model_config = config
    child_id: str
    scope: str
    purpose: str = Field(pattern="^(share|join_group|memory_upgrade|safety_escalation)$")
    source: str = Field(pattern="^(child|guardian|system_safety)$")


class ConsentResponse(BaseModel):
    model_config = config
    id: str
    child_id: str
    scope: str
    purpose: str
    status: str
    source: str


class ConsentRevokeResponse(BaseModel):
    model_config = config
    revoked: bool
    consent_id: str
    affected_shares: List[str]


# ========== Safety ==========

class SafetyCheckRequest(BaseModel):
    model_config = config
    text: str
    child_id: str


class SafetyCheckResponse(BaseModel):
    model_config = config
    needs_check: bool
    patterns: List[str] = []


class SafetyResolveRequest(BaseModel):
    model_config = config
    branch: str = Field(pattern="^(safe_continue|unsafe_support|escalation)$")


class SafetyResolveResponse(BaseModel):
    model_config = config
    resolved_at: Optional[datetime] = None
    resources_shown: bool
    llm_called: bool
    message: str


# ========== Family Group ==========

class FamilyGroupCreate(BaseModel):
    model_config = config
    child_user_id: str
    guardian_user_id: str


class FamilyGroupResponse(BaseModel):
    model_config = config
    group_id: str
    child_id: str
    members: List[Dict[str, Any]]


class MemberAdd(BaseModel):
    model_config = config
    user_id: str
    relation: str = Field(pattern="^(guardian|teacher|counselor|self)$")


class MemberRemoveResponse(BaseModel):
    model_config = config
    removed: bool
    member_id: str


# ========== Generic ==========

class MessageResponse(BaseModel):
    model_config = config
    message: str


class ErrorResponse(BaseModel):
    model_config = config
    detail: str
    code: Optional[str] = None
