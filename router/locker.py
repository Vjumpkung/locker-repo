from fastapi import APIRouter, Body
from config import database
import datetime

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


@router.post("/remove/{std_id}")
def remove_locker_reservation(std_id: int):
    filter_update = {"std_id": std_id, "is_available": False}
    removed_locker = cur.find_one(filter_update)
    temp_bag = removed_locker["contain"]
    update = {"$set": {"std_id": None,
                       "is_available": True,
                       "time_start": None,
                       "time_end": None,
                       "cost": None,
                       "contain": []}}
    cur.update_one(filter_update, update)
    return temp_bag
