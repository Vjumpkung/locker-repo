from config import database
import datetime

cur = database.client["exceed06"]["Locker"]

cur.delete_many({})

# initial

lst = []

default_start_time = datetime.datetime.now()
default_stop_time = datetime.datetime.now() + datetime.timedelta(hours=2)

for i in range(6):
    dic = {
        "locker_id": i + 1,
        "std_id": 0,
        "contain": [],
        "time_start": default_start_time,
        "time_end": default_stop_time,
        "cost": 0,
        "is_available": True,
    }
    lst.append(dic)

cur.insert_many(lst)
