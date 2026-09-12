from uuid import UUID, uuid4

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Game
from placement import generate_fleet


app = FastAPI()


class Ship(BaseModel):
    coordinates: list[str]


class GameResponse(BaseModel):
    session_id: UUID
    ships: list[Ship]


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
    )

    db.add(game)
    db.commit()
    db.refresh(game)

    return GameResponse(
        session_id=game.session_id,
        ships=game.ships,
    )