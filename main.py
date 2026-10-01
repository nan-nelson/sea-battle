import random
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Game
from placement import (
    FIELD_COLUMNS,
    FIELD_ROWS,
    generate_fleet,
    is_valid_coordinate,
)


app = FastAPI()

def get_shot_neighbours(coordinate):
    column = ord(coordinate[0]) - ord("A")
    row = int(coordinate[1:]) - 1

    neighbours = []

    for column_offset, row_offset in (
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ):
        neighbour_column = column + column_offset
        neighbour_row = row + row_offset

        if 0 <= neighbour_column < 10 and 0 <= neighbour_row < 10:
            neighbours.append(
                chr(ord("A") + neighbour_column)
                + str(neighbour_row + 1)
            )

    return neighbours

def get_directional_shot(
    first_coordinate,
    second_coordinate,
    available_coordinates,
):
    first_column = ord(first_coordinate[0])
    first_row = int(first_coordinate[1:])

    second_column = ord(second_coordinate[0])
    second_row = int(second_coordinate[1:])

    column_direction = second_column - first_column
    row_direction = second_row - first_row

    candidates = [
        (
            second_column + column_direction,
            second_row + row_direction,
        ),
        (
            first_column - column_direction,
            first_row - row_direction,
        ),
    ]

    for column, row in candidates:
        if not ("A" <= chr(column) <= "J"):
            continue

        if not (1 <= row <= 10):
            continue

        coordinate = chr(column) + str(row)

        if coordinate in available_coordinates:
            return coordinate

    return None


def get_active_hit_shots(shots):
    hit_shots = []

    for shot in reversed(shots):
        if shot["result"] == "killed":
            break

        if shot["result"] == "hit":
            hit_shots.append(shot)

    hit_shots.reverse()

    return hit_shots


class Ship(BaseModel):
    coordinates: list[str]


class GameResponse(BaseModel):
    session_id: UUID
    ships: list[Ship]


class OpponentShotRequest(BaseModel):
    coordinate: str


class OpponentShotResponse(BaseModel):
    result: str


class ShotResponse(BaseModel):
    coordinate: str


class ShotResultRequest(BaseModel):
    result: str


class ShotResultResponse(BaseModel):
    status: str


@app.post("/game", response_model=GameResponse, status_code=201)
def create_game(db: Session = Depends(get_db)):
    session_id = uuid4()
    fleet = generate_fleet()

    ships = [
        {"coordinates": ship}
        for ship in fleet
    ]

    game = Game(
        session_id=session_id,
        ships=ships,
        hits=[],
        shots=[],
        closed=False,
    )

    db.add(game)
    db.commit()
    db.refresh(game)

    return GameResponse(
        session_id=game.session_id,
        ships=game.ships,
    )


@app.post("/game/{session_id}/close")
def close_game(session_id: UUID, db: Session = Depends(get_db)):
    game = db.get(Game, session_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found",
        )

    if game.closed:
        raise HTTPException(
            status_code=400,
            detail="Game is already closed",
        )

    game.closed = True
    db.commit()

    return {"status": "closed"}

@app.post(
    "/game/{session_id}/shot",
    response_model=ShotResponse,
)
def shot(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    game = db.get(Game, session_id)

    if game.closed:
        raise HTTPException(
            status_code=410,
            detail="Game is already closed",
        )

    all_coordinates = [
        f"{column}{row}"
        for column in FIELD_COLUMNS
        for row in FIELD_ROWS
    ]

    used_coordinates = {
        shot["coordinate"]
        for shot in game.shots
    }

    available_coordinates = [
        coordinate
        for coordinate in all_coordinates
        if coordinate not in used_coordinates
    ]

    if not available_coordinates:
        raise HTTPException(
            status_code=409,
            detail="No available coordinates",
        )

    coordinate = None

    hit_shots = get_active_hit_shots(game.shots)

    if len(hit_shots) >= 2:
        first_hit = hit_shots[-2]["coordinate"]
        second_hit = hit_shots[-1]["coordinate"]

        coordinate = get_directional_shot(
            first_hit,
            second_hit,
            available_coordinates,
        )

    if coordinate is None and hit_shots:
        last_hit = hit_shots[-1]["coordinate"]

        neighbours = get_shot_neighbours(last_hit)

        available_neighbours = [
            neighbour
            for neighbour in neighbours
            if neighbour in available_coordinates
        ]

        if available_neighbours:
            coordinate = random.choice(available_neighbours)

    if coordinate is None:
        coordinate = random.choice(available_coordinates)

    game.shots = [
        *game.shots,
        {
            "coordinate": coordinate,
            "result": None,
        },
    ]

    db.commit()

    return ShotResponse(coordinate=coordinate)


@app.post(
    "/game/{session_id}/shot/result",
    response_model=ShotResultResponse,
)
def shot_result(
    session_id: UUID,
    request: ShotResultRequest,
    db: Session = Depends(get_db),
):
    game = db.get(Game, session_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    if game.closed:
        raise HTTPException(
            status_code=410,
            detail="Game is already closed",
        )


    if request.result not in ("miss", "hit", "killed"):
        raise HTTPException(
            status_code=400,
            detail="Invalid result",
        )

    pending_shot = None

    for shot in reversed(game.shots):
        if shot["result"] is None:
            pending_shot = shot
            break

    if pending_shot is None:
        raise HTTPException(
            status_code=409,
            detail="No pending shot",
        )

    updated_shots = []

    for shot in game.shots:
        if shot["coordinate"] == pending_shot["coordinate"]:
            updated_shots.append(
                {
                    "coordinate": shot["coordinate"],
                    "result": request.result,
                }
            )
        else:
            updated_shots.append(shot)

    game.shots = updated_shots

    db.commit()

    return ShotResultResponse(status="accepted")


@app.post(
    "/game/{session_id}/opponent-shot",
    response_model=OpponentShotResponse,
)
def opponent_shot(
    session_id: UUID,
    request: OpponentShotRequest,
    db: Session = Depends(get_db),
):
    game = db.get(Game, session_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    if game.closed:
        raise HTTPException(
            status_code=410,
            detail="Game is already closed",
        )


    if not is_valid_coordinate(request.coordinate):
        raise HTTPException(
            status_code=400,
            detail="Invalid coordinate",
        )

    hit_ship = None

    for ship in game.ships:
        if request.coordinate in ship["coordinates"]:
            hit_ship = ship
            break

    if hit_ship is None:
        return OpponentShotResponse(result="miss")

    game.hits = [*game.hits, request.coordinate]

    if all(
        coordinate in game.hits
        for coordinate in hit_ship["coordinates"]
    ):
        result = "killed"
    else:
        result = "hit"

    db.commit()

    return OpponentShotResponse(result=result)