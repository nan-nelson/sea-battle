from uuid import uuid4

from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models import Game


client = TestClient(app)


def test_create_game():
    game_id = str(uuid4())

    response = client.post(
        "/game",
        json={
            "game_id": game_id,
            "ships": [
                {
                    "coordinates": ["A1", "A2", "A3", "A4"]
                },
                {
                    "coordinates": ["C1", "D1", "E1"]
                }
            ]
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "is_firstshot" in data
    assert isinstance(data["is_firstshot"], bool)


def test_create_game_saved_to_database():
    game_id = uuid4()

    ships = [
        {
            "coordinates": ["A1", "A2", "A3", "A4"]
        },
        {
            "coordinates": ["C1", "D1", "E1"]
        }
    ]

    response = client.post(
        "/game",
        json={
            "game_id": str(game_id),
            "ships": ships,
        },
    )

    assert response.status_code == 201

    db = SessionLocal()

    try:
        game = db.get(Game, game_id)

        assert game is not None
        assert game.game_id == game_id
        assert game.ships == ships
    finally:
        db.close()


def test_create_game_duplicate_id():
    game_id = uuid4()

    ships = [
        {
            "coordinates": ["A1", "A2", "A3", "A4"]
        },
        {
            "coordinates": ["C1", "D1", "E1"]
        }
    ]

    first_response = client.post(
        "/game",
        json={
            "game_id": str(game_id),
            "ships": ships,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/game",
        json={
            "game_id": str(game_id),
            "ships": ships,
        },
    )

    assert second_response.status_code == 409
def test_create_game_invalid_request():
    response = client.post(
        "/game",
        json={
            "ships": [
                {
                    "coordinates": ["A1", "A2", "A3", "A4"]
                }
            ]
        },
    )

    assert response.status_code == 422
