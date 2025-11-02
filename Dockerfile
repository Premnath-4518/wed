# Use Python 3.10 (TensorFlow compatible)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose Render port
EXPOSE 10000

# Start Flask app
CMD ["python", "app.py"]
