import schedule
from pybiliapi import *
from db import Video, Session, DBOperation
import sys
import threading
import time
import math
from util import create_time_to_ts
from logger import logger_02


def routine_update_via_tid(tid):
    logger_02.info('Now start routine update %d tid...' % tid)

    session = Session()
    bapi = BiliApi()

    # 01 add new video
    logger_02.info('Now start add new video with tid %d...' % tid)

    # get last aid
    last_aids = list(map(lambda x: x.aid, DBOperation.query_last_x_aid_via_tid(tid, 10, session)))
    logger_02.info('Get last aids: %s' % last_aids)  # avoid last aid deleted

    # get page total
    obj = bapi.get_archive_rank_by_partion(tid, 1, 50)
    page_total = math.ceil(obj['data']['page']['count'] / 50)

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
            page_total = math.ceil(obj['data']['page']['count'] / 50)
            # logger_02.info('%d / %d done' % (page_num, page_total))
        except Exception as e:
            logger_02.error('Exception caught. Detail: %s' % e)
        page_num += 1

    if new_video_count == 0:
        logger_02.info('No new video found with %d tid.' % tid)
    else:
        logger_02.info('%d new video(s) found with %d tid.' % (new_video_count, tid))
    logger_02.info('Finish add new video with tid %d!' % tid)

    # 02 delete invalid video
    logger_02.info('Now start delete invalid video with tid %d...' % tid)

    # get count in db
    count_db = DBOperation.count_video_via_tid(tid, session)

    # get count via api
    obj = bapi.get_archive_rank_by_partion(tid, 1, 50)
    count_api = int(obj['data']['page']['count'])
    page_total = math.ceil(obj['data']['page']['count'] / 50)

    logger_02.info('Get count_db = %d, count_api = %d' % (count_db, count_api))
    invalid_count = count_db - count_api
    if invalid_count > 0:
        # need to delete
        page_num = 1
        unsettled_diff_aids = []
        while page_num <= page_total and invalid_count > 0:
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
                # get page aids
                page_aids = [v['aid'] for v in obj['data']['archives']]

                # get db aids
                # TODO check
                create_ts_from = create_time_to_ts(obj['data']['archives'][0]['create']) + 59  # bigger one
                create_ts_to = create_time_to_ts(obj['data']['archives'][-1]['create'])  # smaller one
                db_videos = DBOperation.query_video_between_create_ts(create_ts_from, create_ts_to, session)
                db_aids = list(map(lambda x: x.aid, db_videos))

                # process unsettled
                for aid in unsettled_diff_aids:
                    if aid not in page_aids:
                        DBOperation.delete_video_via_aid(aid, session)
                        logger_02.info('Delete unsettled invalid aid %d.' % aid)
                        invalid_count -= 1
                    else:
                        logger_02.info('Save unsettled aid %d.' % aid)
                unsettled_diff_aids.clear()

                # get diff
                diff_aids = [aid for aid in db_aids if aid not in page_aids]
                new_aids = [aid for aid in page_aids if aid not in db_aids]

                # process diff
                if len(diff_aids) > 0:
                    for aid in diff_aids:
                        # query create time
                        create = -1
                        for v in db_videos:
                            if v.aid == aid:
                                create = v.create
                                break
                        if create_ts_to <= create <= create_ts_to + 59:
                            unsettled_diff_aids.append(aid)
                            logger_02.info('Add aid %d to unsettled list.' % aid)
                        elif create_ts_from - 59 <= create <= create_ts_from:
                            # counted in last page
                            pass
                        else:
                            DBOperation.delete_video_via_aid(aid, session)
                            logger_02.info('Delete invalid aid %d.' % aid)
                            invalid_count -= 1
                else:
                    logger_02.info('No diff aid!')

                # process new
                last_create_ts = 0
                last_create_ts_offset = 59
                for aid in new_aids:
                    for arch in obj['data']['archives']:
                        if arch['aid'] == aid:
                            create = arch['create']
                            create_ts = create_time_to_ts(create)
                            if create_ts == last_create_ts:
                                if last_create_ts_offset > 0:
                                    last_create_ts_offset -= 1
                            else:
                                last_create_ts = create_ts
                                last_create_ts_offset = 59
                            create_ts += last_create_ts_offset
                            video = Video(aid=aid, tid=tid, create=create_ts)
                            logger_02.info('Add new video %s.' % video)
                            DBOperation.add(video, session)
                            break

                page_total = math.ceil(obj['data']['page']['count'] / 50)
                logger_02.info('Page %d / %d done, %d invalid aid left.' % (page_num, page_total, invalid_count))
                page_num += 1
            except Exception as e:
                logger_02.error('Exception caught. Detail: %s' % e)
    else:
        logger_02.info('No invalid video to delete!')

    logger_02.info('Finish delete invalid video with tid %d!' % tid)

    logger_02.info('Finish routine update %d tid.\n' % tid)
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
