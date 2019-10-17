from db import Session
from nbph import *

if __name__ == '__main__':
    # get db session
    session = Session()

    # get pn via aid
    aid = 456930
    pn = get_pn(aid, session)
    print('aid = %d, pn = %d' % (aid, pn))

    # test pn
    index = test_pn(aid, 30, pn)
    if index == -1:
        print('test fail! aid = %d not in pn = %d!' % (aid, pn))
    else:
        print('test success! aid = %d in pn = %d with index %d!' % (aid, pn, index))
