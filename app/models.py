from . import db
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


# class User(db.Model):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     username = Column(String(50), unique=True, nullable=False)
#     tasks = relationship('TaskManager', backref='user', lazy='joined')


class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(400), nullable=False)  # 🆕 Add this line
    tasks = relationship('TaskManager', backref='user', lazy='joined')

class TaskManager(db.Model):
    __tablename__ = 'task_manager'
    id = Column(Integer, primary_key=True)
    task_name = Column(String(100), nullable=False)
    description = Column(String(200))
    status = Column(Boolean, default=False)
    priority = Column(String(20))
    created_at = Column(Date, nullable=False)
    assigned_user = Column(Integer, ForeignKey('users.id'))
    logs = relationship('TaskLogger', backref='task', lazy='joined')
    is_active = Column(Boolean, default=True)


class TaskLogger(db.Model):
    __tablename__ = 'task_logger'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task_manager.id'))
    log_message = Column(String(200))
    timestamp = Column(Date, default=datetime.now)