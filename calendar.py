from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Task, DailyLog
from datetime import datetime, date, timedelta
import calendar as cal

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')


@calendar_bp.route('/month')
@login_required
def month_view():
    """Month view of calendar with completion colors"""
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    
    # Get all daily logs for this month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    daily_logs = DailyLog.query.filter_by(user_id=current_user.id).filter(
        DailyLog.log_date.between(first_day, last_day)
    ).all()
    
    logs_by_date = {log.log_date: log for log in daily_logs}
    
    # Build calendar grid
    cal_matrix = cal.monthcalendar(year, month)
    calendar_data = []
    
    for week in cal_matrix:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                day_date = date(year, month, day)
                log = logs_by_date.get(day_date)
                completion = log.completion_percent if log else 0
                
                # Determine color based on completion %
                if completion == 0:
                    color_class = 'red'
                elif completion < 10:
                    color_class = 'orange'
                elif completion < 40:
                    color_class = 'yellow'
                elif completion < 70:
                    color_class = 'light-green'
                else:
                    color_class = 'dark-green'
                
                week_data.append({
                    'day': day,
                    'date': day_date,
                    'completion': round(completion, 1),
                    'color_class': color_class
                })
        calendar_data.append(week_data)
    
    month_name = cal.month_name[month]
    
    return render_template('calendar.html', 
                          calendar_data=calendar_data, 
                          month_name=month_name, 
                          year=year, 
                          month=month,
                          prev_month=month - 1 if month > 1 else 12,
                          prev_year=year if month > 1 else year - 1,
                          next_month=month + 1 if month < 12 else 1,
                          next_year=year if month < 12 else year + 1)


@calendar_bp.route('/day/<date_str>')
@login_required
def day_view(date_str):
    """View tasks for a specific day"""
    try:
        day_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    tasks = Task.query.filter_by(user_id=current_user.id, task_date=day_date).all()
    daily_log = DailyLog.query.filter_by(user_id=current_user.id, log_date=day_date).first()
    
    return render_template('day_view.html', tasks=tasks, daily_log=daily_log, day_date=day_date)


@calendar_bp.route('/year')
@login_required
def year_view():
    """GitHub-style year heatmap"""
    year = request.args.get('year', default=datetime.now().year, type=int)
    
    # Get all daily logs for this year
    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)
    
    daily_logs = DailyLog.query.filter_by(user_id=current_user.id).filter(
        DailyLog.log_date.between(first_day, last_day)
    ).all()
    
    logs_by_date = {log.log_date: log.completion_percent for log in daily_logs}
    
    return render_template('year_view.html', year=year, logs_by_date=logs_by_date)
