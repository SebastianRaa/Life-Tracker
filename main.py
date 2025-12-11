from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date,datetime,timedelta

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
    entries = db.query(JournalEntry).order_by(JournalEntry.entry_date.desc()).limit(50).all()
    return templates.TemplateResponse("entries.html", {
        "request": request,
        "entries": entries
    })

@app.get("/edit/{entry_id}", response_class=HTMLResponse)
def edit_entry_form(entry_id: int, request: Request, db: Session = Depends(get_db)):
    entry = db.query(JournalEntry).get(entry_id)
    if not entry:
        return RedirectResponse("/entries", status_code=303)
    return templates.TemplateResponse("edit_entry.html", {"request": request, "entry": entry})


@app.get("/visualization")
def visualization(request: Request, year: int = None, month: int = None, db: Session = Depends(get_db)):
    # Standard: aktueller Monat
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Start / Ende
    start_date = date(year, month, 1)
    if month == 12:
        next_month_date = date(year + 1, 1, 1)
    else:
        next_month_date = date(year, month + 1, 1)
    end_date = next_month_date - timedelta(days=1)

    # Query
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.entry_date >= start_date)
        .filter(JournalEntry.entry_date <= end_date)
        .order_by(JournalEntry.entry_date.asc())
        .all()
    )

    # Navigationsdaten
    prev_year = year - 1 if month == 1 else year
    prev_month = 12 if month == 1 else month - 1

    next_year = year + 1 if month == 12 else year
    next_month = 1 if month == 12 else month + 1

    return templates.TemplateResponse(
        "visualization.html",
        {
            "request": request,
            "entries": entries,
            "current_year": year,
            "current_month": month,
            "prev_year": prev_year,
            "prev_month": prev_month,
            "next_year": next_year,
            "next_month": next_month,
        }
    )


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


@app.post("/edit/{entry_id}")
def edit_entry_submit(entry_id: int, 
                      entry_date: str = Form(...),
                      reading: bool = Form(False),
                      exercise: bool = Form(False),
                      no_meat: int = Form(0),
                      flossing: bool = Form(False),
                      health: str = Form("good"),
                      notes: str = Form(""),
                      db: Session = Depends(get_db)):

    entry = db.query(JournalEntry).get(entry_id)
    if entry:
        entry.entry_date = datetime.strptime(entry_date, "%Y-%m-%d")
        entry.reading = reading
        entry.exercise = exercise
        entry.no_meat = no_meat
        entry.flossing = flossing
        entry.health = health
        entry.notes = notes
        db.commit()

    return RedirectResponse("/entries", status_code=303)


@app.post("/delete/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(JournalEntry).get(entry_id)
    if entry:
        db.delete(entry)
        db.commit()
    return RedirectResponse("/entries", status_code=303)