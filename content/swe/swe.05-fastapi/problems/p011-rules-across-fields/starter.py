from datetime import date
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

MAX_GUESTS = {"single": 2, "double": 4}

app = FastAPI()


class Booking(BaseModel):
    start: date
    end: date
    guests: int = Field(ge=1)
    room: Literal["single", "double"]

    # TODO: one @model_validator(mode="after") with the two rules; return self


@app.post("/bookings", status_code=201)
def book(b: Booking):
    return {"room": b.room, "guests": b.guests, "nights": (b.end - b.start).days}
