import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)
db.init_app(app)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(nullable=False)

    service_tickets: Mapped[List['Service_Tickets']] = mapped_column(back_populates='customer')

service_mechanics = db.Table (
    'service_mechanics',
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

class Service_Tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(nullable=False)
    vin: Mapped[str] = mapped_column(nullable=False)
    service_date: Mapped[str] = mapped_column(nullable=False)
    service_description: Mapped[str] = mapped_column(nullable=False)

    customer: Mapped['Customer'] = mapped_column(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanics']] = mapped_column(secondary=service_mechanics, back_populates='service_tickets')

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(nullable=False)
    salary: Mapped[float] = mapped_column(nullable=False)

    service_tickets: Mapped[List['Service_Tickets']] = mapped_column(secondary=service_mechanics, back_populates='mechanics')

with app.app_context():
			db.create_all()		
app.run()