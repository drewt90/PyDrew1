import os
import shutil
import secrets
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_
from passlib.context import CryptContext

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PyprCM Case Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACTIVE_TOKENS = {}

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in")
    token = authorization.split(" ", 1)[1]
    user_id = ACTIVE_TOKENS.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/")
def health_check():
    return {"status": "online", "system": "PyprCM", "database": "SQLite"}

@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        hashed_password=pwd_context.hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login")
def login_user(creds: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == creds.username).first()
    if not user or not pwd_context.verify(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = secrets.token_hex(24)
    ACTIVE_TOKENS[token] = user.id
    return {"token": token, "username": user.username, "full_name": user.full_name}

@app.post("/clients", response_model=schemas.ClientResponse)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = db.query(models.Client).filter(models.Client.case_number == client.case_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Case number already exists")
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients", response_model=List[schemas.ClientResponse])
def list_clients(
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Client)
    if status and status != "All":
        query = query.filter(models.Client.status == status)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                models.Client.full_name.ilike(term),
                models.Client.case_number.ilike(term),
                models.Client.email.ilike(term),
                models.Client.claim_number.ilike(term),
                models.Client.insurance_provider.ilike(term),
                models.Client.attorney.ilike(term),
                models.Client.law_firm.ilike(term),
                models.Client.providers.ilike(term),
            )
        )
    return query.order_by(models.Client.id.desc()).all()

@app.patch("/clients/{client_id}", response_model=schemas.ClientResponse)
def update_client(
    client_id: int,
    updates: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client

@app.post("/clients/{client_id}/notes", response_model=schemas.CaseNoteResponse)
def create_case_note(
    client_id: int,
    note: schemas.CaseNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db_note = models.CaseNote(**note.model_dump(), client_id=client_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.post("/clients/{client_id}/upload", response_model=schemas.AttachmentResponse)
def upload_attachment(
    client_id: int,
    label: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    safe_name = f"{client_id}_{secrets.token_hex(4)}_{os.path.basename(file.filename)}"
    dest_path = UPLOAD_DIR / safe_name
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_att = models.Attachment(
        label=label,
        item_type="file",
        url_or_path=f"/uploads/{safe_name}",
        client_id=client_id,
    )
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att

@app.post("/clients/{client_id}/links", response_model=schemas.AttachmentResponse)
def add_link_attachment(
    client_id: int,
    link: schemas.LinkAttachmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db_att = models.Attachment(
        label=link.label,
        item_type="link",
        url_or_path=link.url,
        client_id=client_id,
    )
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att
