from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

# Create database
os.makedirs("database", exist_ok=True)
engine = create_engine("sqlite:///database/inspections.db", echo=False)
Base = declarative_base()

# Define table
class Inspection(Base):
    __tablename__ = "inspections"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    timestamp       = Column(DateTime, default=datetime.datetime.now)
    image_name      = Column(String)
    defect_type     = Column(String)
    confidence      = Column(Float)
    severity        = Column(String)
    recommendation  = Column(String)
    region          = Column(String)
    result          = Column(String)  # PASS or FAIL

# Create table
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_inspection(image_name, defect_type, confidence, 
                   severity, recommendation, region, result):
    session = Session()
    record = Inspection(
        timestamp      = datetime.datetime.now(),
        image_name     = image_name,
        defect_type    = defect_type,
        confidence     = confidence,
        severity       = severity,
        recommendation = recommendation,
        region         = region,
        result         = result
    )
    session.add(record)
    session.commit()
    session.close()
    print(f"✅ Saved to database: {image_name} — {result}")

def get_all_inspections():
    session = Session()
    records = session.query(Inspection).all()
    session.close()
    return records

print("✅ Database setup complete!")