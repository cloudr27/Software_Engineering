import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db  # если Base лежит в app/models.py, поменяй импорт
from app.main import app


@pytest.fixture()
def client():
    # Временная БД в памяти: каждый тест начинается с чистой базы
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    # Справочники и тестовый пользователь, как в SQL-схеме
    db = TestingSession()
    db.add_all([models.Role(name=n) for n in ("user", "agent", "admin")])
    db.add_all([models.Status(name=n) for n in ("Open", "In Progress", "Resolved", "Closed")])
    db.add_all([
        models.Priority(name="Low", sla_hours=72),
        models.Priority(name="Medium", sla_hours=24),
        models.Priority(name="High", sla_hours=8),
        models.Priority(name="Critical", sla_hours=4),
    ])
    db.commit()
    db.add(models.User(username="testuser", email="user@example.com",
                       password_hash="fake_hash_123", role_id=1))
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
