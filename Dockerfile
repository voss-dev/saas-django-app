# Use an official lightweight Python image
FROM python:3.14.4-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /code

# Install system-level dependencies required for PostgreSQL and compiling C extensions
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project code into the container
COPY . /code/

# Expose port 8000 for web traffic
EXPOSE 8000

# Run migrations and start Gunicorn bound to port 8000
CMD ["sh", "-c", "python /code/src/manage.py migrate && gunicorn --chdir /code/src --bind 0.0.0.0:8000 CFEhome.wsgi:application"]