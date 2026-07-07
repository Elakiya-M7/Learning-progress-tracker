# DailyTrack - Personal Productivity Tracker

A full-stack web application for students and self-learners to track their daily productivity, manage tasks, and visualize progress through color-coded calendars and analytics.

## Features

✅ **Authentication** - User signup/login with secure password hashing
✅ **Task Management** - Add, edit, delete tasks with priority levels and categories  
✅ **Categories** - Default categories (Academics, Creative, Health, Personal Growth) + custom categories
✅ **File Uploads** - Attach photos/videos to tasks for proof of completion
✅ **Calendar View** - Color-coded monthly calendar based on daily completion %
✅ **Analytics Dashboard** - Daily completion, weekly trends, category breakdown, streaks
✅ **Streak Tracking** - Track current and longest streaks with freeze tokens
✅ **Responsive Design** - Mobile-friendly Bootstrap 5 UI
✅ **Dark Mode** - Toggle dark/light theme
✅ **Daily Logs** - Mood ratings, reflection notes, completion tracking

## Tech Stack

- **Backend**: Python + Flask
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML + Jinja2 + Bootstrap 5 + Vanilla JavaScript
- **Charts**: Chart.js for analytics visualization
- **Authentication**: Flask-Login + bcrypt

## Prerequisites

- Python 3.8+
- MySQL Server 5.7+
- pip package manager

## Installation

### 1. Clone the Repository

```bash
cd dailytrack
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

```bash
mysql -u root -p
```

Then run:

```sql
CREATE DATABASE dailytrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dailytrack'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON dailytrack.* TO 'dailytrack'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure Environment Variables

Edit `.env` file with your database credentials:

```
DB_HOST=localhost
DB_USER=dailytrack
DB_PASSWORD=your_password
DB_NAME=dailytrack
SECRET_KEY=your-super-secret-key-change-this
```

Generate a secure secret key:

```python
import secrets
print(secrets.token_hex(32))
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### First Time Setup

1. **Sign Up**: Create a new account with name, email, and password
2. **Auto Categories**: Four default categories are created automatically
3. **Dashboard**: You'll be redirected to the "Today" view where you can start adding tasks

### Daily Workflow

1. **Add Tasks**: Click the task form on the right sidebar
2. **Complete Tasks**: Check the checkbox next to each task to mark it done
3. **Attach Media**: Upload photos/videos for proof of completion
4. **View Progress**: See today's completion % at the top of the page

### Calendar & Analytics

- **Calendar View**: See a month view with color-coded days based on completion %
- **Analytics**: Charts showing weekly trends, category breakdown, streaks, and best/worst days
- **Day View**: Click any calendar day to see detailed tasks and reflections for that day

### Categories

- **View Categories**: Listed in the right sidebar
- **Add Category**: Fill in the form to create custom categories
- **Delete Category**: Remove non-default categories with the × button

### Streaks

- **Current Streak**: Breaks if a day has 0% completion (without a freeze)
- **Freeze Token**: Mark 1-2 days/month as "excused" without breaking streak
- **View Streaks**: See current and longest streaks in Analytics dashboard

## File Structure

```
dailytrack/
├── app.py                 # Flask application factory
├── config.py             # Configuration settings
├── models.py             # SQLAlchemy models
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (git ignored)
├── routes/
│   ├── auth.py          # Authentication routes (signup/login/logout)
│   ├── tasks.py         # Task & category management
│   ├── calendar.py      # Calendar views
│   └── analytics.py     # Analytics & dashboard
├── static/
│   ├── css/style.css    # Main stylesheet
│   ├── js/main.js       # JavaScript functionality
│   └── uploads/         # User-uploaded files
├── templates/
│   ├── base.html        # Base template with navbar
│   ├── login.html       # Login page
│   ├── signup.html      # Signup page
│   ├── dashboard.html   # Today's task view
│   ├── calendar.html    # Month calendar view
│   ├── year_view.html   # Year heatmap
│   ├── day_view.html    # Single day detailed view
│   ├── analytics.html   # Analytics dashboard
│   └── monthly_analytics.html  # Monthly summary
└── utils/
    └── streak_calculator.py   # Streak calculation logic
```

## Database Schema

### Users Table
```sql
users (id, name, email, password_hash, created_at, dark_mode)
```

### Categories Table
```sql
categories (id, user_id, name, color_hex, icon, is_default, created_at)
```

### Tasks Table
```sql
tasks (id, user_id, category_id, goal_id, title, notes, priority, 
       is_recurring, recurrence_type, task_date, is_completed, 
       completed_at, media_url, created_at)
```

### Daily Logs Table
```sql
daily_logs (id, user_id, log_date, completion_percent, mood_rating, 
            reflection_note, is_streak_freeze)
```

### Streaks Table
```sql
streaks (id, user_id, category_id, current_streak, longest_streak, last_updated)
```

### SubTasks Table
```sql
subtasks (id, task_id, title, is_completed, created_at)
```

### Goals Table
```sql
goals (id, user_id, title, description, target_date, created_at)
```

## Security Features

✅ Password hashing with bcrypt
✅ SQL injection prevention (ORM + parameterized queries)
✅ User data isolation (user_id checks on all queries)
✅ File upload validation (type & size checks)
✅ Session-based authentication with Flask-Login
✅ CSRF protection (Flask default)

## Keyboard Shortcuts (Future)

- `?` - Show help
- `t` - Go to today
- `c` - Go to calendar
- `a` - Go to analytics

## Tips & Best Practices

- **Set realistic daily goals** - Aim for 90%+ completion
- **Use categories wisely** - Group related tasks together
- **Break large tasks** - Use subtasks for complex projects
- **Regular check-ins** - Review your streaks and trends weekly
- **Attach proof** - Upload photos/videos for creative tasks
- **Track your mood** - Rate your daily mood to identify patterns

## Troubleshooting

### "Cannot connect to database"
- Verify MySQL is running: `mysql.server start` (Mac) or `net start MySQL` (Windows)
- Check .env credentials match your MySQL setup
- Verify database and user exist

### "Tasks not saving"
- Check browser console for JavaScript errors (F12)
- Verify uploads folder has write permissions
- Check Flask server logs for exceptions

### "Media files not appearing"
- Ensure upload folder exists: `static/uploads/`
- Check file permissions (should be readable)
- Verify media URL in database matches actual file

### "Login not working"
- Clear browser cookies and cache
- Verify user exists in database
- Check password hash in database (should start with `$2b$`)

## Performance Optimization

- Add database indexes on frequently queried columns (task_date, user_id)
- Cache analytics calculations for 1 hour
- Lazy-load calendar for past/future years
- Compress media uploads before storage

## Future Enhancements

- [ ] Search & filter tasks by date range/category
- [ ] CSV export of tasks and completion data
- [ ] Recurring task automation
- [ ] Goal tracking with progress links
- [ ] Weekly summary email
- [ ] Mobile app (React Native)
- [ ] Social sharing of streaks
- [ ] Customizable color schemes
- [ ] Pomodoro timer integration
- [ ] Habit tracking templates

## API Endpoints

```
GET    /                          # Index (redirects to /tasks/today)
POST   /auth/signup               # Create account
POST   /auth/login                # Login
GET    /auth/logout               # Logout

GET    /tasks/today               # Today's dashboard
POST   /tasks/add                 # Create task
POST   /tasks/<id>/toggle         # Toggle completion
GET    /tasks/<id>/edit           # Edit task form
POST   /tasks/<id>/edit           # Update task
POST   /tasks/<id>/delete         # Delete task

POST   /tasks/category/add        # Create category
POST   /tasks/category/<id>/delete # Delete category

GET    /calendar/month            # Month view
GET    /calendar/day/<date>       # Day details
GET    /calendar/year             # Year heatmap

GET    /analytics/dashboard       # Analytics dashboard
GET    /analytics/monthly         # Monthly analytics
```

## Contributing

To contribute:
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please check:
1. The troubleshooting section above
2. Application logs in terminal
3. Browser console (F12)
4. Flask debug output

---

**Happy tracking! 📊**
