from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, Integer, String, DateTime, Text
import datetime


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


class UserMessages(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    text = Column(String(1000), nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    count = Column(Integer, default=0)