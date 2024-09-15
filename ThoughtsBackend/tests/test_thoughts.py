"""Test the Thoughts operations.

Use the thought_fixture to have data to retrieve, it generates three thoughts
"""

import http.client
from unittest.mock import ANY

from faker import Faker
from freezegun import freeze_time

from thoughts_backend import token_validation

from .constants import PRIVATE_KEY

fake = Faker()

@freeze_time("2019-05-07 13:47:34")
def test_create_me_thought(client):
    new_thought = {
        "username": fake.name(),
        "text": fake.text(240),
    }
    header = token_validation.generate_token_header(fake.name(), PRIVATE_KEY)
    headers = { "Authorization": header }
    response = client.post("/api/me/thoughts/", data=new_thought, headers=headers)
    result = response.json

    assert response.status_code == http.client.CREATED

    expected = {
        "id": ANY,
        "username": ANY,
        "text": new_thought["text"],
        "timestamp": "2019-05-07T13:47:34",
    }
    assert result == expected

def test_create_me_unauthorized(client):
    new_thought = {
        "username": fake.name(),
        "text": fake.text(240),
    }
    response = client.post("/api/me/thoughts/", data=new_thought)
    assert response.status_code == http.client.UNAUTHORIZED

def test_list_me_thoughts(client, thought_fixture):
    username = fake.name()
    text = fake.text(240)

    # Create a new thought
    new_thought = { "text": text }
    header = token_validation.generate_token_header(username, PRIVATE_KEY)
    headers = { "Authorization": header }
    response = client.post("/api/me/thoughts/", data=new_thought, headers=headers)
    result = response.json

    assert response.status_code == http.client.CREATED

    # Get thoughts of the user
    response = client.get("/api/me/thoughts/", headers=headers)
    results = response.json

    assert response.status_code == http.client.OK
    assert len(results) == 1
    result = results[0]
    expected_result = {
            "id": ANY,
            "username": username,
            "text": text,
            "timestamp": ANY,
            }
    assert result == expected_result

def test_list_me_unauthorized(client):
    response = client.get("/api/me/thoughts/")
    assert response.status_code == http.client.UNAUTHORIZED

def test_list_thoughts(client, thought_fixture):
    response = client.get("/api/thoughts/")
    result = response.json

    assert response.status_code == http.client.OK
    assert len(result) > 0

    # Check that ids are incrementing
    previous_id = -1
    for thought in result:
        expected = {
            "text": ANY,
            "username": ANY,
            "id": ANY,
            "timestamp": ANY,
        }
        assert expected == thought
        assert thought["id"] > previous_id
        previous_id = thought["id"]

def test_list_thoughts_search(client, thought_fixture):
    username = fake.name()
    new_thought = {
        "username": username,
        "text": "A tale about a Platypus"
    }
    header = token_validation.generate_token_header(username, PRIVATE_KEY)
    headers = { "Authorization": header }
    response = client.post("/api/me/thoughts/", data=new_thought, headers=headers)
    assert response.status_code == http.client.CREATED

    response = client.get("/api/thoughts/?search=platypus")
    result = response.json

    assert response.status_code == http.client.OK
    assert len(result) > 0

    for thought in result:
        expected = {
            "text": ANY,
            "username": username,
            "id": ANY,
            "timestamp": ANY,
        }
        assert expected == thought
        assert "platypus" in thought["text"].lower()


def test_get_non_existing_thought(client, thought_fixture):
    thought_id = 123456
    response = client.get(f"/api/thoughts/{thought_id}/")

    assert response.status_code == http.client.NOT_FOUND
