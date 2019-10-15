__all__ = ['DBOperation']


class DBOperation:

    @classmethod
    def query_all(cls, table, session):
        try:
            result = session.query(table).all()
            return result
        except Exception as e:
            print(e)
            return None

    @classmethod
    def add(cls, obj, session):
        try:
            session.add(obj)
            session.commit()
        except Exception as e:
            print(e)

    @classmethod
    def add_all(cls, obj_list, session):
        try:
            session.add_all(obj_list)
            session.commit()
        except Exception as e:
            print(e)
            for obj in obj_list:
                cls.add(obj, session)
