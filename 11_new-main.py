import time
import math
from logger import logger_11
from pybiliapi import BiliApi
from util import get_ts_s, ts_s_to_str
from db import Session, DBOperation, NbphRecord


def main():
    round_count = 1
    round_start = 0
    round_end = 0
    round_visit_count = 0
    session = None
    while True:
        try:
            logger_11.info('round %d start' % round_count)
            round_start = get_ts_s()
            round_visit_count = 0
            bapi = BiliApi()
            session = Session()

            # get page total
            obj = bapi.get_archive_rank_by_partion(30, 1, 50)
            page_total = math.ceil(obj['data']['page']['count'] / 50)
            logger_11.info('%d page(s) found' % page_total)

            page_num = 1
            while page_num <= page_total:
                obj = bapi.get_archive_rank_by_partion(30, page_num, 50)
                while True:
                    try:
                        for _ in obj['data']['archives']:
                            pass
                        break
                    except TypeError:
                        logger_11.warning('TypeError caught, re-call page_num = %d' % page_num)
                        time.sleep(1)
                        obj = bapi.get_archive_rank_by_partion(30, page_num, 50)
                try:
                    added = get_ts_s()
                    for arch in obj['data']['archives']:
                        aid = int(arch['aid'])
                        nbph_record = DBOperation.query_nbph_record_via_aid(aid, session)
                        if nbph_record:
                            if nbph_record.pn != page_num:
                                nbph_record.pn = page_num
                                nbph_record.added = added
                                session.commit()
                        else:
                            nbph_record = NbphRecord()
                            nbph_record.aid = aid
                            nbph_record.pn = page_num
                            nbph_record.added = added
                            DBOperation.add(nbph_record, session)
                        round_visit_count += 1
                except Exception as e:
                    logger_11.error('Exception caught. Detail: %s' % e)
                page_num += 1
                time.sleep(0.1)
        except Exception as e:
            logger_11.error(e)
        finally:
            session.close()
            round_end = get_ts_s()
            logger_11.info('round %d, start: %s, end: %s, timespan: %d, visit_count: %d, speed: %.2f'
                           % (round_count, ts_s_to_str(round_start), ts_s_to_str(round_end), round_end-round_start,
                              round_visit_count, round_visit_count/(round_end-round_start)*60))
            round_count += 1
            time.sleep(10)


if __name__ == '__main__':
    main()
