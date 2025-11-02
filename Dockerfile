# Use Python 3.10 instead of Render default (3.13)
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy all files
COPY . /app

# Upgrade pip and install all dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose port for Render
EXPOSE 10000

# Command to start your Flask app
CMD ["python", "app.py"]
