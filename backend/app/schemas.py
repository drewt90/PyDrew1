from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- User Auth Schemas ---
class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str

    class Config:
        from_attributes = True

# --- Attachment Schemas ---
class LinkAttachmentCreate(BaseModel):
    label: str
    url: str

class AttachmentResponse(BaseModel):
    id: int
    label: str
    item_type: str
    url_or_path: str
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Case Note Schemas ---
class CaseNoteCreate(BaseModel):
    title: str
    content: str

class CaseNoteResponse(CaseNoteCreate):
    id: int
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Client Schemas ---
class ClientCreate(BaseModel):
    full_name: str
    case_number: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    ssn: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    claim_number: Optional[str] = None
    attorney: Optional[str] = None
    law_firm: Optional[str] = None
    providers: Optional[str] = None
    status: str = "Active"

class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    case_number: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    ssn: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    claim_number: Optional[str] = None
    attorney: Optional[str] = None
    law_firm: Optional[str] = None
    providers: Optional[str] = None
    status: Optional[str] = None

class ClientResponse(ClientCreate):
    id: int
    created_at: datetime
    notes: List[CaseNoteResponse] = []
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True
