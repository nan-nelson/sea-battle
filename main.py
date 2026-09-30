from uuid import UUID

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Ship(BaseModel):
    coordinates: list[str]


class GameResponse(BaseModel):
    session_id: UUID
    ships: list[Ship]


@app.post("/game", response_model=GameResponse, status_code=201)
def create_game():
    raise RuntimeError("Game creation is not implemented yet")