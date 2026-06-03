from datetime import datetime

from pydantic import BaseModel, Field


class ConversationBase(BaseModel):
    title: str | None = Field(default=None, description="Optional conversation title")

class ConversationCreate(ConversationBase):
    user_id: str = Field(..., description="Supabase user ID")

class ConversationRead(ConversationBase):
    id: str = Field(..., description="Conversation UUID")
    user_id: str = Field(..., description="Supabase user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True
