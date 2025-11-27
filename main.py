from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date,datetime

from database import Base, engine, SessionLocal
from models import JournalEntry

# DB erstellen, falls sie nicht existiert
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Dependency: DB Session bekommen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def journal_form(request: Request):
    today = date.today().isoformat()
    return templates.TemplateResponse("journal.html", {"request": request, "today": today})

@app.get("/entries", response_class=HTMLResponse)
def list_entries(request: Request, db: Session = Depends(get_db)):
    entries = db.query(JournalEntry).order_by(JournalEntry.id.desc()).limit(50).all()
    return templates.TemplateResponse("entries.html", {
        "request": request,
        "entries": entries
    })

@app.post("/submit")
def submit(
    request: Request,
    entry_date: str = Form(datetime.now),
    reading: bool = Form(False),
    exercise: bool = Form(False),
    no_meat: int = Form(0),
    flossing: bool = Form(False),
    health: str = Form("good"),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    
    # String "YYYY-MM-DD" in datetime umwandeln
    entry_date_obj = datetime.strptime(entry_date, "%Y-%m-%d")

    entry = JournalEntry(entry_date=entry_date_obj, reading=reading, exercise=exercise, no_meat=no_meat, flossing=flossing, health=health, notes=notes)
    db.add(entry)
    db.commit()

    return RedirectResponse("/", status_code=303)
