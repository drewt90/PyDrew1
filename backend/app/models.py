from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    case_number = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    ssn = Column(String, nullable=True)
    insurance_provider = Column(String, nullable=True)
    insurance_id = Column(String, nullable=True)
    claim_number = Column(String, index=True, nullable=True)
    attorney = Column(String, nullable=True)
    law_firm = Column(String, nullable=True)
    providers = Column(Text, nullable=True)
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    notes = relationship("CaseNote", back_populates="client", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="client", cascade="all, delete-orphan")


class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="notes")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    item_type = Column(String, nullable=False)
    url_or_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="attachments")
