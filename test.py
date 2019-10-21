from db import Session
from nbph import *

if __name__ == '__main__':
    # get db session
    session = Session()

    # get pn via aid
    aid = 456930
    tid, pn = get_tid_pn(aid, session)
    print('aid = %d, tid = %d, pn = %d' % (aid, tid, pn))

    # test pn
    index = test_pn(aid, tid, pn)
    if index == -1:
        print('test fail! aid = %d not in pn = %d!' % (aid, pn))
    else:
        print('test success! aid = %d in pn = %d with index %d!' % (aid, pn, index))
