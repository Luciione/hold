# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime

import json

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.Text())
    role = db.Column(db.String(20), nullable=False)
    jwt_auth_active = db.Column(db.Boolean())
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def toDICT(self):
        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):
        return self.toDICT()


class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    school = db.relationship('School', backref='owners', lazy=True)

class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    owner = db.relationship('Owner', backref='school', lazy=True)
    classrooms = db.relationship('Classroom', backref='school', lazy=True)
    students = db.relationship('Student', backref='school', lazy=True)
    educators = db.relationship('Educator', backref='school', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    classroom = db.relationship('Classroom', backref='students', lazy=True)

class Educator(db.Model):
    __tablename__ = 'educators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    school = db.relationship('School', backref='educators', lazy=True)
    classrooms = db.relationship('Classroom', backref='educator', lazy=True)
    assessments = db.relationship('Assessment', backref='educator', lazy=True)
    drive_educator = db.relationship('Drive', backref='educator', lazy=True, uselist=False, foreign_keys='Drive.educator_id')

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    school = db.relationship('School', backref='classrooms', lazy=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('educators.id'))
    educator = db.relationship('Educator', backref='classrooms', foreign_keys=[educator_id])
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'))
    drive = db.relationship('Drive', backref='classroom', foreign_keys=[drive_id])
    chatrooms = db.relationship('Chatroom', backref='classroom', lazy=True)
    students = db.relationship('Student', backref='classroom', lazy=True)
    assessments = db.relationship('Assessment', backref='classroom', lazy=True)

class Drive(db.Model):
    __tablename__ = 'drives'
    id = db.Column(db.Integer, primary_key=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('educators.id'), nullable=False)
    educator = db.relationship('Educator', backref='drive', lazy=True, uselist=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    classroom = db.relationship('Classroom', backref='drive', lazy=True, uselist=False)

class Assessment(db.Model):
    __tablename__ = 'assessments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'), nullable=False)
    drive = db.relationship('Drive', backref='assessment', lazy=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('educators.id'), nullable=False)
    educator = db.relationship('Educator', backref='assessment', lazy=True)
    questions = db.relationship('Question', backref='assessment', lazy=True)

class Chatroom(db.Model):
    __tablename__ = 'chatrooms'
    id = db.Column(db.Integer, primary_key=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('educators.id'), nullable=False)
    educator = db.relationship('Educator', backref='chatroom', lazy=True, uselist=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), nullable=False)
    chat = db.relationship('Chat', backref='chatroom', lazy=True, uselist=False)
    classrooms = db.relationship('Classroom', backref='chatroom', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_choices = db.Column(db.JSON, nullable=False)
    correct_choice = db.Column(db.Integer, nullable=False)
    question_points = db.Column(db.Integer, nullable=False)

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    answers = db.Column(db.JSON, nullable=False)
    points_earned = db.Column(db.Float, nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    assessment = db.relationship('Assessment', backref='submission', lazy=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student = db.relationship('Student', backref='submission', lazy=True)

class UserMaterialsAssociation(db.Model):
    __tablename__ = 'user_materials'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), primary_key=True)

class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id'), nullable=False)
    drive = db.relationship('Drive', backref='material', lazy=True)
    classrooms = db.relationship('Classroom', secondary='classroom_materials', back_populates='material', lazy=True)
    users = db.relationship('Users', secondary=UserMaterialsAssociation, backref='materials', lazy=True)

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    percentage = db.Column(db.Float, nullable=False)
    gradebook_id = db.Column(db.Integer, db.ForeignKey('gradebooks.id'), nullable=False)
    gradebook = db.relationship('Gradebook', backref='grade', lazy=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    assessment = db.relationship('Assessment', backref='grade', lazy=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    student = db.relationship('Student', backref='grade', lazy=True)

gradebook_student_association = db.Table(
    'gradebook_student_association',
    db.Column('gradebook_id', db.Integer, db.ForeignKey('gradebooks.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True)
)

class Gradebook(db.Model):
    __tablename__ = 'gradebooks'
    id = db.Column(db.Integer, primary_key=True)
    educator_id = db.Column(db.Integer, db.ForeignKey('educators.id'), nullable=False)
    educator = db.relationship('Educator', backref='gradebooks', lazy=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    assessment = db.relationship('Assessment', backref='gradebooks', lazy=True)
    students = db.relationship('Student', secondary=gradebook_student_association, backref='gradebooks', lazy=True)
