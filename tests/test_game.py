from uuid import UUID

from fastapi.testclient import TestClient

from database import SessionLocal
from main import app, get_active_hit_shots
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


def test_shot_returns_valid_coordinate():
    response = client.post("/game")

    assert response.status_code == 201

    session_id = response.json()["session_id"]

    response = client.post(
        f"/game/{session_id}/shot",
    )

    assert response.status_code == 200

    coordinate = response.json()["coordinate"]

    assert coordinate[0] in "ABCDEFGHIJ"
    assert 1 <= int(coordinate[1:]) <= 10


def test_shot_does_not_repeat_coordinate():
    response = client.post("/game")

    assert response.status_code == 201

    session_id = response.json()["session_id"]

    first_response = client.post(
        f"/game/{session_id}/shot",
    )

    second_response = client.post(
        f"/game/{session_id}/shot",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_coordinate = first_response.json()["coordinate"]
    second_coordinate = second_response.json()["coordinate"]

    assert first_coordinate != second_coordinate


def test_shot_result_accepts_miss():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    shot_response = client.post(f"/game/{session_id}/shot")
    assert shot_response.status_code == 200

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "miss"},
    )

    assert result_response.status_code == 200
    assert result_response.json() == {"status": "accepted"}


def test_shot_result_accepts_hit():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    shot_response = client.post(f"/game/{session_id}/shot")
    assert shot_response.status_code == 200

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "hit"},
    )

    assert result_response.status_code == 200
    assert result_response.json() == {"status": "accepted"}


def test_shot_result_accepts_killed():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    shot_response = client.post(f"/game/{session_id}/shot")
    assert shot_response.status_code == 200

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "killed"},
    )

    assert result_response.status_code == 200
    assert result_response.json() == {"status": "accepted"}



def test_shot_result_rejects_invalid_result():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    client.post(f"/game/{session_id}/shot")

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "unknown"},
    )

    assert result_response.status_code == 400
    assert result_response.json()["detail"] == "Invalid result"


def test_shot_result_without_shot_returns_conflict():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "miss"},
    )

    assert result_response.status_code == 409
    assert result_response.json()["detail"] == "No pending shot"

def test_shot_result_is_saved_to_game():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    shot_response = client.post(f"/game/{session_id}/shot")
    assert shot_response.status_code == 200
    coordinate = shot_response.json()["coordinate"]

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "hit"},
    )

    assert result_response.status_code == 200

    game = SessionLocal().get(Game, UUID(session_id))

    assert game is not None
    assert game.shots == [
        {
            "coordinate": coordinate,
            "result": "hit",
        }
    ]

def test_shot_after_hit_targets_neighbour():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    first_shot = client.post(
        f"/game/{session_id}/shot",
    )
    assert first_shot.status_code == 200
    first_coordinate = first_shot.json()["coordinate"]

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "hit"},
    )
    assert result_response.status_code == 200

    second_shot = client.post(
        f"/game/{session_id}/shot",
    )
    assert second_shot.status_code == 200
    second_coordinate = second_shot.json()["coordinate"]

    column = ord(first_coordinate[0]) - ord("A")
    row = int(first_coordinate[1:])

    second_column = ord(second_coordinate[0]) - ord("A")
    second_row = int(second_coordinate[1:])

    column_difference = abs(column - second_column)
    row_difference = abs(row - second_row)

    assert column_difference + row_difference == 1


def test_shot_after_two_hits_continues_direction():
    response = client.post("/game")
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    first_shot = client.post(
        f"/game/{session_id}/shot",
    )
    assert first_shot.status_code == 200
    first_coordinate = first_shot.json()["coordinate"]

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "hit"},
    )
    assert result_response.status_code == 200

    second_shot = client.post(
        f"/game/{session_id}/shot",
    )
    assert second_shot.status_code == 200
    second_coordinate = second_shot.json()["coordinate"]

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "hit"},
    )
    assert result_response.status_code == 200

    third_shot = client.post(
        f"/game/{session_id}/shot",
    )
    assert third_shot.status_code == 200
    third_coordinate = third_shot.json()["coordinate"]

    first_column = ord(first_coordinate[0])
    first_row = int(first_coordinate[1:])

    second_column = ord(second_coordinate[0])
    second_row = int(second_coordinate[1:])

    third_column = ord(third_coordinate[0])
    third_row = int(third_coordinate[1:])

    column_direction = second_column - first_column
    row_direction = second_row - first_row

    assert (
        third_column == second_column + column_direction
        and third_row == second_row + row_direction
    ) or (
        third_column == first_column - column_direction
        and third_row == first_row - row_direction
    )


def test_get_active_hit_shots_resets_after_killed():
    shots = [
        {"coordinate": "D5", "result": "hit"},
        {"coordinate": "D6", "result": "hit"},
        {"coordinate": "D7", "result": "killed"},
        {"coordinate": "A1", "result": "hit"},
    ]

    active_hits = get_active_hit_shots(shots)

    assert active_hits == [
        {"coordinate": "A1", "result": "hit"},
    ]


def test_close_game_returns_closed():
    response = client.post("/game")

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    close_response = client.post(
        f"/game/{session_id}/close",
    )

    assert close_response.status_code == 200
    assert close_response.json() == {"status": "closed"}


def test_close_game_returns_400_when_already_closed():
    response = client.post("/game")

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    first_close = client.post(
        f"/game/{session_id}/close",
    )

    assert first_close.status_code == 200

    second_close = client.post(
        f"/game/{session_id}/close",
    )

    assert second_close.status_code == 400
    assert second_close.json() == {"detail": "Game is already closed"}


def test_close_game_returns_404_for_unknown_session():
    unknown_session_id = "550e8400-e29b-41d4-a716-446655440000"

    response = client.post(
        f"/game/{unknown_session_id}/close",
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


def test_shot_after_game_closed_returns_410():
    response = client.post("/game")

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    close_response = client.post(
        f"/game/{session_id}/close",
    )

    assert close_response.status_code == 200

    shot_response = client.post(
        f"/game/{session_id}/shot",
    )

    assert shot_response.status_code == 410
    assert shot_response.json() == {"detail": "Game is already closed"}


def test_shot_result_after_game_closed_returns_410():
    response = client.post("/game")

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    close_response = client.post(
        f"/game/{session_id}/close",
    )

    assert close_response.status_code == 200

    result_response = client.post(
        f"/game/{session_id}/shot/result",
        json={"result": "miss"},
    )

    assert result_response.status_code == 410
    assert result_response.json() == {"detail": "Game is already closed"}


def test_opponent_shot_after_game_closed_returns_410():
    response = client.post("/game")

    assert response.status_code == 201
    session_id = response.json()["session_id"]

    close_response = client.post(
        f"/game/{session_id}/close",
    )

    assert close_response.status_code == 200

    opponent_shot_response = client.post(
        f"/game/{session_id}/opponent-shot",
        json={"coordinate": "A1"},
    )

    assert opponent_shot_response.status_code == 410
    assert opponent_shot_response.json() == {
        "detail": "Game is already closed"
    }