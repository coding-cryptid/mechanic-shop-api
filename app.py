import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_marshmallow import Marshmallow

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
ma = Marshmallow()
db.init_app(app)
ma.init_app(app)

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
    service_date: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_description: Mapped[str] = mapped_column(db.String(255), nullable=False)

    customer: Mapped['Customer'] = relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanics']] = relationship(secondary=service_mechanics, back_populates='service_tickets')

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List['Service_Tickets']] = relationship(secondary=service_mechanics, back_populates='mechanics')

with app.app_context():
    db.create_all()


# MARSHMALLOW SCHEMAS

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_Tickets
        load_instance = True

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics
        load_instance = True

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

# CRUD ENDPOINTS

# CUSTOMERS
# POST /customers
@app.route('/customers', methods=['POST'])
def create_customer():
    from flask import request, jsonify

    data = request.get_json()
    new_customer = Customer(
        name=data['name'],
        email=data['email'],
        phone_number=data['phone_number']
    )
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

# GET /customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers), 200

# GET /customers/<id>
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer), 200

# PUT /customers/<id>
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    from flask import request, jsonify

    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    customer.name = data['name']
    customer.email = data['email']
    customer.phone_number = data['phone_number']
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE /customers/<id>
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204

# SERVICE TICKETS
# POST /service_tickets
@app.route('/service_tickets', methods=['POST'])
def create_service_ticket():
    from flask import request, jsonify

    data = request.get_json()
    new_service_ticket = Service_Tickets(
        customer_id=data['customer_id'],
        vin=data['vin'],
        service_date=data['service_date'],
        service_description=data['service_description']
    )
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201

# GET /service_tickets
@app.route('/service_tickets', methods=['GET'])
def get_service_tickets():
    service_tickets = Service_Tickets.query.all()
    return service_tickets_schema.jsonify(service_tickets), 200

# GET /service_tickets/<id>
@app.route('/service_tickets/<int:id>', methods=['GET'])
def get_service_ticket(id):
    service_ticket = Service_Tickets.query.get_or_404(id)
    return service_ticket_schema.jsonify(service_ticket), 200

# PUT /service_tickets/<id>
@app.route('/service_tickets/<int:id>', methods=['PUT'])
def update_service_ticket(id):
    from flask import request, jsonify

    service_ticket = Service_Tickets.query.get_or_404(id)
    data = request.get_json()
    service_ticket.customer_id = data['customer_id']
    service_ticket.vin = data['vin']
    service_ticket.service_date = data['service_date']
    service_ticket.service_description = data['service_description']
    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200

# DELETE /service_tickets/<id>
@app.route('/service_tickets/<int:id>', methods=['DELETE'])
def delete_service_ticket(id):
    service_ticket = Service_Tickets.query.get_or_404(id)
    db.session.delete(service_ticket)
    db.session.commit()
    return '', 204

# MECHANICS
# POST /mechanics
@app.route('/mechanics', methods=['POST'])
def create_mechanic():
    from flask import request, jsonify

    data = request.get_json()
    new_mechanic = Mechanics(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        salary=data['salary']
    )
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# GET /mechanics
@app.route('/mechanics', methods=['GET'])
def get_mechanics():
    mechanics = Mechanics.query.all()
    return mechanics_schema.jsonify(mechanics), 200

# GET /mechanics/<id>
@app.route('/mechanics/<int:id>', methods=['GET'])
def get_mechanic(id):
    mechanic = Mechanics.query.get_or_404(id)
    return mechanic_schema.jsonify(mechanic), 200

# PUT /mechanics/<id>
@app.route('/mechanics/<int:id>', methods=['PUT'])
def update_mechanic(id):
    from flask import request, jsonify

    mechanic = Mechanics.query.get_or_404(id)
    data = request.get_json()
    mechanic.name = data['name']
    mechanic.email = data['email']
    mechanic.phone = data['phone']
    mechanic.salary = data['salary']
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# DELETE /mechanics/<id>
@app.route('/mechanics/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanics.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    app.run()