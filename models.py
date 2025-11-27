from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from datetime import date,datetime
from database import Base

class JournalEntry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    entry_date = Column(DateTime, default=datetime.now)
    reading = Column(Boolean, default=False)
    exercise = Column(Boolean, default=False)
    no_meat = Column(Integer, default=0)
    flossing = Column(Boolean, default=False)
    health = Column(String, default="")
    notes = Column(String, default="")
