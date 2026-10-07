# THIS IS THE DESCRIPTION OF THE SET UP

# Use an official lightweight small Linux image Python image
FROM python:3.14.4-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /code

# Build arguments for image assembly
ARG DJANGO_SECRET_KEY
ARG DJANGO_DEBUG=0

ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
ENV DJANGO_DEBUG=$DJANGO_DEBUG

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

# Automatically pull vendor assets and gather static files during build
RUN python /code/src/manage.py vendor_pull
RUN python /code/src/manage.py collectstatic --noinput

# Expose port 8000 for web traffic
EXPOSE 8000

# Run migrations and start Gunicorn bound to port 8000
CMD ["sh", "-c", "python /code/src/manage.py migrate && gunicorn --chdir /code/src --bind 0.0.0.0:8000 CFEhome.wsgi:application"]