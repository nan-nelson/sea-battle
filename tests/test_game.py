from uuid import UUID

from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models import Game


client = TestClient(app)


def test_create_game():
    response = client.post("/game")

    assert response.status_code == 200

    data = response.json()

    assert "session_id" in data
    assert data["session_id"] is not None


def test_create_game_saved_to_database():
    response = client.post("/game")

    assert response.status_code == 200

    session_id = UUID(response.json()["session_id"])

    db = SessionLocal()

    try:
        game = db.get(Game, session_id)

        assert game is not None
        assert game.session_id == session_id
    finally:
        db.close()