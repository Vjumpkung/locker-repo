import datetime
from config import database
from math import ceil

cur = database.client["exceed06"]["Locker"]


def check_bill(locker_id: int) -> int:
    query = list(cur.find({"locker_id": locker_id}, {"_id": 0}))[0]
    now_time = datetime.datetime.now()
    end_time = query["time_end"]
    if end_time >= now_time:
        dt = str(end_time - now_time).split(".")[0]
        return query["cost"]
    else:
        dt = str(now_time - end_time).split(".")[0]
    day_count = 0
    min_count = 0
    if "days" in dt:
        dt = dt.split(",")
        dt = [i.replace("days", "").strip().split(":") for i in dt]
        day_count = int(dt[0][0])
        hr_count = int(dt[1][0])
        min_count = int(dt[1][1])
        sec_count = int(dt[1][2])
    else:
        dt = dt.split(":")
        hr_count = int(dt[0])
        min_count = int(dt[1])
        sec_count = int(dt[2])
    total_min = 0
    total_min += (day_count * 24 * 60) + (hr_count * 60) + min_count
    if sec_count > 0:
        total_min += 1
    if total_min >= 10:
        return query["cost"] + ceil(total_min / 10) * 20
    else:
        return query["cost"]
