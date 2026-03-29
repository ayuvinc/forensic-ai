from typing import Optional
from pydantic import BaseModel


class SlideSpec(BaseModel):
    slide_number: int
    title: str
    purpose: str
    key_message: str
    content_bullets: list[str]
    evidence_needed: list[str]
    suggested_visual: str
    speaker_notes: str
    risks_or_gaps: list[str]


class DeckStoryboard(BaseModel):
    case_id: str
    deck_objective: str
    audience: str
    decision_required: str
    key_messages: list[str]
    slides: list[SlideSpec]
    open_questions: list[str]


class DeckMasterPrompt(BaseModel):
    case_id: str
    audience: str
    target_tool: str = "claude_ppt"
    system_prompt: str
    user_prompt: str
    step_prompts: list[str]
    attachment_guidance: str
    usage_notes: str
