from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app import models, schemas
from app.database import get_db

app = FastAPI(title="HelpDesk API", version="1.0")

# ================= СПРАВОЧНИКИ =================
@app.get("/api/dictionaries/statuses", response_model=List[schemas.StatusResponse], tags=["Dictionaries"])
def get_statuses(db: Session = Depends(get_db)):
    return db.query(models.Status).all()

@app.get("/api/dictionaries/priorities", response_model=List[schemas.PriorityResponse], tags=["Dictionaries"])
def get_priorities(db: Session = Depends(get_db)):
    return db.query(models.Priority).all()

@app.get("/api/dictionaries/roles", response_model=List[schemas.RoleResponse], tags=["Dictionaries"])
def get_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()

# ================= ПОЛЬЗОВАТЕЛИ =================
@app.post("/api/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
  
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password, 
        role_id=user.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/api/users", response_model=List[schemas.UserResponse], tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# ================= ЗАЯВКИ (TICKETS) =================
@app.post("/api/tickets", response_model=schemas.TicketResponse, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    # При создании заявка всегда получает статус 1 (Open)
    new_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        author_id=ticket.author_id,
        priority_id=ticket.priority_id,
        status_id=1 
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.get("/api/tickets", response_model=List[schemas.TicketResponse], tags=["Tickets"])
def get_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()

@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketResponse, tags=["Tickets"])
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.patch("/api/tickets/{ticket_id}", response_model=schemas.TicketResponse, tags=["Tickets"])
def update_ticket_status(ticket_id: int, ticket_update: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket_update.status_id is not None:
        ticket.status_id = ticket_update.status_id
        # Если переводим в статус 3 (Resolved), ставим время решения
        if ticket_update.status_id == 3:
            ticket.resolved_at = datetime.now(timezone.utc)

    if ticket_update.assignee_id is not None:
        ticket.assignee_id = ticket_update.assignee_id

    db.commit()
    db.refresh(ticket)
    return ticket

# ================= КОММЕНТАРИИ =================
@app.post("/api/tickets/{ticket_id}/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED, tags=["Comments"])
def add_comment(ticket_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    new_comment = models.Comment(
        ticket_id=ticket_id,
        author_id=comment.author_id,
        text=comment.text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.get("/api/tickets/{ticket_id}/comments", response_model=List[schemas.CommentResponse], tags=["Comments"])
def get_ticket_comments(ticket_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.ticket_id == ticket_id).all()