from fastapi import APIRouter
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
