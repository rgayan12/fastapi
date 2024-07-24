import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..main import app
from dotenv import load_dotenv

load_dotenv()
client = TestClient(app)


# @patch('pika.BlockingConnection')
def test_read_item():
    response = client.get("/mailchimp/ping", headers={"Access-Token": os.getenv('FAST_API_ACCESS_TOKEN')})
    assert response.status_code == 200
    # assert response.json() == {
    #     "id": "foo",
    #     "title": "Foo",
    #     "description": "There goes my hero",
    # }
