<div align="center">
  <img src="https://assets.jdbnet.co.uk/projects/echolog.png" alt="EchoLog" width="200" />
  
  # EchoLog
</div>

A Flask-based web application for personal homelab journaling. Track your daily activities, maintain a streak, and search through your journal entries with a modern, PWA-enabled interface.

## Features

- **Daily Journal Entries**: Create and manage journal entries for any date
- **Streak Tracking**: Automatically calculates consecutive days with entries
- **Search Functionality**: Search by keyword or filter by specific date
- **PWA Support**: Progressive Web App making this installable on mobile devices
- **Modern UI**: Beautiful gradient design with Tailwind CSS and responsive layout
- **Optional Authentication**: Enable login protection with environment variables
- **Multiple Database Support**: Use MySQL/MariaDB or SQLite for data persistence
- **Docker Ready**: Easy deployment with Docker and Docker Compose
- **Kubernetes Support**: Includes Kubernetes deployment manifest

## Quick Start with Docker

For deployment examples, see the [examples folder](examples/).

## Configuration

### Database Selection

EchoLog supports both MySQL/MariaDB and SQLite:

- SQLite (default for quick start)
- MySQL/MariaDB

See the [examples folder](examples/) for docker-compose files for both database types.

### Environment Variables

#### Database Configuration

- `DB_TYPE`: Database type - `mysql` (default) or `sqlite`

**MySQL/MariaDB options:**
- `MYSQL_HOST`: MySQL/MariaDB host (default: localhost)
- `MYSQL_USER`: Database user (default: root)
- `MYSQL_PASSWORD`: Database password (default: empty)
- `MYSQL_DATABASE`: Database name (default: echolog)

**SQLite options:**
- `SQLITE_DB`: Path to SQLite database file (default: echolog.db)

#### Application Configuration

- `SECRET_KEY`: Flask secret key for sessions (**REQUIRED in production!**)
- `TZ`: Timezone for date handling (default: UTC)
- `LOGIN_ENABLED`: Enable login protection (default: false)
- `LOGIN_USERNAME`: Username for authentication (default: admin)
- `LOGIN_PASSWORD`: Password for authentication (default: admin)

### Database Setup

#### MySQL/MariaDB

The application automatically initializes the database schema on first run. Ensure the database and user exist with appropriate permissions:

```sql
CREATE DATABASE echolog;
CREATE USER 'echolog'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON echolog.* TO 'echolog'@'%';
FLUSH PRIVILEGES;
```

#### SQLite

SQLite requires no setup - the database file is created automatically on first run. Ensure the directory where the database file is stored is writable by the application.

## Usage

### Creating Entries

1. Access the web interface at `http://your-server:5000`
2. Enter a journal entry in the text area
3. Select the date (defaults to today)
4. Click "Add Entry" to save

### Searching

- Use the search box to find entries by keyword
- Use the date picker to filter by specific date
- Combine both for advanced filtering

### Managing Entries

- **Edit**: Click the edit icon on any entry to modify it
- **Delete**: Click the delete icon to remove an entry permanently
- Use pagination controls to navigate through older entries

### Streak Tracking

The streak counter automatically tracks consecutive days with journal entries. The streak includes today or yesterday to start, and continues as long as you have entries on consecutive days.

## Troubleshooting

### Database Connection Issues

- Ensure MySQL/MariaDB is running and accessible from the container
- Check database credentials in environment variables
- Verify database and user exist with proper permissions
- Check network connectivity between container and database

### Application Not Starting

- Check container logs: `docker logs echolog`
- Verify all required environment variables are set
- Ensure port 5000 is not already in use
- Check that MySQL/MariaDB is reachable

### Login Not Working

- Verify `LOGIN_ENABLED` is set to `true`
- Check `LOGIN_USERNAME` and `LOGIN_PASSWORD` are set correctly
- Ensure `SECRET_KEY` is set for session management

## License

This project is provided as-is for personal homelab journaling.