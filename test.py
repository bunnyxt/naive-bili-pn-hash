from pybiliapi import *
import time


if __name__ == '__main__':
    bapi = BiliApi()
    for i in range(364108, 540768, 3):
        obj = bapi.get_video_view(i)
        if obj['code'] == 0:
            pubdate = int(obj['data']['pubdate'])
            ctime = int(obj['data']['ctime'])
            if pubdate != ctime:
                print(i, pubdate, ctime)
    time.sleep(0.2)