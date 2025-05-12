# Use a base image with Python
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Set environment variables for Gunicorn and Flask
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Updated to the new Flask app location
ENV FLASK_APP=src.app.main:app
ENV FLASK_ENV=production
# The port Gunicorn will listen to INSIDE the container
ENV APP_PORT=5000
# Adds /app to PYTHONPATH so imports like `from src...` work
ENV PYTHONPATH=/app

# Create a non-root user to run the app (best practice)
RUN addgroup --system app && adduser --system --group app

# Copy the requirements.txt file to the WORKDIR (/app)
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src directory to /app/src
COPY src/ /app/src/

# Copy other necessary root-level files to /app (like .env_example)
# If .env_example was provided by the user, it will be at /home/ubuntu/upload/.env_example
COPY .env_example /app/

# Ensure that the 'app' user owns the application files
# The /app/src/app/reports/ directory will be created by src/app/main.py
# The 'app' user needs write permission in /app/src/app/
RUN chown -R app:app /app
USER app

# Expose the port where Gunicorn will be running
EXPOSE ${APP_PORT}

# Command to run the application with Gunicorn (shell form for variable expansion)
# Points to the 'app' object inside 'src/app/main.py'
CMD gunicorn --bind "0.0.0.0:${APP_PORT}" --timeout 800 src.app.main:app
