from config import database
import datetime

cur = database.client["exceed06"]["Locker"]

cur.delete_many({})

# initial

lst = []

default_start_time = datetime.datetime.now()
default_stop_time = datetime.datetime.now() + datetime.timedelta(hours=2)

for i in range(4):
    dic = {
        "locker_id": i + 1,
        "std_id": None,
        "contain": None,
        "time_start": None,
        "time_end": None,
        "cost": None,
        "is_available": True,
    }
    lst.append(dic)

dic = {
        "locker_id": 5,
        "std_id": 12,
        "contain": [],
        "time_start": default_start_time,
        "time_end": default_stop_time,
        "cost": 0,
        "is_available": False,
    }
lst.append(dic)

dic = {
        "locker_id": 6,
        "std_id": 5,
        "contain": ["bag"],
        "time_start": default_start_time,
        "time_end": default_stop_time,
        "cost": 10,
        "is_available": False,
    }
lst.append(dic)

cur.insert_many(lst)
