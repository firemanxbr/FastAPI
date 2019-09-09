from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    name: str
    email: str
    token: str = None
    max_wallet: int = None
    date_created: datetime = None
    api_response_time: int = None

class Wallet(BaseModel):
    address: str = None
    balance: float = None
    token: str
    user_id: int = None
    date_created: datetime = None
    api_response_time: int = None

class Transaction(BaseModel):
    token: str
    address_income: str
    address_outcome: str
    amount: float
    balance_outcome: float = None
    user_id: int = None
    date_created: datetime = None
    api_response_time: int = None
