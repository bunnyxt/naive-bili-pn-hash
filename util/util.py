import time

__all__ = ['create_time_to_ts']


def create_time_to_ts(create):
    ts = 0
    try:
        time_array = time.strptime(create, "%Y-%m-%d %H:%M")
        ts = int(time.mktime(time_array))
    except Exception as e:
        print(e)
    return ts
