import os
import unittest
from datetime import date, datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from werkzeug.security import generate_password_hash

from app import create_app
from app.models import (
    db,
    Customer,
    Inventory,
    Mechanics,
    Service_Tickets,
    ServiceTicketInventory,
    Users,
)
from app.utils.util import encode_token, SECRET_KEY, ALGORITHM
from jose import jwt


def uses_fixtures(fixtures):
    def decorator(func):
        func._fixtures = tuple(fixtures)
        return func
    return decorator


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            RATELIMIT_HEADERS_ENABLED=True,
        )
        self.client = self.app.test_client()
        self.db = db

        with self.app.app_context():
            self.db.drop_all()
            self.db.create_all()

            method = getattr(self, self._testMethodName)
            requested = set(getattr(method, "_fixtures", ()))

            if requested & {"auth_token", "expired_token", "auth_token_no_customer"}:
                requested.add("sample_users")

            if requested & {
                "sample_tickets",
                "sample_tickets_with_mechanics",
                "sample_tickets_with_parts",
                "sample_mechanics_with_tickets",
            }:
                requested.add("sample_customers")

            if requested & {
                "sample_tickets_with_parts",
            }:
                requested.add("sample_inventory")
                requested.add("sample_tickets")

            if requested & {
                "sample_tickets_with_mechanics",
                "sample_mechanics_with_tickets",
            }:
                requested.add("sample_mechanics")
                requested.add("sample_tickets")

            self._load_fixtures(requested)

            self.sample_customers = self._get_all(Customer)
            self.sample_inventory = self._get_all(Inventory)
            self.sample_mechanics = self._get_all(Mechanics)
            self.sample_tickets = self._get_all(Service_Tickets)
            self.sample_users = self._get_all(Users)

            self.auth_token = None
            self.expired_token = None
            self.auth_token_no_customer = None

            if "auth_token" in requested:
                user = self.db.session.query(Users).filter_by(
                    email="user1@example.com"
                ).one()
                self.auth_token = encode_token(user.id)

            if "expired_token" in requested:
                user = self.db.session.query(Users).filter_by(
                    email="user1@example.com"
                ).one()
                self.expired_token = jwt.encode(
                    {
                        "sub": str(user.id),
                        "exp": datetime.utcnow() - timedelta(hours=1),
                        "iat": datetime.utcnow() - timedelta(hours=2),
                    },
                    SECRET_KEY,
                    algorithm=ALGORITHM,
                )

            if "auth_token_no_customer" in requested:
                user = self.db.session.query(Users).filter_by(
                    email="nocustomer@example.com"
                ).one()
                self.auth_token_no_customer = encode_token(user.id)

    def tearDown(self):
        try:
            with self.app.app_context():
                self.db.session.remove()
                self.db.drop_all()
        finally:
            self.app = None
            self.client = None

    def _get_all(self, model):
        return self.db.session.query(model).all()

    def _load_fixtures(self, requested):
        if "sample_customers" in requested:
            self._seed_customers()
        if "sample_inventory" in requested:
            self._seed_inventory()
        if "sample_mechanics" in requested:
            self._seed_mechanics()
        if "sample_users" in requested:
            self._seed_users()
        if "sample_tickets" in requested:
            self._seed_tickets()
        if "sample_mechanics_with_tickets" in requested:
            self._attach_mechanics_to_tickets()
        if "sample_tickets_with_mechanics" in requested:
            self._attach_mechanics_to_tickets()
        if "sample_tickets_with_parts" in requested:
            self._seed_ticket_parts()

        self.db.session.commit()

    def _seed_customers(self):
        customers = [
            Customer(
                name="John Doe",
                email="user1@example.com",
                phone_number="555-1234",
            ),
            Customer(
                name="Jane Doe",
                email="jane@example.com",
                phone_number="555-5678",
            ),
            Customer(
                name="Alice Johnson",
                email="alice@example.com",
                phone_number="555-1111",
            ),
        ]
        self.db.session.add_all(customers)
        self.db.session.flush()

    def _seed_inventory(self):
        items = [
            Inventory(name="Premium Oil Filter", price=19.99),
            Inventory(name="Air Filter", price=12.99),
            Inventory(name="Spark Plugs", price=8.99),
        ]
        self.db.session.add_all(items)
        self.db.session.flush()

    def _seed_mechanics(self):
        mechanics = [
            Mechanics(
                name="Robert Smith",
                email="robert@example.com",
                phone_number="555-5555",
                salary=50000,
            ),
            Mechanics(
                name="Sarah Johnson",
                email="sarah@example.com",
                phone_number="555-5556",
                salary=52000,
            ),
            Mechanics(
                name="Mike Brown",
                email="mike@example.com",
                phone_number="555-5557",
                salary=48000,
            ),
        ]
        self.db.session.add_all(mechanics)
        self.db.session.flush()

    def _seed_users(self):
        users = [
            Users(
                name="Test User",
                email="user1@example.com",
                password=generate_password_hash("password123", method='pbkdf2:sha256'),
            ),
            Users(
                name="No Customer User",
                email="nocustomer@example.com",
                password=generate_password_hash("password123", method='pbkdf2:sha256'),
            ),
        ]
        self.db.session.add_all(users)
        self.db.session.flush()

    def _seed_tickets(self):
        tickets = [
            Service_Tickets(
                customer_id=1,
                vin="ABC123456789",
                service_date=date(2024, 5, 15),
                service_description="Oil change and filter replacement",
            ),
            Service_Tickets(
                customer_id=1,
                vin="XYZ987654321",
                service_date=date(2024, 6, 10),
                service_description="Brake inspection",
            ),
            Service_Tickets(
                customer_id=2,
                vin="DEF456789012",
                service_date=date(2024, 7, 20),
                service_description="Tire rotation",
            ),
        ]
        self.db.session.add_all(tickets)
        self.db.session.flush()

    def _attach_mechanics_to_tickets(self):
        mechanics = self.db.session.query(Mechanics).order_by(Mechanics.id).all()
        tickets = self.db.session.query(Service_Tickets).order_by(Service_Tickets.id).all()
        if not mechanics or not tickets:
            return

        tickets[0].mechanics = [mechanics[0], mechanics[1]]
        if len(tickets) > 1 and len(mechanics) > 1:
            tickets[1].mechanics = [mechanics[0]]
        if len(tickets) > 2 and len(mechanics) > 2:
            tickets[2].mechanics = [mechanics[2]]
        self.db.session.flush()

    def _seed_ticket_parts(self):
        tickets = self.db.session.query(Service_Tickets).order_by(Service_Tickets.id).all()
        inventory = self.db.session.query(Inventory).order_by(Inventory.id).all()
        if not tickets or len(inventory) < 2:
            return

        self.db.session.add_all([
            ServiceTicketInventory(
                service_ticket_id=tickets[0].id,
                inventory_id=inventory[0].id,
                quantity=2,
            ),
            ServiceTicketInventory(
                service_ticket_id=tickets[0].id,
                inventory_id=inventory[1].id,
                quantity=1,
            ),
        ])
        self.db.session.flush()
