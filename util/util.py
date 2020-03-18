import time
import datetime

__all__ = ['create_time_to_ts', 'get_ts_s', 'ts_s_to_str']


def create_time_to_ts(create):
    ts = 0
    try:
        time_array = time.strptime(create, "%Y-%m-%d %H:%M")
        ts = int(time.mktime(time_array))
    except Exception as e:
        print(e)
    return ts


def get_ts_s():
    return int(round(datetime.datetime.now().timestamp()))


def ts_s_to_str(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))