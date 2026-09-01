from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class GameResponse(BaseModel):
    session_id: UUID


@app.post("/game", response_model=GameResponse)
def create_game():
    return GameResponse(session_id=uuid4())