from sqlalchemy.ext import declarative

class SimpleNetBase(object):

    @declarative.declared_attr
    def __tablename__(table):
        return "%ss" % table.__name__.lower()

BASE = declarative.declarative_base(table=SimpleNetBase)
