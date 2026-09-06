from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Game


app = FastAPI()


class Ship(BaseModel):
    coordinates: list[str]


class GameRequest(BaseModel):
    game_id: UUID
    ships: list[Ship]


class GameResponse(BaseModel):
    is_firstshot: bool


@app.post("/game", response_model=GameResponse, status_code=201)
def create_game(request: GameRequest, db: Session = Depends(get_db)):
    game = Game(
        game_id=request.game_id,
        ships=[ship.model_dump() for ship in request.ships],
    )

    try:
        db.add(game)
        db.commit()
        db.refresh(game)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Game with this game_id already exists",
        )

    return GameResponse(is_firstshot=False)