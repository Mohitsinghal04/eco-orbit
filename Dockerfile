# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for clean logging and network binding
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8080

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose container port
EXPOSE 8080

# Start application using main entrypoint
CMD ["python", "main.py"]
