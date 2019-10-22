from sqlalchemy.exc import IntegrityError as SqlalchemyIntegrityError
from pymysql.err import IntegrityError as PymysqlIntegrityError
from sqlalchemy.exc import InvalidRequestError
from .models import Video
from sqlalchemy import func
from logger import logger_db

__all__ = ['DBOperation']


class DBOperation:

    @classmethod
    def add(cls, obj, session):
        try:
            session.add(obj)
            session.commit()
        except Exception as e:
            logger_db.error('Exception caught! DBOperation add(%r).' % obj, exc_info=True)
            session.rollback()

    @classmethod
    def add_all(cls, obj_list, session):
        try:
            session.add_all(obj_list)
            session.commit()
        except (SqlalchemyIntegrityError, PymysqlIntegrityError, InvalidRequestError):
            logger_db.warning('Exception caught! DBOperation add_all(%r). Now go add one by one.' % obj_list,
                              exc_info=True)
            session.rollback()
            for obj in obj_list:
                cls.add(obj, session)
        except Exception as e:
            logger_db.error('Exception caught! DBOperation add_all(%r).' % obj_list, exc_info=True)
            session.rollback()

    @classmethod
    def query_all(cls, table, session):
        try:
            result = session.query(table).all()
            return result
        except Exception as e:
            logger_db.error('Exception caught! DBOperation query_all(%r).' % table, exc_info=True)
            return None

    @classmethod
    def count_video_via_tid(cls, tid, session):
        try:
            count = session.query(func.count(Video.aid)).filter(Video.tid == tid).scalar()
            return count
        except Exception as e:
            logger_db.error('Exception caught! DBOperation count_video_via_tid(%r).' % tid, exc_info=True)
            return None

    @classmethod
    def query_last_x_aid_via_tid(cls, tid, x, session):
        try:
            result = session.query(Video).filter(Video.tid == tid).order_by(Video.create.desc()).limit(x).all()
            return result
        except Exception as e:
            logger_db.error('Exception caught! DBOperation query_last_x_aid_via_tid(%r, %r).' % (tid, x), exc_info=True)
            return None

    @classmethod
    def query_video_via_aid(cls, aid, session):
        try:
            result = session.query(Video).filter(Video.aid == aid).first()
            return result
        except Exception as e:
            logger_db.error('Exception caught! DBOperation query_video_via_aid(%r).' % aid, exc_info=True)
            return None

    @classmethod
    def count_later_video_via_tid_and_create(cls, tid, create, session):
        try:
            count = session.query(func.count(Video.aid)).filter(Video.tid == tid, Video.create >= create).scalar()
            return count
        except Exception as e:
            logger_db.error(
                'Exception caught! DBOperation count_later_video_via_tid_and_create(%r, %r).' % (tid, create),
                exc_info=True)
            return None

    @classmethod
    def query_video_between_create_ts(cls, ts_from, ts_to, session):
        try:
            result = session.query(Video).filter(Video.create >= ts_to, Video.create <= ts_from).all()
            return result
        except Exception as e:
            logger_db.error('Exception caught! DBOperation query_video_between_create_ts(%r, %r).' % (ts_from, ts_to),
                            exc_info=True)
            return None

    @classmethod
    def delete_video_via_aid(cls, aid, session):
        try:
            session.query(Video).filter(Video.aid == aid).delete()
            session.commit()
        except Exception as e:
            logger_db.error('Exception caught! DBOperation delete_video_via_aid(%r).' % aid, exc_info=True)
            session.rollback()
