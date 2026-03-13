import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

# ── Database Connection ──
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite if no Supabase URL (for local testing)
if not DATABASE_URL:
    os.makedirs("database", exist_ok=True)
    DATABASE_URL = "sqlite:///database/inspections.db"
    print("⚠️ Using local SQLite database")
else:
    print("✅ Using Supabase cloud database")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# ── Table 1: Inspections ──
class Inspection(Base):
    __tablename__ = "inspections"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    timestamp      = Column(DateTime, default=datetime.datetime.now)
    image_name     = Column(String)
    defect_type    = Column(String)
    confidence     = Column(Float)
    severity       = Column(String)
    recommendation = Column(String)
    region         = Column(String)
    result         = Column(String)

# ── Table 2: Users ──
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String, unique=True, nullable=False)
    name       = Column(String, nullable=False)
    email      = Column(String, nullable=False)
    password   = Column(String, nullable=False)
    role       = Column(String, default="viewer")
    created_at = Column(DateTime, default=datetime.datetime.now)
    is_active  = Column(Boolean, default=True)

# ── Table 3: Login History ──
class LoginHistory(Base):
    __tablename__ = "login_history"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String, nullable=False)
    login_time = Column(DateTime, default=datetime.datetime.now)
    status     = Column(String)
    ip_address = Column(String, default="localhost")

# Create all tables
Base.metadata.create_all(engine)

# ── Inspection Functions ──
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

# ── User Functions ──
def create_user(username, name, email, password, role="viewer"):
    import bcrypt
    session = Session()
    existing = session.query(User).filter_by(username=username).first()
    if existing:
        print(f"⚠️ User {username} already exists!")
        session.close()
        return False
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(
        username   = username,
        name       = name,
        email      = email,
        password   = hashed.decode('utf-8'),
        role       = role,
        created_at = datetime.datetime.now(),
        is_active  = True
    )
    session.add(user)
    session.commit()
    session.close()
    print(f"✅ User {username} created successfully!")
    return True

def get_user(username):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user

def get_all_users():
    session = Session()
    users = session.query(User).all()
    session.close()
    return users

def verify_password(username, password):
    import bcrypt
    user = get_user(username)
    if not user or not user.is_active:
        return False
    return bcrypt.checkpw(
        password.encode('utf-8'),
        user.password.encode('utf-8')
    )

def save_login_history(username, status):
    session = Session()
    record = LoginHistory(
        username   = username,
        login_time = datetime.datetime.now(),
        status     = status
    )
    session.add(record)
    session.commit()
    session.close()

print("✅ Database setup complete!")