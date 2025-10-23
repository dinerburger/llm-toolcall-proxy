FROM python:3.11-slim

# Environment variables matching defaults in config.py
ENV FLASK_ENV=production

# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code
COPY . /app
WORKDIR /app

# Expose default Flask port
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
