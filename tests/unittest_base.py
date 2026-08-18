import importlib
import unittest


class APITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = cls._load_app()
        cls.db = cls._load_db()

    @staticmethod
    def _load_app():
        candidates = ("run", "app")

        for module_name in candidates:
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue

            app = getattr(module, "app", None)
            if app is not None and hasattr(app, "test_client"):
                return app

            factory = getattr(module, "create_app", None)
            if callable(factory):
                return factory()

        raise ImportError(
            "Could not find the Flask application. "
            "Make sure run.py exposes `app`, or exposes a `create_app()` function."
        )

    @staticmethod
    def _load_db():
        try:
            extensions = importlib.import_module("app.extensions")
            return getattr(extensions, "db", None)
        except ImportError:
            return None

    def setUp(self):
        self.app.config.update(TESTING=True)
        self.client = self.app.test_client()
        self.db = type(self).db

        self.sample_customers = None
        self.sample_inventory = None
        self.sample_mechanics = None
        self.sample_tickets = None
        self.sample_mechanics_with_tickets = None
        self.sample_tickets_with_parts = None
        self.sample_tickets_with_mechanics = None
        self.sample_users = None
        self.auth_token = None
        self.expired_token = "expired_token"
        self.auth_token_no_customer = "invalid_token"

        if self.db is not None and self.app.config.get("TEST_RECREATE_DB", True):
            try:
                with self.app.app_context():
                    self.db.session.remove()
                    self.db.drop_all()
                    self.db.create_all()
            except Exception:
                pass
        self.auth_token = self._login_for_token(
            "user1@example.com", "password123"
        )

    def tearDown(self):
        if self.db is not None:
            try:
                with self.app.app_context():
                    self.db.session.remove()
            except Exception:
                pass

    def _login_for_token(self, email, password):
        try:
            response = self.client.post(
                "/users/login",
                json={"email": email, "password": password},
            )
            if response.status_code == 200:
                data = response.get_json(silent=True) or {}
                return data.get("auth_token")
        except Exception:
            pass
        return None