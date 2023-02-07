from pydantic import BaseModel


class Reservation(BaseModel):
    std_id: int
    contain: list
    locker_id: int
    hour: int
    minute: int