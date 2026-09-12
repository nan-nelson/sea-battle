from uuid import UUID

from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models import Game
from placement import validate_fleet


client = TestClient(app)


def test_create_game_has_no_request_body():
    openapi = app.openapi()

    game_endpoint = openapi["paths"]["/game"]["post"]

    assert "requestBody" not in game_endpoint


def test_create_game_response_matches_contract():
    openapi = app.openapi()

    game_endpoint = openapi["paths"]["/game"]["post"]

    response_schema = (
        game_endpoint["responses"]["201"]["content"]["application/json"]["schema"]
    )

    assert response_schema["$ref"] == "#/components/schemas/GameResponse"


def test_game_response_contains_contract_fields():
    openapi = app.openapi()

    schemas = openapi["components"]["schemas"]
    game_response = schemas["GameResponse"]

    assert game_response["required"] == ["session_id", "ships"]
    assert "session_id" in game_response["properties"]
    assert "ships" in game_response["properties"]


def test_create_game_returns_valid_game():
    response = client.post("/game")

    assert response.status_code == 201

    data = response.json()

    assert "session_id" in data
    assert "ships" in data

    UUID(data["session_id"])

    ships = [
        ship["coordinates"]
        for ship in data["ships"]
    ]

    assert len(ships) == 10
    assert validate_fleet(ships)


def test_create_game_saved_to_database():
    response = client.post("/game")

    assert response.status_code == 201

    data = response.json()
    session_id = UUID(data["session_id"])

    db = SessionLocal()

    try:
        game = db.get(Game, session_id)

        assert game is not None
        assert game.session_id == session_id
        assert game.ships == data["ships"]
    finally:
        db.close()


def test_create_game_creates_unique_sessions():
    first_response = client.post("/game")
    second_response = client.post("/game")

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_session_id = first_response.json()["session_id"]
    second_session_id = second_response.json()["session_id"]

    assert first_session_id != second_session_id