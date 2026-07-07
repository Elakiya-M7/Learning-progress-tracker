from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from models import db, Task, Category, SubTask, DailyLog
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from config import Config
import csv
import io

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@tasks_bp.route('/today')
@login_required
def today():
    """Dashboard showing today's tasks"""
    today_date = date.today()
    tasks = Task.query.filter_by(user_id=current_user.id, task_date=today_date).all()
    categories = current_user.categories.all()
    
    # Calculate today's completion %
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.is_completed)
    completion_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get or create daily log
    daily_log = DailyLog.query.filter_by(user_id=current_user.id, log_date=today_date).first()
    if not daily_log:
        daily_log = DailyLog(user_id=current_user.id, log_date=today_date, completion_percent=completion_percent)
        db.session.add(daily_log)
        db.session.commit()
    else:
        daily_log.completion_percent = completion_percent
        db.session.commit()
    
    return render_template('dashboard.html', tasks=tasks, categories=categories, 
                          completion_percent=completion_percent, daily_log=daily_log, today_date=today_date)


@tasks_bp.route('/today/update-log', methods=['POST'])
@login_required
def update_daily_log():
    """Update daily log with mood rating and reflection"""
    today_date = date.today()
    mood_rating = request.form.get('mood_rating', type=int)
    reflection_note = request.form.get('reflection_note', '').strip()
    
    # Get or create daily log
    daily_log = DailyLog.query.filter_by(user_id=current_user.id, log_date=today_date).first()
    if not daily_log:
        daily_log = DailyLog(user_id=current_user.id, log_date=today_date)
        db.session.add(daily_log)
    
    # Update fields
    if mood_rating and 1 <= mood_rating <= 5:
        daily_log.mood_rating = mood_rating
    if reflection_note:
        daily_log.reflection_note = reflection_note
    
    db.session.commit()
    flash('Daily log updated successfully!', 'success')
    
    return redirect(url_for('tasks.today'))


@tasks_bp.route('/add', methods=['POST'])
@login_required
def add_task():
    """Add a new task"""
    try:
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        priority = request.form.get('priority', 'Med')
        task_date_str = request.form.get('task_date', str(date.today()))
        is_recurring = request.form.get('is_recurring') == 'on'
        recurrence_type = request.form.get('recurrence_type', 'none')
        notes = request.form.get('notes', '').strip()
        goal_id = request.form.get('goal_id') or None
        
        # Validation
        if not title:
            flash('Task title is required.', 'danger')
            return redirect(request.referrer or url_for('tasks.today'))
        
        # Verify category belongs to user
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
        if not category:
            flash('Invalid category.', 'danger')
            return redirect(request.referrer or url_for('tasks.today'))
        
        # Parse task date
        task_date = datetime.strptime(task_date_str, '%Y-%m-%d').date()
        
        # Create task
        task = Task(
            user_id=current_user.id,
            category_id=category_id,
            goal_id=goal_id,
            title=title,
            priority=priority,
            is_recurring=is_recurring,
            recurrence_type=recurrence_type,
            notes=notes,
            task_date=task_date
        )
        
        # Handle file upload
        if 'media' in request.files:
            file = request.files['media']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                task.media_url = f"uploads/{filename}"
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding task: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('tasks.today'))


@tasks_bp.route('/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task.is_completed:
        task.mark_incomplete()
    else:
        task.mark_complete()
    
    db.session.commit()
    
    # Update daily log
    today_date = task.task_date
    tasks_on_date = Task.query.filter_by(user_id=current_user.id, task_date=today_date).all()
    completed = sum(1 for t in tasks_on_date if t.is_completed)
    completion_percent = (completed / len(tasks_on_date) * 100) if tasks_on_date else 0
    
    daily_log = DailyLog.query.filter_by(user_id=current_user.id, log_date=today_date).first()
    if daily_log:
        daily_log.completion_percent = completion_percent
        db.session.commit()
    
    return jsonify({
        'success': True,
        'is_completed': task.is_completed,
        'completion_percent': completion_percent
    })


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit a task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('tasks.today'))
    
    if request.method == 'POST':
        try:
            task.title = request.form.get('title', '').strip()
            task.category_id = request.form.get('category_id')
            task.priority = request.form.get('priority', 'Med')
            task.notes = request.form.get('notes', '').strip()
            task.is_recurring = request.form.get('is_recurring') == 'on'
            task.recurrence_type = request.form.get('recurrence_type', 'none')
            task.goal_id = request.form.get('goal_id') or None
            
            # Verify category belongs to user
            category = Category.query.filter_by(id=task.category_id, user_id=current_user.id).first()
            if not category:
                flash('Invalid category.', 'danger')
                return redirect(url_for('tasks.today'))
            
            # Handle file upload
            if 'media' in request.files:
                file = request.files['media']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
                    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    task.media_url = f"uploads/{filename}"
            
            db.session.commit()
            flash('Task updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'danger')
        
        return redirect(url_for('tasks.today'))
    
    categories = current_user.categories.all()
    return render_template('edit_task.html', task=task, categories=categories)


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        # Delete media file if exists
        if task.media_url:
            filepath = os.path.join('static', task.media_url)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.session.delete(task)
        db.session.commit()
        
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('tasks.today'))


@tasks_bp.route('/category/add', methods=['POST'])
@login_required
def add_category():
    """Add a new category"""
    try:
        name = request.form.get('name', '').strip()
        color_hex = request.form.get('color_hex', '#3498db')
        icon = request.form.get('icon', '📌')
        
        # Validation
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('tasks.today'))
        
        # Check if category already exists for this user
        existing = Category.query.filter_by(user_id=current_user.id, name=name).first()
        if existing:
            flash('You already have a category with this name.', 'danger')
            return redirect(url_for('tasks.today'))
        
        # Create category
        category = Category(
            user_id=current_user.id,
            name=name,
            color_hex=color_hex,
            icon=icon,
            is_default=False
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding category: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('tasks.today'))


@tasks_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    if category.is_default:
        return jsonify({'error': 'Cannot delete default categories'}), 403
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('tasks.today'))


@tasks_bp.route('/search')
@login_required
def search():
    """Search tasks by keyword, category, or date range"""
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = Task.query.filter_by(user_id=current_user.id)
    
    # Filter by keyword
    if keyword:
        query = query.filter(
            db.or_(
                Task.title.ilike(f'%{keyword}%'),
                Task.notes.ilike(f'%{keyword}%')
            )
        )
    
    # Filter by category
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Filter by date range
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Task.task_date >= start)
        except ValueError:
            flash('Invalid start date format.', 'warning')
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Task.task_date <= end)
        except ValueError:
            flash('Invalid end date format.', 'warning')
    
    # Execute query
    results = query.order_by(Task.task_date.desc()).all()
    categories = current_user.categories.all()
    
    return render_template('search_results.html', 
                          results=results, 
                          categories=categories,
                          keyword=keyword,
                          category_id=category_id,
                          start_date=start_date,
                          end_date=end_date)


@tasks_bp.route('/export/csv')
@login_required
def export_csv():
    """Export all tasks as CSV"""
    # Get all tasks for the user
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Title', 'Category', 'Priority', 'Completed', 'Completed At', 'Notes', 'Media'
    ])
    
    # Write data rows
    for task in tasks:
        writer.writerow([
            task.task_date.strftime('%Y-%m-%d'),
            task.title,
            task.category.name,
            task.priority.value,
            'Yes' if task.is_completed else 'No',
            task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else '',
            task.notes or '',
            task.media_url or ''
        ])
    
    # Prepare file for download
    output.seek(0)
    response = send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"dailytrack_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    
    return response


# Dashboard blueprint name mapping
from flask import Blueprint as BP
dashboard_bp = BP('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Redirect to today view"""
    return redirect(url_for('tasks.today'))

# Register dashboard blueprint
