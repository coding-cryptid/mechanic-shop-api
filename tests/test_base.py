import importlib
import unittest

try:
    from flask.testing import FlaskClient
except ImportError: 
    FlaskClient = None


class RedirectFollowingClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs.setdefault("follow_redirects", True)
        return super().open(*args, **kwargs)


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app = cls._load_app()
        cls.db = cls._load_db()

    @staticmethod
    def _load_app():
        errors = []

        for module_name in ("run", "app"):
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                errors.append(f"{module_name}: {exc}")
                continue

            app = getattr(module, "app", None)
            if app is not None and hasattr(app, "test_client"):
                return app

            factory = getattr(module, "create_app", None)
            if callable(factory):
                try:
                    return factory()
                except TypeError:
                    pass
                except Exception as exc:
                    errors.append(f"{module_name}.create_app(): {exc}")

        detail = "; ".join(errors)
        raise ImportError(
            "Could not find the Flask application. "
            "Make sure run.py exposes `app` or `create_app()`. "
            + detail
        )

    @staticmethod
    def _load_db():
        for module_name in ("app.extensions", "app"):
            try:
                module = importlib.import_module(module_name)
                db = getattr(module, "db", None)
                if db is not None:
                    return db
            except Exception:
                continue
        return None

    def setUp(self):
        self.app.config["TESTING"] = True

        self.app.test_client_class = RedirectFollowingClient
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

        self.expired_token = "expired_token"
        self.auth_token_no_customer = "invalid_token"

        self.auth_token = self._login_for_token(
            "user1@example.com",
            "password123",
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
                follow_redirects=True,
            )
            if response.status_code == 200:
                data = response.get_json(silent=True) or {}
                return data.get("auth_token")
        except Exception:
            pass
        return None