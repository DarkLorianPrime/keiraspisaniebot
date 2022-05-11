from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_mixins import AllFeaturesMixin

from vk_base.Models.database import session

Base = declarative_base()


class BaseModel(Base, AllFeaturesMixin):
    __abstract__ = True


class Group(BaseModel):
    __tablename__ = "vkhandler_group"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group = Column(String)
    chat_id = Column(String)


class Settings(BaseModel):
    __tablename__ = "vkhandler_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    admin_access = Column(Boolean, default=True)
    add_class = Column(Boolean, default=True)
    add_time = Column(Boolean, default=True)
    add_teacher = Column(Boolean, default=True)
    buttons = Column(Boolean, default=True)
    autosend = Column(Boolean, default=True)
    autosend_time = Column(String, default="22:00")
    notify_update = Column(Boolean, default=True)


mtm_notify = Table("vkhandler_notify_urls",
                   Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('notifyid', Integer, ForeignKey("vkhandler_notify.id")),
                   Column('urlid', Integer, ForeignKey("vkhandler_notifyurls.id")))


class Notify(BaseModel):
    __tablename__ = "vkhandler_notify"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    count = Column(Integer, default=0)
    name = Column(String)
    text = Column(String)
    urls = relationship("NotifyUrls", secondary=mtm_notify, backref="Notify")


class NotifyUrls(BaseModel):
    __tablename__ = "vkhandler_notifyurls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    url = Column(String)


class NotifyGroup(BaseModel):
    __tablename__ = "vkhandler_notifygroup"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    url = Column(String)


class PushGroup(BaseModel):
    __tablename__ = "vkhandler_pushgroup"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    name = Column(String)
    users = Column(JSON)


BaseModel.set_session(session)
