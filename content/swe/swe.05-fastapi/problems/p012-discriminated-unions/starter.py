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


# TODO: a plain union tries all three models and reports every failure.
# Make it a discriminated union on the field "method".
Payment = Card | Bank | Upi


@app.post("/payments", status_code=201)
def pay(payment: Payment):
    # TODO: the summary text for each kind of payment
    return {"method": payment.method, "amount_paise": payment.amount_paise, "summary": ""}
