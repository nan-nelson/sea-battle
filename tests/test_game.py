from main import app
from fastapi.testclient import TestClient


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