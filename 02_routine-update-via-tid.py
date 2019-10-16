import schedule
from pybiliapi import *
from db import Video, Session, DBOperation
import sys
import threading
import time
from util import create_time_to_ts


def routine_update_via_tid(tid):
    print('Now start routine update %d tid...' % tid)
    print(time.time())

    # get last aid
    session = Session()
    last_aids = list(map(lambda x: x.aid, DBOperation.query_last_x_aid_via_tid(tid, 10, session)))
    print('last aids: %s' % last_aids)  # avoid last aid deleted

    # get page total
    bapi = BiliApi()
    obj = bapi.get_archive_rank_by_partion(tid, 1, 50)
    page_total = int(obj['data']['page']['count'] / 50) + 1

    # add new videos data info from api
    page_num = 1
    last_aid_list = []
    last_create_ts = 0
    last_create_ts_offset = 59
    goon = True
    new_video_count = 0
    while page_num <= page_total and goon:
        obj = bapi.get_archive_rank_by_partion(tid, page_num, 50)
        try:
            aid_list = []
            video_list = []
            for arch in obj['data']['archives']:
                aid = int(arch['aid'])
                create = arch['create']

                if aid in last_aids:
                    print('Meet aid = %d in last_aids, break' % aid)
                    goon = False
                    break

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
                    video = Video(aid=aid, tid=tid, create=create_ts)
                    new_video_count += 1
                    print('Add new video %s' % video)
                    video_list.append(video)
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

    if new_video_count == 0:
        print('No new video found with %d tid' % tid)
    else:
        print('%d new video found with %d tid' % (new_video_count, tid))
    print('Finish routine update %d tid.\n' % tid)
    session.close()


def routine_update_via_tid_task(tid):
    threading.Thread(target=routine_update_via_tid, args=(tid,)).start()


def routine_update_via_tid_start(tid):
    schedule.every(10).minutes.do(routine_update_via_tid_task, tid)

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        tid = int(sys.argv[1])
        print('Now start routine update via tid %d...' % tid)

        routine_update_via_tid_start(tid)

        print('Stopped!')
    else:
        print('[Error] No tid assigned!')
        exit(-1)
