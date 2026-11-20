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
    created_at: datetime = Field(serialization_alias="createdAt")

    @computed_field
    @property
    def total_paise(self) -> int:
        return sum(line.price_paise * line.qty for line in self.items)


def to_api(order: Order) -> dict:
    return order.model_dump(mode="json", by_alias=True, exclude_none=True)


@app.post("/orders/preview", response_model_exclude_none=True)
def preview(order: Order) -> Order:
    return order
