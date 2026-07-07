from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
import enum

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    dark_mode = db.Column(db.Boolean, default=False)
    
    # Relationships
    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    daily_logs = db.relationship('DailyLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    streaks = db.relationship('Streak', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Category(db.Model):
    """Category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    color_hex = db.Column(db.String(7), default='#3498db')  # Default blue
    icon = db.Column(db.String(50), default='📌')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    streaks = db.relationship('Streak', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='_user_category_uc'),)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Goal(db.Model):
    """Goal model for longer-term objectives"""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='goal', lazy='dynamic')
    
    def __repr__(self):
        return f'<Goal {self.title}>'


class PriorityEnum(enum.Enum):
    """Priority enumeration"""
    HIGH = 'High'
    MEDIUM = 'Med'
    LOW = 'Low'


class RecurrenceEnum(enum.Enum):
    """Recurrence enumeration"""
    NONE = 'none'
    DAILY = 'daily'
    WEEKLY = 'weekly'


class Task(db.Model):
    """Task model"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id', ondelete='SET NULL'), nullable=True)
    
    title = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    priority = db.Column(db.Enum(PriorityEnum), default=PriorityEnum.MEDIUM)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.Enum(RecurrenceEnum), default=RecurrenceEnum.NONE)
    
    task_date = db.Column(db.Date, nullable=False, index=True)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    media_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subtasks = db.relationship('SubTask', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def mark_complete(self):
        """Mark task as completed with timestamp"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
    
    def mark_incomplete(self):
        """Mark task as incomplete"""
        self.is_completed = False
        self.completed_at = None
    
    def __repr__(self):
        return f'<Task {self.title}>'


class SubTask(db.Model):
    """SubTask model for breaking down tasks"""
    __tablename__ = 'subtasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SubTask {self.title}>'


class DailyLog(db.Model):
    """Daily log model for tracking daily metrics"""
    __tablename__ = 'daily_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, index=True)
    completion_percent = db.Column(db.Float, default=0.0)
    mood_rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    reflection_note = db.Column(db.Text, nullable=True)
    is_streak_freeze = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'log_date', name='_user_daily_log_uc'),)
    
    def __repr__(self):
        return f'<DailyLog {self.log_date}>'


class Streak(db.Model):
    """Streak tracking model"""
    __tablename__ = 'streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)
    
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'category_id', name='_user_category_streak_uc'),)
    
    def __repr__(self):
        return f'<Streak current={self.current_streak}>'
