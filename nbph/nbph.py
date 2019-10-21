from db import DBOperation
from pybiliapi import *
import math

__all__ = ['get_tid_pn', 'test_pn']


def get_tid_pn(aid, session):
    # query video
    video = DBOperation.query_video_via_aid(aid, session)
    if video is None:
        print('Video aid=%d not found!' % aid)
        return None

    # query count
    tid = video.tid
    create = video.create
    # count_total = DBOperation.count_video_via_tid(tid, session)
    count_later = DBOperation.count_later_video_via_tid_and_create(tid, create, session)

    if count_later is None:
        print('Fail to count later video!')
        return None

    pn = math.ceil(count_later / 50)
    return tid, pn


def test_pn(aid, tid, pn):
    bapi = BiliApi()
    obj = bapi.get_archive_rank_by_partion(tid, pn, 50)
    try:
        index = 1
        aids_list = []
        for arch in obj['data']['archives']:
            aid_ = int(arch['aid'])
            aids_list.append((aid_, index))
            index += 1

        filtered_list = list(filter(lambda x: x[0] == aid, aids_list))
        if len(filtered_list) == 1:
            return filtered_list[0][1]
        else:
            return -1
    except Exception as e:
        print(e)
        return -1
