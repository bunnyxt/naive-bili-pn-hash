import schedule
from pybiliapi import *
import db
import sys

if __name__ == '__main__':
    if len(sys.argv) == 2:
        tid = int(sys.argv[1])
        print('Now start init db with tid %d...' % tid)

        init_via_tid(tid)

        print('Done!')
    else:
        print('[Error] No tid assigned!')
        exit(-1)
