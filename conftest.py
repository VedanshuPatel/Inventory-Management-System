from contextlib import closing
import pytest
from inventory_db import connect, init_db
from seed_db import load_seed

@pytest.fixture
def conn():
    """Open an in-memory DB via connect(), with schema loaded."""
    with closing(connect(":memory:")) as connection:
        init_db(connection)
        yield connection

@pytest.fixture
def seeded_conn(conn):
    """Same as conn, with sample data loaded."""
    load_seed(conn)
    return conn