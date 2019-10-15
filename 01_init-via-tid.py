from pybiliapi import *
import db
import sys


def init_via_tid(tid):
    bapi = BiliApi()
    session = db.Session()

    # get page total
    obj = bapi.get_archive_rank_by_partion(tid, 1, 50)
    page_total = int(obj['data']['page']['count'] / 50) + 1

    # get videos data info from api
    page_num = 626
    while page_num <= page_total:
        obj = bapi.get_archive_rank_by_partion(tid, page_num, 50)
        try:
            video_list = []
            for arch in obj['data']['archives']:
                aid = int(arch['aid'])
                video_list.append(db.Video(aid=aid, tid=tid))
            db.DBOperation.add_all(video_list, session)
            page_total = int(obj['data']['page']['count'] / 50) + 1
            print('%d / %d' % (page_num, page_total))
        except Exception as e:
            print(e)
        page_num += 1


if __name__ == '__main__':
    if len(sys.argv) == 2:
        tid = int(sys.argv[1])
        print('Now start init db with tid %d...' % tid)

        init_via_tid(tid)

        print('Done!')
    else:
        print('[Error] No tid assigned!')
        exit(-1)
