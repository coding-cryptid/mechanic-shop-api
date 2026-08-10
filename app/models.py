from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from datetime import date

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List['Service_Tickets']] = relationship(back_populates='customer')

service_mechanics = db.Table(
    'service_mechanics',
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'), primary_key=True)
)

class Service_Tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_description: Mapped[str] = mapped_column(db.String(255), nullable=False)

    customer: Mapped['Customer'] = relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanics']] = relationship(secondary=service_mechanics, back_populates='service_tickets')

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[int] = mapped_column(db.Integer, nullable=False)

    service_tickets: Mapped[List['Service_Tickets']] = relationship(secondary=service_mechanics, back_populates='mechanics')

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)