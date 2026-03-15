# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask reportlab

# Expose Flask port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]