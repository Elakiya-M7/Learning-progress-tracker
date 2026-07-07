from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Task, DailyLog, Category
from datetime import datetime, date, timedelta
from utils.streak_calculator import calculate_streaks, get_current_streak

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Analytics dashboard"""
    today = date.today()
    
    # Get today's completion
    today_log = DailyLog.query.filter_by(user_id=current_user.id, log_date=today).first()
    today_completion = today_log.completion_percent if today_log else 0
    
    # Get last 7 days for weekly trend
    last_7_days = [today - timedelta(days=i) for i in range(7)]
    last_7_days.reverse()
    
    weekly_data = []
    for day in last_7_days:
        log = DailyLog.query.filter_by(user_id=current_user.id, log_date=day).first()
        completion = log.completion_percent if log else 0
        weekly_data.append({
            'date': day.strftime('%a'),
            'completion': round(completion, 1)
        })
    
    # Get category breakdown
    categories = current_user.categories.all()
    category_data = []
    
    for category in categories:
        tasks = Task.query.filter_by(user_id=current_user.id, category_id=category.id).filter(
            Task.task_date >= today - timedelta(days=30)
        ).all()
        
        completed = sum(1 for t in tasks if t.is_completed)
        total = len(tasks)
        
        if total > 0:
            category_data.append({
                'name': category.name,
                'color': category.color_hex,
                'completed': completed,
                'total': total,
                'percentage': round(completed / total * 100, 1)
            })
    
    # Get streaks
    overall_streak = get_current_streak(current_user.id, None)
    category_streaks = {}
    for category in categories:
        streak = get_current_streak(current_user.id, category.id)
        category_streaks[category.id] = streak
    
    # Best and worst days
    all_logs = DailyLog.query.filter_by(user_id=current_user.id).filter(
        DailyLog.log_date >= today - timedelta(days=30)
    ).all()
    
    day_completions = {}
    for log in all_logs:
        day_name = log.log_date.strftime('%A')
        if day_name not in day_completions:
            day_completions[day_name] = []
        day_completions[day_name].append(log.completion_percent)
    
    best_day = None
    worst_day = None
    if day_completions:
        best_day = max(day_completions.items(), key=lambda x: sum(x[1]) / len(x[1]))
        worst_day = min(day_completions.items(), key=lambda x: sum(x[1]) / len(x[1]))
    
    return render_template('analytics.html',
                          today_completion=today_completion,
                          weekly_data=weekly_data,
                          category_data=category_data,
                          overall_streak=overall_streak,
                          category_streaks=category_streaks,
                          best_day=best_day,
                          worst_day=worst_day)


@analytics_bp.route('/monthly')
@login_required
def monthly():
    """Monthly analytics"""
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    daily_logs = DailyLog.query.filter_by(user_id=current_user.id).filter(
        DailyLog.log_date.between(first_day, last_day)
    ).all()
    
    monthly_completion = sum(log.completion_percent for log in daily_logs) / len(daily_logs) if daily_logs else 0
    
    return render_template('monthly_analytics.html',
                          year=year,
                          month=month,
                          monthly_completion=monthly_completion,
                          daily_logs=daily_logs)
