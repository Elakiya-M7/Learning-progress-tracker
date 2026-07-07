# DailyTrack - Quick Start Guide

## ✅ Project Complete!

Your DailyTrack project has been successfully built with all features as specified. Below is a quick reference for getting started.

## 🚀 Quick Setup (5 minutes)

### Step 1: MySQL Database Setup

Open MySQL command line and run:

```sql
CREATE DATABASE dailytrack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dailytrack'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON dailytrack.* TO 'dailytrack'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 2: Update .env File

Edit the `.env` file in the dailytrack folder:

```
DB_HOST=localhost
DB_USER=dailytrack
DB_PASSWORD=your_password_here    # Use the password you created above
DB_NAME=dailytrack
SECRET_KEY=generate-a-random-secret-key
```

To generate a secure SECRET_KEY, run in Python:
```python
import secrets
print(secrets.token_hex(32))
```

### Step 3: Install Dependencies

```bash
# Navigate to project folder
cd dailytrack

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

## 📋 Features Implemented

### Authentication ✅
- User signup with email validation
- Secure login with bcrypt password hashing
- Session-based authentication
- Auto-creation of default categories on signup

### Task Management ✅
- Add/edit/delete tasks
- Task priorities (High/Medium/Low)
- Recurring tasks (Daily/Weekly)
- File uploads (photos/videos)
- Task completion tracking with timestamps

### Categories ✅
- 4 Default categories (Academics, Creative, Health, Personal Growth)
- Custom category creation
- Color-coded categories
- Category-specific metrics

### Calendar View ✅
- Month view with color-coded days
- Color coding based on daily completion %:
  - Dark Green: 90-100%
  - Light Green: 70-89%
  - Yellow: 40-69%
  - Orange: 10-39%
  - Red: 0% / No tasks
- Click days to see detailed task list
- Year heatmap (GitHub-style)

### Analytics Dashboard ✅
- Today's completion percentage
- Weekly trend chart (last 7 days)
- Category breakdown (pie chart)
- Current streak & longest streak tracking
- Best/worst day of week analysis
- Monthly completion statistics

### Daily Logs & Reflection ✅
- Mood rating (1-5 stars)
- Reflection notes (end-of-day prompts)
- Daily completion tracking
- Mood/effort visualization in analytics

### Streak System ✅
- Current streak tracking
- Longest streak record (overall & per-category)
- Streak freeze tokens (mark days as "excused")
- Recalculates on task completion changes

### Search & Export ✅
- Search by keyword (title/notes)
- Filter by category
- Filter by date range
- CSV export of all tasks with completion data

### UI/UX ✅
- Bootstrap 5 responsive design
- Mobile-friendly layout
- Dark mode support (toggle in navbar)
- Intuitive navigation
- Flash messages for user feedback

## 🎯 User Workflow

1. **Sign Up** → Creates account + 4 default categories
2. **Add Tasks** → Dashboard sidebar (Today view)
3. **Complete Tasks** → Check checkbox (auto-updates completion %)
4. **Track Progress** → Calendar shows color-coded days
5. **Analyze** → Analytics tab shows trends & streaks
6. **Reflect** → End-of-day mood & notes (bottom of dashboard)
7. **Export** → CSV download for backup/analysis

## 📁 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Flask application factory |
| `models.py` | Database models (User, Task, Category, etc.) |
| `config.py` | Configuration settings |
| `routes/auth.py` | Login/signup/logout |
| `routes/tasks.py` | Task CRUD, categories, search, export |
| `routes/calendar.py` | Calendar views |
| `routes/analytics.py` | Analytics dashboard |
| `templates/base.html` | Navigation & base layout |
| `templates/dashboard.html` | Today's task view |
| `static/css/style.css` | Styling & responsive design |
| `static/js/main.js` | Interactivity (AJAX, validation) |
| `utils/streak_calculator.py` | Streak calculation logic |

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Activate venv first, then:
pip install -r requirements.txt
```

### "Cannot connect to database"
1. Verify MySQL is running
2. Check .env credentials
3. Verify database exists: `mysql -u dailytrack -p dailytrack`

### "Address already in use" error
Flask is running on port 5000. Either:
- Kill the existing process
- Or run on different port: `python app.py --port 5001`

### "File upload not working"
1. Check `static/uploads/` folder exists
2. Verify folder has write permissions
3. Check file size < 20MB
4. Check file type (jpg/png/mp4/mov only)

## 📈 Next Steps

1. **User Signup** → Create your first account
2. **Add Tasks** → Start with 3-5 tasks for today
3. **Complete Tasks** → Check them off and watch %
4. **View Calendar** → See your daily progress
5. **Check Analytics** → Discover your patterns

## 💡 Tips for Success

- ✅ Set realistic daily goals (aim for 90%)
- 📸 Attach proof photos for creative tasks
- 🏆 Build streaks by completing daily
- 📊 Review analytics weekly
- 🎯 Use categories to organize by area
- 💬 Add reflection notes for insights

## 🆘 Support

For issues:
1. Check README.md in project root
2. Review browser console (F12) for JS errors
3. Check terminal for Flask errors
4. Verify MySQL is running
5. Re-check .env configuration

---

**Ready to build your streak? Start at http://localhost:5000** 🚀
