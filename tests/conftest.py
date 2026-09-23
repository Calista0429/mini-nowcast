import pytest

from assistant import db


@pytest.fixture
def needs_db():
    if not db.DB_PATH.exists():
        pytest.skip("run `make ingest build` first")
