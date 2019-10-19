import schedule
from pybiliapi import *
from db import Video, Session, DBOperation
import sys
import threading
import time
from util import create_time_to_ts
from logger import logger_02


def routine_update_via_tid(tid):
    logger_02.info('Now start routine update %d tid...' % tid)

    # get last aid
    session = Session()
    last_aids = list(map(lambda x: x.aid, DBOperation.query_last_x_aid_via_tid(tid, 10, session)))
    logger_02.info('Get last aids: %s' % last_aids)  # avoid last aid deleted

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
        while True:
            try:
                for _ in obj['data']['archives']:
                    pass
                break
            except TypeError:
                logger_02.warning('TypeError caught, re-call page_num = %d' % page_num)
                time.sleep(1)
                obj = bapi.get_archive_rank_by_partion(tid, page_num, 50)
        try:
            aid_list = []
            video_list = []
            for arch in obj['data']['archives']:
                aid = int(arch['aid'])
                create = arch['create']

                if aid in last_aids:
                    logger_02.info('Meet aid = %d in last_aids, break.' % aid)
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
                    logger_02.info('Add new video %s' % video)
                    video_list.append(video)
                    aid_list.append(aid)
                else:
                    logger_02.warning('Aid %d already added!' % aid)
            DBOperation.add_all(video_list, session)
            last_aid_list = aid_list
            page_total = int(obj['data']['page']['count'] / 50) + 1
            # logger_02.info('%d / %d done' % (page_num, page_total))
        except Exception as e:
            logger_02.error('Exception caught. Detail: %s' % e)
        page_num += 1

    if new_video_count == 0:
        logger_02.info('No new video found with %d tid.' % tid)
    else:
        logger_02.info('%d new video(s) found with %d tid.' % (new_video_count, tid))
    logger_02.info('Finish routine update %d tid.' % tid)
    session.close()


def routine_update_via_tid_task(tid):
    threading.Thread(target=routine_update_via_tid, args=(tid,)).start()


def routine_update_via_tid_start(tid):
    routine_update_via_tid_task(tid)
    schedule.every(10).minutes.do(routine_update_via_tid_task, tid)

    while True:
        schedule.run_pending()
        time.sleep(10)


def main():
    if len(sys.argv) == 2:
        tid = int(sys.argv[1])
        logger_02.info('Now start routine update via tid %d...' % tid)

        routine_update_via_tid_start(tid)

        logger_02.info('Routine update stopped!')
    else:
        logger_02.error('No tid assigned!')
        exit(-1)


if __name__ == '__main__':
    main()
