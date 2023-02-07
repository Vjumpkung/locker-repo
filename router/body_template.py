from pydantic import BaseModel


class Locker(BaseModel):
    locker_id: int
    is_available: bool = True


class Customer(BaseModel):
    std_id: int
    contain: str
    time_start: int
    time_end: int
    cost: int = 0
