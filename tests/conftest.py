import pytest
from fastapi.testclient import TestClient

import data.base as db_base
from main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db_path = tmp_path / "shop_test.db"
    monkeypatch.setattr(db_base, "DB_PATH", test_db_path)
    db_base.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if test_db_path.exists():
        test_db_path.unlink()

    with TestClient(app) as test_client:
        yield test_client

    if test_db_path.exists():
        test_db_path.unlink()
