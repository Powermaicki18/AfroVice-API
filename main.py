from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
import os

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, String, Text,
    DateTime, ForeignKey
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session, joinedload

# ==========================
# DATABASE CONFIG
# ==========================

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# SQLALCHEMY MODELS
# ==========================

class Role(Base):
    __tablename__ = "Role"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    name = Column(String, nullable=False, unique=True)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "User"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(BigInteger, ForeignKey("Role.id"), nullable=False)
    photo = Column(String, nullable=True)

    role = relationship("Role", back_populates="users")
    tickets = relationship("Ticket", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class MusicGender(Base):
    __tablename__ = "Music_Gender"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    name = Column(String, nullable=False, unique=True)

    artist_genders = relationship("ArtistGender", back_populates="music_gender")


class Artist(Base):
    __tablename__ = "Artist"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    name = Column(String, nullable=False)
    photo = Column(String, nullable=False)

    genders = relationship("ArtistGender", back_populates="artist")
    presentations = relationship("PresentationArtist", back_populates="artist")


class ArtistGender(Base):
    __tablename__ = "Artist_Gender"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    artist_id = Column(BigInteger, ForeignKey("Artist.id"), nullable=False)
    music_gender_id = Column(BigInteger, ForeignKey("Music_Gender.id"), nullable=False)

    artist = relationship("Artist", back_populates="genders")
    music_gender = relationship("MusicGender", back_populates="artist_genders")


class Event(Base):
    __tablename__ = "Event"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    name = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    price = Column(Integer, nullable=False)

    presentations = relationship("Presentation", back_populates="event")


class Presentation(Base):
    __tablename__ = "Presentation"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    event_id = Column(BigInteger, ForeignKey("Event.id"), nullable=False)
    date_start = Column(DateTime(timezone=False), nullable=False)
    date_end = Column(DateTime(timezone=False), nullable=True)
    flyer = Column(String, nullable=False)

    event = relationship("Event", back_populates="presentations")
    artists = relationship("PresentationArtist", back_populates="presentation")
    tickets = relationship("Ticket", back_populates="presentation")
    comments = relationship("Comment", back_populates="presentation")


class PresentationArtist(Base):
    __tablename__ = "Presentation_Artist"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    presentation_id = Column(BigInteger, ForeignKey("Presentation.id"), nullable=False)
    artist_id = Column(BigInteger, ForeignKey("Artist.id"), nullable=False)
    schedule = Column(DateTime(timezone=False), nullable=False)

    presentation = relationship("Presentation", back_populates="artists")
    artist = relationship("Artist", back_populates="presentations")


class Ticket(Base):
    __tablename__ = "Ticket"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=False)
    presentation_id = Column(BigInteger, ForeignKey("Presentation.id"), nullable=False)

    user = relationship("User", back_populates="tickets")
    presentation = relationship("Presentation", back_populates="tickets")


class Comment(Base):
    __tablename__ = "Comment"

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    message = Column(Text, nullable=False)
    presentation_id = Column(BigInteger, ForeignKey("Presentation.id"), nullable=True)
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=True)

    presentation = relationship("Presentation", back_populates="comments")
    user = relationship("User", back_populates="comments")


# ==========================
# Pydantic SCHEMAS (Pydantic v2)
# ==========================

class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    name: str
    email: EmailStr
    photo: Optional[str] = None
    role_id: int


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MusicGenderBase(BaseModel):
    name: str


class MusicGenderCreate(MusicGenderBase):
    pass


class MusicGenderRead(MusicGenderBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ArtistBase(BaseModel):
    name: str
    photo: str


class ArtistCreate(ArtistBase):
    pass


class ArtistRead(ArtistBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    price: int


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PresentationBase(BaseModel):
    event_id: int
    date_start: datetime
    date_end: Optional[datetime] = None
    flyer: str


class PresentationCreate(PresentationBase):
    pass


class PresentationRead(PresentationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TicketBase(BaseModel):
    user_id: int
    presentation_id: int


class TicketCreate(TicketBase):
    pass


class TicketRead(TicketBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    message: str
    presentation_id: Optional[int] = None
    user_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentRead(BaseModel):
    id: int
    message: str
    created_at: datetime
    user: Optional[UserRead] = None
    presentation: Optional[PresentationRead] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================
# FASTAPI APP + CORS
# ==========================

app = FastAPI(title="AfroVice API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "https://afrovice.maaango.com",
    "https://afrovice-api.maaango.com",
]

vercel_regex = r"^https://.*\.vercel\.app$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=vercel_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ==========================
# HEALTH-CHECK ENDPOINTS
# ==========================

@app.get("/ping")
def ping():
    return "pong"

@app.get("/")
def hello():
    return "Hello world from FastAPI"


# ==========================
# ROLE ENDPOINTS
# ==========================

@app.get("/roles", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@app.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    db_role = Role(
        name=role.name,
        created_at=datetime.utcnow()
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


# ==========================
# USER ENDPOINTS
# ==========================

@app.get("/users", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password,  # ⚠️ in prod: hash this
        role_id=user.role_id,
        photo=user.photo,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==========================
# MUSIC GENDER ENDPOINTS
# ==========================

@app.get("/genders", response_model=List[MusicGenderRead])
def list_music_genders(db: Session = Depends(get_db)):
    return db.query(MusicGender).all()


@app.post("/genders", response_model=MusicGenderRead, status_code=status.HTTP_201_CREATED)
def create_music_gender(gender: MusicGenderCreate, db: Session = Depends(get_db)):
    db_gender = MusicGender(
        name=gender.name,
        created_at=datetime.utcnow()
    )
    db.add(db_gender)
    db.commit()
    db.refresh(db_gender)
    return db_gender


# ==========================
# ARTIST ENDPOINTS
# ==========================

@app.get("/artists", response_model=List[ArtistRead])
def list_artists(db: Session = Depends(get_db)):
    return db.query(Artist).all()


@app.get("/artists/{artist_id}", response_model=ArtistRead)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.get(Artist, artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@app.post("/artists", response_model=ArtistRead, status_code=status.HTTP_201_CREATED)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    db_artist = Artist(
        name=artist.name,
        photo=artist.photo,
        created_at=datetime.utcnow()
    )
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist


# ==========================
# EVENT ENDPOINTS
# ==========================

@app.get("/events", response_model=List[EventRead])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()


@app.get("/events/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(
        name=event.name,
        logo=event.logo,
        price=event.price,
        created_at=datetime.utcnow()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


# ==========================
# PRESENTATION ENDPOINTS
# ==========================

@app.get("/presentations", response_model=List[PresentationRead])
def list_presentations(db: Session = Depends(get_db)):
    return db.query(Presentation).all()


@app.get("/presentations/{presentation_id}", response_model=PresentationRead)
def get_presentation(presentation_id: int, db: Session = Depends(get_db)):
    pres = db.get(Presentation, presentation_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Presentation not found")
    return pres


@app.post("/presentations", response_model=PresentationRead, status_code=status.HTTP_201_CREATED)
def create_presentation(presentation: PresentationCreate, db: Session = Depends(get_db)):
    db_pres = Presentation(
        event_id=presentation.event_id,
        date_start=presentation.date_start,
        date_end=presentation.date_end,
        flyer=presentation.flyer,
        created_at=datetime.utcnow()
    )
    db.add(db_pres)
    db.commit()
    db.refresh(db_pres)
    return db_pres


# ==========================
# TICKET ENDPOINTS
# ==========================

@app.get("/tickets", response_model=List[TicketRead])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).all()


@app.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = Ticket(
        user_id=ticket.user_id,
        presentation_id=ticket.presentation_id,
        created_at=datetime.utcnow()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# ==========================
# COMMENT ENDPOINTS
# ==========================

@app.get("/comments", response_model=List[CommentRead])
def list_comments(db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .options(
            joinedload(Comment.user),
            joinedload(Comment.presentation),
        )
        .all()
    )
    return comments


@app.post("/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    db_comment = Comment(
        message=comment.message,
        presentation_id=comment.presentation_id,
        user_id=comment.user_id,
        created_at=datetime.utcnow()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

