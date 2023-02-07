from fastapi import APIRouter, Body
from config import database
import datetime
from router import cost

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


@router.post("/remove/{std_id}")
def remove_locker_reservation(std_id: int, client_money: int = Body(embed=True)):
    filter_update = {"std_id": std_id, "is_available": False}
    removed_locker = cur.find_one(filter_update)
    temp_bag = removed_locker["contain"]
    temp_locker = removed_locker["locker_id"]
    update = {"$set": {"std_id": None,
                       "is_available": True,
                       "time_start": None,
                       "time_end": None,
                       "cost": None,
                       "contain": []}}
    temp_bill = cost.check_bill(temp_locker)
    if client_money > temp_bill > 0:
        cur.update_one(filter_update, update)
        return {
            "Item_removed": temp_bag,
            "Change": client_money - temp_bill
        }
    else:
        cur.update_one(filter_update, update)
        return {
            "Item_removed": temp_bag
        }
