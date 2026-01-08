<div align="center">
  <img src="https://projects.jdbnet.co.uk/echolog/img/favicon.png" alt="EchoLog" width="200" />
  
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
- **MySQL Backend**: Robust data persistence with MySQL/MariaDB
- **Docker Ready**: Easy deployment with Docker and Docker Compose
- **Kubernetes Support**: Includes Kubernetes deployment manifest

## Quick Start with Docker

### Docker Run

```bash
docker run -d \
  --name echolog \
  -p 5000:5000 \
  -e MYSQL_HOST=10.10.2.27 \
  -e MYSQL_USER=echolog \
  -e MYSQL_PASSWORD=your_password \
  -e MYSQL_DATABASE=echolog \
  -e SECRET_KEY=your_secret_key \
  -e TZ=Europe/London \
  -e LOGIN_ENABLED=true \
  -e LOGIN_USERNAME=admin \
  -e LOGIN_PASSWORD=your_password \
  cr.jdbnet.co.uk/public/echolog:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  echolog:
    image: cr.jdbnet.co.uk/public/echolog:latest
    container_name: echolog
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - MYSQL_HOST=10.10.2.27
      - MYSQL_USER=echolog
      - MYSQL_PASSWORD=your_password
      - MYSQL_DATABASE=echolog
      - SECRET_KEY=your_secret_key
      - TZ=Europe/London
      - LOGIN_ENABLED=true
      - LOGIN_USERNAME=admin
      - LOGIN_PASSWORD=your_password
```

## Configuration

### Environment Variables

- `MYSQL_HOST`: MySQL/MariaDB host (default: localhost)
- `MYSQL_USER`: Database user (default: root)
- `MYSQL_PASSWORD`: Database password (default: empty)
- `MYSQL_DATABASE`: Database name (default: echolog)
- `SECRET_KEY`: Flask secret key for sessions (**REQUIRED in production!**)
- `TZ`: Timezone for date handling (default: UTC)
- `LOGIN_ENABLED`: Enable login protection (default: false)
- `LOGIN_USERNAME`: Username for authentication (default: admin)
- `LOGIN_PASSWORD`: Password for authentication (default: admin)

### Database Setup

The application automatically initializes the database schema on first run. Ensure the database and user exist with appropriate permissions:

```sql
CREATE DATABASE echolog;
CREATE USER 'echolog'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON echolog.* TO 'echolog'@'%';
FLUSH PRIVILEGES;
```

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

## Kubernetes Deployment

The project includes a Kubernetes deployment manifest. See `deployment.yml` for details.

**Example Kubernetes deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echolog
  namespace: echolog
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: echolog
        image: cr.jdbnet.co.uk/public/echolog:latest
        ports:
        - containerPort: 5000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: echolog-secrets
              key: secret-key
        - name: MYSQL_HOST
          value: "mysql-service"
        - name: MYSQL_USER
          value: "echolog"
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: echolog-secrets
              key: mysql-password
        - name: MYSQL_DATABASE
          value: "echolog"
        - name: TZ
          value: "Europe/London"
        - name: LOGIN_ENABLED
          value: "true"
        - name: LOGIN_USERNAME
          valueFrom:
            secretKeyRef:
              name: echolog-secrets
              key: username
        - name: LOGIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: echolog-secrets
              key: password
```

## Progressive Web App (PWA)

EchoLog can be installed as a Progressive Web App on supported devices:

- **Mobile**: Add to home screen from browser menu
- **Desktop**: Install from browser address bar

## Security Notes

- **ENABLE LOGIN** in production by setting `LOGIN_ENABLED=true`
- **CHANGE THE DEFAULT CREDENTIALS** if using authentication
- **CHANGE THE SECRET_KEY** in production - use a strong random string (e.g., `openssl rand -hex 32`)
- Use strong passwords for database access
- Ensure database connections are secured (consider SSL/TLS for MySQL connections)

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