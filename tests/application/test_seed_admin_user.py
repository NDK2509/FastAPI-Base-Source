from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError

from application.use_cases.login_usecase import LoginUseCase
from application.use_cases.seed_admin_user_usecase import SeedAdminUserUseCase
from conftest import build_settings
from core.environment_setting import Settings
from domain.entities import UserEntity
from infrastructure.security.password_hasher import PasswordHasher
import main as main_module
from presentation.api.v1.auth.auth_schemas import LoginSchema


class _InMemoryUserRepo:
    def __init__(self):
        self.users: dict[str, UserEntity] = {}

    def get_by_username(self, username: str) -> UserEntity | None:
        return self.users.get(username)

    def create(self, user: UserEntity) -> UserEntity:
        self.users[user.username] = user
        return user


class TestSeedAdminUserUseCase:
    def test_creates_admin_with_hashed_password_and_allows_login(self, monkeypatch):
        repo = _InMemoryUserRepo()
        session = MagicMock()

        use_case = SeedAdminUserUseCase(session)
        monkeypatch.setattr(use_case, "user_repository", repo)

        created = use_case.invoke(" admin ", "admin1234")
        assert created is not None
        assert created.username == "admin"
        assert created.first_name == "System"
        assert created.last_name == "Admin"
        assert created.password != "admin1234"
        assert PasswordHasher.verify("admin1234", created.password)

        login_use_case = LoginUseCase(session)
        monkeypatch.setattr(login_use_case, "user_repository", repo)
        logged_in = login_use_case.invoke(
            LoginSchema(username="admin", password="admin1234")
        )
        assert logged_in is created

        wrong_login = login_use_case.invoke(
            LoginSchema(username="admin", password="wrong-password")
        )
        assert wrong_login is None

    def test_is_idempotent_when_admin_already_exists(self, monkeypatch):
        repo = _InMemoryUserRepo()
        existing = UserEntity(
            first_name="Existing",
            last_name="Admin",
            username="admin",
            password=PasswordHasher.hash("existing-secret"),
        )
        repo.create(existing)

        use_case = SeedAdminUserUseCase(MagicMock())
        monkeypatch.setattr(use_case, "user_repository", repo)

        result = use_case.invoke("admin", "new-password")
        assert result is existing
        assert len(repo.users) == 1
        assert PasswordHasher.verify("existing-secret", result.password)

    def test_skips_when_username_or_password_blank(self, monkeypatch):
        repo = _InMemoryUserRepo()
        use_case = SeedAdminUserUseCase(MagicMock())
        monkeypatch.setattr(use_case, "user_repository", repo)

        assert use_case.invoke("   ", "admin1234") is None
        assert use_case.invoke("admin", "") is None
        assert repo.users == {}


class TestSeedInitialAdminStartup:
    def test_settings_loads_admin_credentials_as_secret(self, monkeypatch):
        monkeypatch.setenv("ADMIN_USERNAME", "superadmin")
        monkeypatch.setenv("ADMIN_PASSWORD", "supersecret123")
        settings = Settings(_env_file=None)

        assert settings.admin_username == "superadmin"
        assert settings.admin_password is not None
        assert settings.admin_password.get_secret_value() == "supersecret123"
        assert "supersecret123" not in repr(settings)

    def test_skips_when_admin_credentials_missing_or_partial(self):
        called = False

        def failing_factory():
            nonlocal called
            called = True
            yield MagicMock()

        main_module.seed_initial_admin(build_settings(), session_factory=failing_factory)
        main_module.seed_initial_admin(
            build_settings(admin_username="admin", admin_password=None),
            session_factory=failing_factory,
        )
        main_module.seed_initial_admin(
            build_settings(admin_username=None, admin_password="admin1234"),
            session_factory=failing_factory,
        )
        assert called is False

    def test_calls_seed_use_case_when_configured(self, monkeypatch):
        invoked_with = []
        fake_session = MagicMock()
        fake_session.__enter__.return_value = fake_session
        fake_session.__exit__.return_value = False

        def fake_factory():
            yield fake_session

        class FakeUseCase:
            def __init__(self, session):
                assert session is fake_session

            def invoke(self, username: str, password: str):
                invoked_with.append((username, password))
                return UserEntity(
                    first_name="System",
                    last_name="Admin",
                    username=username,
                    password="hashed",
                )

        monkeypatch.setattr(main_module, "SeedAdminUserUseCase", FakeUseCase)

        main_module.seed_initial_admin(
            build_settings(admin_username="admin", admin_password="admin1234"),
            session_factory=fake_factory,
        )
        assert invoked_with == [("admin", "admin1234")]

    def test_handles_database_errors_gracefully(self):
        def broken_factory():
            raise OperationalError("SELECT 1", {}, Exception("db down"))
            yield  # pragma: no cover

        main_module.seed_initial_admin(
            build_settings(admin_username="admin", admin_password="admin1234"),
            session_factory=broken_factory,
        )
