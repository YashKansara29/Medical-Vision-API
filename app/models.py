from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

#Represents one patient scan interaction
class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    #One session can have many messages
    messages: List["ChatMessage"] = Relationship(back_populates="session")

#Represents the back-and-forth chat
class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chatsession.id")
    role: str = Field(...) # 'user' (doctor) or 'ai' 
    content: str = Field(...) #actual text
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Link back to the parent session
    session: ChatSession = Relationship(back_populates="messages")