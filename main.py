from uuid import UUID, uuid4

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Game


app = FastAPI()


class GameResponse(BaseModel):
    session_id: UUID


@app.post("/game", response_model=GameResponse)
def create_game(db: Session = Depends(get_db)):
    game = Game(session_id=uuid4())

    db.add(game)
    db.commit()
    db.refresh(game)

    return GameResponse(session_id=game.session_id)