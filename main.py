from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Game
from placement import generate_fleet, is_valid_coordinate


app = FastAPI()


class Ship(BaseModel):
    coordinates: list[str]


class GameResponse(BaseModel):
    session_id: UUID
    ships: list[Ship]

class OpponentShotRequest(BaseModel):
    coordinate: str


class OpponentShotResponse(BaseModel):
    result: str


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
    )

    db.add(game)
    db.commit()
    db.refresh(game)

    return GameResponse(
        session_id=game.session_id,
        ships=game.ships,
    )

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