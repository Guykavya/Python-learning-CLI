from typing import Annotated, Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class PaymentBase(BaseModel):
    amount_paise: int = Field(gt=0)


class Card(PaymentBase):
    method: Literal["card"]
    number: str = Field(pattern=r"^\d{16}$")
    expiry: str = Field(pattern=r"^(0[1-9]|1[0-2])/\d{2}$")


class Bank(PaymentBase):
    method: Literal["bank"]
    account: str = Field(pattern=r"^\d{9,18}$")
    ifsc: str = Field(pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")


class Upi(PaymentBase):
    method: Literal["upi"]
    vpa: str = Field(pattern=r"^[a-z0-9._-]+@[a-z]+$")


Payment = Annotated[Card | Bank | Upi, Field(discriminator="method")]


def summary(payment) -> str:
    if isinstance(payment, Card):
        return "card ending " + payment.number[-4:]
    if isinstance(payment, Bank):
        return "bank " + payment.ifsc
    return "upi " + payment.vpa


@app.post("/payments", status_code=201)
def pay(payment: Payment):
    return {"method": payment.method, "amount_paise": payment.amount_paise, "summary": summary(payment)}
