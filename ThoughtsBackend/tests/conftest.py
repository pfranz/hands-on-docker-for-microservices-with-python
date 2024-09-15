
import http.client

import pytest
from faker import Faker

from thoughts_backend import token_validation
from thoughts_backend.app import create_app

from .constants import PRIVATE_KEY

fake = Faker()

@pytest.fixture
def app():
    application = create_app()

    application.app_context().push()
    application.db.create_all()

    return application

@pytest.fixture
def thought_fixture(client):

    thought_ids = []
    for _ in range(3):
        thought = {
                "text": fake.text(240),
                }
        header = token_validation.generate_token_header(fake.name(), PRIVATE_KEY)
        headers = { "Authorization": header, }
        response = client.post("/api/me/thoughts/", data=thought, headers=headers)
        assert response.status_code == http.client.CREATED
        result = response.json
        thought_ids.append(result["id"])

    yield thought_ids

    response = client.get("/api/thoughts/")
    thoughts = response.json
    for thought in thoughts:
        thought_id = thought["id"]
        url = f"/admin/thoughts/{thought_id}/"
        response = client.delete(url)
        assert response.status_code == http.client.NO_CONTENT
