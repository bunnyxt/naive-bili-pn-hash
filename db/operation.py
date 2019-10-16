from sqlalchemy.exc import IntegrityError as SqlalchemyIntegrityError
from pymysql.err import IntegrityError as PymysqlIntegrityError
from sqlalchemy.exc import InvalidRequestError
from .models import Video
from sqlalchemy import func

__all__ = ['DBOperation']


class DBOperation:

    @classmethod
    def add(cls, obj, session):
        try:
            session.add(obj)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()

    @classmethod
    def add_all(cls, obj_list, session):
        try:
            session.add_all(obj_list)
            session.commit()
        except (SqlalchemyIntegrityError, PymysqlIntegrityError, InvalidRequestError):
            session.rollback()
            for obj in obj_list:
                cls.add(obj, session)
        except Exception as e:
            print(e)
            session.rollback()

    @classmethod
    def query_all(cls, table, session):
        try:
            result = session.query(table).all()
            return result
        except Exception as e:
            print(e)
            return None

    @classmethod
    def count_video_via_tid(cls, tid, session):
        try:
            count = session.query(func.count(Video.aid)).filter(Video.tid == tid).scalar()
            return count
        except Exception as e:
            print(e)
            return None

    @classmethod
    def query_last_x_aid_via_tid(cls, tid, x, session):
        try:
            result = session.query(Video).filter(Video.tid == tid).order_by(Video.create.desc()).limit(x).all()
            return result
        except Exception as e:
            print(e)
            return None

    @classmethod
    def query_video_via_aid(cls, aid, session):
        try:
            result = session.query(Video).filter(Video.aid == aid).first()
            return result
        except Exception as e:
            print(e)
            return None

    @classmethod
    def count_later_video_via_tid_and_create(cls, tid, create, session):
        try:
            count = session.query(func.count(Video.aid)).filter(Video.tid == tid, Video.create >= create).scalar()
            return count
        except Exception as e:
            print(e)
            return None
