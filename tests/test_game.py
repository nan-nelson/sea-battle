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


def test_opponent_shot_returns_miss ():
    response = client.post("/game")
    
    assert response.status_code == 201

    data = response.json()
    session_id = data["session_id"]

    occupied_cells = {
        coordinate
        for ship in data["ships"]
        for coordinate in ship["coordinates"]
    }

    all_cells = {
        f"{column}{row}"
        for column in "ABCDEFGHIJ"
        for row in range(1, 11)
    }

    miss_coordinate = next(
        coordinate
        for coordinate in all_cells
        if coordinate not in occupied_cells
    )

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": miss_coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "miss"}


def test_opponent_shot_returns_hit():
    response = client.post("/game")

    assert response.status_code == 201

    data = response.json()
    session_id = data["session_id"]

    ship = next(
        ship
        for ship in data["ships"]
        if len(ship["coordinates"]) == 2
    )

    coordinate = ship["coordinates"][0]

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "hit"}


def test_opponent_shot_returns_killed():
    response = client.post("/game")

    assert response.status_code == 201

    data = response.json()
    session_id = data["session_id"]

    ship = next(
        ship
        for ship in data["ships"]
        if len(ship["coordinates"]) == 2
    )

    first_coordinate = ship["coordinates"][0]
    second_coordinate = ship["coordinates"][1]

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": first_coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "hit"}

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": second_coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "killed"}


def test_opponent_shot_rejects_invalid_coordinate():
    response = client.post("/game")

    assert response.status_code == 201

    session_id = response.json()["session_id"]

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": "Z99"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid coordinate"}


def test_opponent_shot_returns_404_for_unknown_session():
    unknown_session_id = "550e8400-e29b-41d4-a716-446655440000"

    response = client.post(
        f"/game/{unknown_session_id}/opponent-shot",
        json={"coordinate": "A1"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_opponent_shot_saves_hit_to_database():
    response = client.post("/game")

    assert response.status_code == 201

    data = response.json()
    session_id = UUID(data["session_id"])

    ship = next(
        ship
        for ship in data["ships"]
        if len(ship["coordinates"]) == 2
    )

    coordinate = ship["coordinates"][0]

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "hit"}

    db = SessionLocal()

    try:
        game = db.get(Game, session_id)

        assert game is not None
        assert coordinate in game.hits
    finally:
        db.close()


def test_opponent_shot_kills_ship_only_after_all_cells_are_hit():
    response = client.post("/game")

    assert response.status_code == 201

    data = response.json()
    session_id = data["session_id"]

    ship = next(
        ship
        for ship in data["ships"]
        if len(ship["coordinates"]) == 3
    )

    first_coordinate = ship["coordinates"][0]
    second_coordinate = ship["coordinates"][1]
    third_coordinate = ship["coordinates"][2]

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": first_coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "hit"}

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": second_coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "hit"}

    response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": third_coordinate},
    )

    assert response.status_code == 200
    assert response.json() == {"result": "killed"}