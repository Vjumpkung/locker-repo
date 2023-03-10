from fastapi import APIRouter, Body, HTTPException
from config import database
import datetime
from router import cost
from router.body_template import Reservation
from math import ceil

router = APIRouter(prefix="/locker", tags=["locker"])
cur = database.client["exceed06"]["Locker"]


@router.get("/")
def get_all_locker():
    t = list(cur.find({}, {"_id": 0}))
    lst = []
    for i in t:
        dic = {}
        dic["locker_id"] = i["locker_id"]
        dic["is_available"] = i["is_available"]
        if not i["is_available"]:
            current_time = datetime.datetime.now()
            end_time = i["time_end"]
            if end_time >= current_time:
                dic["time_left"] = str(end_time - current_time).split(".")[0]
            else:
                dic["time_left"] = (
                    "late : " + str(current_time - end_time).split(".")[0]
                )
        lst.append(dic)

    return lst


@router.post("/reserve")
def reserve_locker(reservation: Reservation):
    locker_id = reservation.locker_id
    locker = cur.find_one({"locker_id": reservation.locker_id})
    if locker_id not in range(1, 7):
        raise HTTPException(status_code=400, detail="Locker id must be in range 1-6.")
    if locker["is_available"]:
        if len(reservation.contain) == 0:
            raise HTTPException(
                status_code=400,
                detail="You must put at least 1 belonging in the locker.",
            )
        if reservation.hour < 0 or reservation.minute < 0:
            raise HTTPException(
                status_code=400, detail="Hour and minute can not be negative."
            )
        if reservation.hour == 0 and reservation.minute == 0:
            raise HTTPException(
                status_code=400, detail="The duration must be more than 0"
            )
        expected_duration = datetime.timedelta(
            hours=reservation.hour, minutes=reservation.minute
        )
        if expected_duration > datetime.timedelta(hours=2):
            time_diff = expected_duration - datetime.timedelta(hours=2)
            cost = ceil(time_diff.total_seconds() / 3600) * 5
        else:
            cost = 0
        cur.update_many(
            {"locker_id": locker_id},
            {
                "$set": {
                    "std_id": reservation.std_id,
                    "time_start": datetime.datetime.now(),
                    "time_end": datetime.datetime.now() + expected_duration,
                    "is_available": False,
                    "contain": reservation.contain,
                    "cost": cost,
                }
            },
        )
        return f"Your reservation is done! You will have to pay {cost} baht when picking up your belonging."
    else:
        raise HTTPException(status_code=400, detail="Sorry, Locker is not available.")


@router.post("/remove/{locker_id}")
def remove_locker_reservation(
    locker_id: int, client_money: int = Body(embed=True), std_id: int = Body(embed=True)
):
    filter_update = {"locker_id": locker_id, "is_available": False, "std_id": std_id}
    removed_locker = cur.find_one(filter_update)
    if removed_locker == None:
        raise HTTPException(400, detail="Invalid std_id")
    temp_bag = removed_locker["contain"]
    update = {
        "$set": {
            "std_id": None,
            "is_available": True,
            "time_start": None,
            "time_end": None,
            "cost": None,
            "contain": [],
        }
    }
    temp_bill = cost.check_bill(locker_id)
    if client_money < temp_bill:
        raise HTTPException(status_code=400, detail="Not enough money.")
    if client_money > temp_bill >= 0:
        cur.update_one(filter_update, update)
        return {"Item_removed": temp_bag, "Change": client_money - temp_bill}
    else:
        cur.update_one(filter_update, update)
        return {"Item_removed": temp_bag}
