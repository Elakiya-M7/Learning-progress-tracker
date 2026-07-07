"""
Streak calculation utility for tracking user productivity streaks
"""
from datetime import datetime, date, timedelta
from models import DailyLog, Streak, db


def calculate_streaks(user_id, category_id=None):
    """
    Calculate current and longest streaks for a user or category.
    A streak is broken if a day has 0% completion and is not a streak freeze.
    
    Args:
        user_id: The user's ID
        category_id: Optional category ID. If None, calculates overall streak.
    
    Returns:
        dict: Contains 'current_streak' and 'longest_streak'
    """
    # Get all daily logs for the user, ordered by date descending
    if category_id:
        # For category-specific streaks, we'd need to filter tasks by category
        query = DailyLog.query.filter_by(user_id=user_id).order_by(DailyLog.log_date.desc())
    else:
        query = DailyLog.query.filter_by(user_id=user_id).order_by(DailyLog.log_date.desc())
    
    logs = query.all()
    
    if not logs:
        return {'current_streak': 0, 'longest_streak': 0}
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    for i, log in enumerate(logs):
        # If completion > 0 or is a streak freeze, continue the streak
        if log.completion_percent > 0 or log.is_streak_freeze:
            temp_streak += 1
            # Update current streak if this is recent (within last few days)
            if i < 3:  # Today or recent days
                current_streak = temp_streak
        else:
            # Streak broken
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            temp_streak = 0
    
    # Check if the last streak is the longest
    if temp_streak > longest_streak:
        longest_streak = temp_streak
    
    # Update database
    streak_record = Streak.query.filter_by(user_id=user_id, category_id=category_id).first()
    if streak_record:
        streak_record.current_streak = current_streak
        streak_record.longest_streak = longest_streak
        streak_record.last_updated = datetime.utcnow()
    else:
        streak_record = Streak(
            user_id=user_id,
            category_id=category_id,
            current_streak=current_streak,
            longest_streak=longest_streak
        )
        db.session.add(streak_record)
    
    db.session.commit()
    
    return {'current_streak': current_streak, 'longest_streak': longest_streak}


def get_current_streak(user_id, category_id=None):
    """
    Get the current streak for a user or category from the database.
    Recalculates if not found.
    
    Args:
        user_id: The user's ID
        category_id: Optional category ID
    
    Returns:
        int: Current streak count
    """
    streak_record = Streak.query.filter_by(user_id=user_id, category_id=category_id).first()
    
    if not streak_record:
        result = calculate_streaks(user_id, category_id)
        return result['current_streak']
    
    return streak_record.current_streak


def get_longest_streak(user_id, category_id=None):
    """
    Get the longest streak for a user or category.
    
    Args:
        user_id: The user's ID
        category_id: Optional category ID
    
    Returns:
        int: Longest streak count
    """
    streak_record = Streak.query.filter_by(user_id=user_id, category_id=category_id).first()
    
    if not streak_record:
        result = calculate_streaks(user_id, category_id)
        return result['longest_streak']
    
    return streak_record.longest_streak


def update_streak_on_completion(user_id, task_date):
    """
    Update streak after a task is marked complete.
    This is called whenever a task is toggled.
    
    Args:
        user_id: The user's ID
        task_date: The date of the task
    """
    from models import Task
    
    # Get all tasks for the user on this date
    tasks = Task.query.filter_by(user_id=user_id, task_date=task_date).all()
    
    if not tasks:
        return
    
    # Calculate completion for this day
    completed = sum(1 for t in tasks if t.is_completed)
    total = len(tasks)
    completion_percent = (completed / total * 100) if total > 0 else 0
    
    # Update or create daily log
    daily_log = DailyLog.query.filter_by(user_id=user_id, log_date=task_date).first()
    if not daily_log:
        daily_log = DailyLog(user_id=user_id, log_date=task_date, completion_percent=completion_percent)
        db.session.add(daily_log)
    else:
        daily_log.completion_percent = completion_percent
    
    db.session.commit()
    
    # Recalculate streaks
    calculate_streaks(user_id)
