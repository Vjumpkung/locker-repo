from fastapi import APIRouter
from config import database
import datetime
from fastapi import FastAPI, HTTPException, Body
from router.body_template import Reservation

router = APIRouter(prefix="/locker", tags=["locker"])
cur = database.client["exceed06"]["Locker"]


@router.get("/")
def get_all_locker():
    t = list(cur.find({}, {"_id": 0}))
    lst = []
    for i in t:
        dic = {}
        dic["locker_id"] = i["locker_id"]
        current_time = datetime.datetime.now()
        end_time = i["time_end"]
        if end_time >= current_time:
            dic["time_left"] = str(end_time - current_time).split(".")[0]
        else:
            dic["time_left"] = "late : " + str(current_time - end_time).split(".")[0]
        lst.append(dic)
    return lst


@router.post("/reserve")
def reserve_locker(reservation: Reservation):
    locker_id = reservation.locker_id
    locker = cur.find_one({"locker_id": reservation.locker_id})
    if locker["is_available"]:
        expected_duration = datetime.timedelta(hours=reservation.hour, minutes=reservation.minute)
        if expected_duration > datetime.timedelta(hours=2):
            time_diff = expected_duration - datetime.timedelta(hours=2)
            cost = time_diff.total_seconds()//60//60 * 5
        else:
            cost = 0
        cur.update_many({"locker_id": locker_id}, {'$set': {"std_id": reservation.std_id,
                                                            "time_start": datetime.datetime.now(),
                                                            "time_end": datetime.datetime.now() + expected_duration,
                                                            "is_available": False,
                                                            "contain": reservation.contain,
                                                            "cost": cost
                                                            }})
    else:
        raise HTTPException(status_code=400, detail="Sorry, Locker is not available.")
