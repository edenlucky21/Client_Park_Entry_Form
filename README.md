# Uganda Wildlife Authority - Park Entry System

A Flask-based park entry registration system for managing tourist, transit, and student visitor information.

## Features

- ✅ Multi-form support (Tourist, Transit, Student)
- ✅ Dynamic client and vehicle management
- ✅ Admin dashboard with search and filtering
- ✅ CSV export functionality
- ✅ PDF generation for submissions
- ✅ Statistics and analytics

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/edenlucky21/Client_Park_Entry_Form.git
cd Client_Park_Entry_Form

# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

### Access
- **Form**: http://127.0.0.1:5000/
- **Admin Dashboard**: http://127.0.0.1:5000/admin
- **API Stats**: http://127.0.0.1:5000/stats
2. **Connect GitHub**: Link your GitHub repository
3. **Deploy**: Railway will automatically detect Django and deploy
4. **Database**: Railway provides PostgreSQL automatically
5. **Environment Variables** (optional):
   - `SECRET_KEY`: Your Django secret key
   - `DEBUG`: Set to `False` for production

### Manual Deployment

For other platforms (Heroku, DigitalOcean, etc.):

```bash
# Install production dependencies
pip install gunicorn dj-database-url psycopg2-binary

# Set environment variables
export DATABASE_URL="your_postgresql_url"
export SECRET_KEY="your_secret_key"
export DEBUG=False

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn park_entry.wsgi:application --bind 0.0.0.0:$PORT
```

## Project Structure

```
park_entry/           # Main Django project
├── settings.py       # Configuration
├── urls.py          # URL routing
├── wsgi.py          # Production server
└── asgi.py          # Async server

park_forms/          # Main app
├── models.py        # Database models
├── views.py         # Business logic
├── admin.py         # Admin interface
├── urls.py          # App URLs
└── apps.py          # App configuration

templates/           # HTML templates
static/             # CSS, JS, images
```

## Technologies Used

- **Backend**: Django 4.2
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML, CSS, JavaScript
- **PDF Generation**: ReportLab
- **Deployment**: Railway/Gunicorn

## Security Features

- CSRF protection
- Input validation
- Secure settings for production
- Admin authentication
- CORS configuration

## License

This project is developed for the Uganda Wildlife Authority.
