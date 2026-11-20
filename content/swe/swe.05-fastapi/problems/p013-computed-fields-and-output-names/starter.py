from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field

app = FastAPI()


class Line(BaseModel):
    name: str
    price_paise: int = Field(ge=0)
    qty: int = Field(ge=1)


class Order(BaseModel):
    items: list[Line]
    coupon: str | None = None
    created_at: datetime            # TODO: written out as "createdAt"

    # TODO: a computed field total_paise


def to_api(order: Order) -> dict:
    return order.model_dump()       # TODO: JSON values, output names, no None


@app.post("/orders/preview")        # TODO: leave out None values
def preview(order: Order) -> Order:
    return order
