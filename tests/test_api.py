from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module


_original_snapshot = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the original in-memory activities before each test
    app_module.activities.clear()
    app_module.activities.update(deepcopy(_original_snapshot))
    yield
    # Tear down: restore original snapshot after test as well
    app_module.activities.clear()
    app_module.activities.update(deepcopy(_original_snapshot))


client = TestClient(app_module.app)


def test_get_activities():
    # Arrange (fixture already set)
    # Act
    resp = client.get('/activities')
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert 'Chess Club' in data


def test_signup_adds_participant():
    # Arrange
    email = 'tester@example.com'
    # Act
    resp = client.post('/activities/Chess%20Club/signup', params={'email': email})
    # Assert
    assert resp.status_code == 200
    data = client.get('/activities').json()
    assert email in data['Chess Club']['participants']


def test_signup_prevents_duplicate():
    # Arrange
    email = 'duplicate@example.com'
    # Act
    r1 = client.post('/activities/Chess%20Club/signup', params={'email': email})
    r2 = client.post('/activities/Chess%20Club/signup', params={'email': email})
    # Assert
    assert r1.status_code == 200
    assert r2.status_code == 400
    data = client.get('/activities').json()
    assert data['Chess Club']['participants'].count(email) == 1


def test_delete_unregisters_participant():
    # Arrange
    email = 'remove@example.com'
    client.post('/activities/Chess%20Club/signup', params={'email': email})
    # Act
    r = client.delete('/activities/Chess%20Club/signup', params={'email': email})
    # Assert
    assert r.status_code == 200
    data = client.get('/activities').json()
    assert email not in data['Chess Club']['participants']
