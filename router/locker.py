from fastapi import APIRouter, Body, HTTPException
from config import database
import datetime
from router import cost
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
            raise HTTPException(status_code=400, detail="You must put at least 1 belonging in the locker.")
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
        return "Your reservation is done!"
    else:
        raise HTTPException(status_code=400, detail="Sorry, Locker is not available.")


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
