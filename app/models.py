from typing import List
from sqlalchemy import Date, ForeignKey
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
    inventory_items: Mapped[List['ServiceTicketInventory']] = relationship(back_populates='service_ticket')

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

class ServiceTicketInventory(Base):
    """Junction table: tracks which parts are used on which tickets + quantity"""
    __tablename__ = 'service_ticket_inventory'

    service_ticket_id: Mapped[int] = mapped_column(
        ForeignKey('service_tickets.id'), 
        primary_key=True
    )
    inventory_id: Mapped[int] = mapped_column(
        ForeignKey('inventory.id'), 
        primary_key=True
    )
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)

    service_ticket: Mapped['Service_Tickets'] = relationship(back_populates='inventory_items')
    inventory: Mapped['Inventory'] = relationship(back_populates='service_ticket_items')

class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_ticket_items: Mapped[List['ServiceTicketInventory']] = relationship(back_populates='inventory')