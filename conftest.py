import pytest
from test_api import setup, teardown

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    setup()
    yield
    teardown()
