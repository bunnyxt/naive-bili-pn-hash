from .basic import Base
from sqlalchemy import Column, Integer

__all__ = ['Video']


class Video(Base):
    """video table"""

    __tablename__ = 'video'

    aid = Column(Integer, primary_key=True, nullable=False, unique=True)
    tid = Column(Integer, nullable=False)

    def __repr__(self):
        return "<Video(aid=%d, tid=%s)>" % (self.aid, self.tid)
