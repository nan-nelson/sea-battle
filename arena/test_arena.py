import pytest

from arena.main import play_turn


def test_play_turn_rejects_invcorrect_result(monkeypatch):
    game = {
        "ships": [
            {"coordinates": ["A1"]},
        ]
    }

    monkeypatch.setattr(
        "arena.main.make_shot",
        lambda *args: {"coordinate": "A1"},
    )

    monkeypatch.setattr(
        "arena.main.send_opponent_shot",
        lambda *args: {"result": "miss"},
    )

    with pytest.raises(
        ValueError,
        match="Service returned incorrect result",
    ):
        play_turn(
           "service_a",
           "session_a",
           "service_b",
           "session_b",
           game,
           set(),
        )


def test_play_turn_rejects_invalid_result(monkeypatch):
    game = {
        "ships": [
            {"coordinates": ["A1"]},
        ]
    }

    monkeypatch.setattr(
        "arena.main.make_shot",
        lambda *args: {"coordinate": "A1"},
    )

    monkeypatch.setattr(
        "arena.main.send_opponent_shot",
        lambda *args: {"result": "invalid"},
    )

    with pytest.raises(
        ValueError,
        match="Service returned invalid result",
    ):
        play_turn(
           "service_a",
           "session_a",
           "service_b",
           "session_b",
           game,
           set(),
        )

import httpx

from arena.main import make_shot


def test_make_shot_timeout(monkeypatch):
    def fake_post(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(
        ValueError,
        match="Service timeout",
    ):
        make_shot(
            "http://test",
            "session-id",
        )


def test_make_shot_http_error(monkeypatch):
    response = httpx.Response(
        500,
        request=httpx.Request(
            "POST",
            "http://test",
        ),
    )

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(
        ValueError,
        match="Service error",
    ):
        make_shot(
            "http://test",
            "session-id",
        )


def test_create_game_rejects_invalid_fleet(monkeypatch):
    response = httpx.Response(
        200,
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "ships": [
                {"coordinates": ["A1", "B1", "C1", "D1"]},
            ],
        },
        request=httpx.Request(
            "POST",
            "http://test",
        ),
    )

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "post", fake_post)

    from arena.main import create_game

    with pytest.raises(
        ValueError,
        match="Invalid fleet",
    ):
        create_game("http://test")


def test_create_game_rejects_invalid_json(monkeypatch):
    response = httpx.Response(
        200,
        content=b"invalid json",
        request=httpx.Request(
            "POST",
            "http://test",
        ),
    )

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "post", fake_post)

    from arena.main import create_game

    with pytest.raises(
        ValueError,
        match="Invalid service response",
    ):
        create_game("http://test")


def test_create_game_rejects_missing_fields(monkeypatch):
    response = httpx.Response(
        200,
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
        },
        request=httpx.Request(
            "POST",
            "http://test",
        ),
    )

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "post", fake_post)

    from arena.main import create_game

    with pytest.raises(
        ValueError,
        match="Invalid service response",
    ):
        create_game("http://test")


def test_create_game_rejects_invalid_ships_type(monkeypatch):
    response = httpx.Response(
        200,
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "ships": "not a list",
        },
        request=httpx.Request(
            "POST",
            "http://test",
        ),
    )

    def fake_post(*args, **kwargs):
        return response

    monkeypatch.setattr(httpx, "post", fake_post)

    from arena.main import create_game

    with pytest.raises(
        ValueError,
        match="Invalid service response",
    ):
        create_game("http://test")


def test_create_game_rejects_missing_coordinates(monkeypatch):
    game = {"ships": [{"coordinates": ["A1"]}]}

    monkeypatch.setattr(
        "arena.main.make_shot",
        lambda *args: {},
    )

    with pytest.raises(ValueError, match="Invalid service response"):
        play_turn(
            "service_a",
            "session_a",
            "service_b",
            "session_b",
            game,
            set(),
        )


def test_play_turn_rejects_numeric_coordinates(monkeypatch):
    monkeypatch.setattr(
        "arena.main.make_shot",
        lambda *args: {"coordinate": 123},
    )

    with pytest.raises(
        ValueError, 
        match="Invalid service response",
    ):
        play_turn(
            "service_a",
            "session_a",
            "service_b",
            "session_b",
            {"ships": [{"coordinates": ["A1"]}]},
            set(),
        )


def test_play_turn_rejects_out_of_bounds_coordinates(monkeypatch):
    monkeypatch.setattr(
        "arena.main.make_shot",
        lambda *args: {"coordinate": "K11"},
    )

    with pytest.raises(
        ValueError, 
        match="Invalid service response",
    ):
        play_turn(
            "service_a",
            "session_a",
            "service_b",
            "session_b",
            {"ships": [{"coordinates": ["A1"]}]},
            set(),
        )