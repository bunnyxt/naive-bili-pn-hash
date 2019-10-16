from pybiliapi import *
from db import DBOperation, Session, Video
import sys
from util import create_time_to_ts


def init_via_tid(tid):
    bapi = BiliApi()
    session = Session()

    # get page total
    obj = bapi.get_archive_rank_by_partion(tid, 1, 50)
    page_total = int(obj['data']['page']['count'] / 50) + 1

    # get videos data info from api
    page_num = 1
    last_aid_list = []
    last_create_ts = 0
    last_create_ts_offset = 59
    while page_num <= page_total:
        obj = bapi.get_archive_rank_by_partion(tid, page_num, 50)
        try:
            aid_list = []
            video_list = []
            for arch in obj['data']['archives']:
                aid = int(arch['aid'])
                create = arch['create']
                if aid not in last_aid_list:
                    # manual reset create_ts
                    create_ts = create_time_to_ts(create)
                    if create_ts == last_create_ts:
                        if last_create_ts_offset > 0:
                            last_create_ts_offset -= 1
                    else:
                        last_create_ts = create_ts
                        last_create_ts_offset = 59
                    create_ts += last_create_ts_offset
                    video_list.append(Video(aid=aid, tid=tid, create=create_ts))
                    aid_list.append(aid)
                else:
                    print('%d already added!' % aid)
            DBOperation.add_all(video_list, session)
            last_aid_list = aid_list
            page_total = int(obj['data']['page']['count'] / 50) + 1
            print('%d / %d done' % (page_num, page_total))
        except Exception as e:
            print(e)
        page_num += 1

    session.close()
    print('Success get %d tid videos data info from api.' % tid)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        tid = int(sys.argv[1])
        print('Now start init db with tid %d...' % tid)

        init_via_tid(tid)

        print('Done!')
    else:
        print('[Error] No tid assigned!')
        exit(-1)
