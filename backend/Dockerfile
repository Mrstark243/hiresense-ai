# Use a lightweight Python base image
FROM python:3.10-slim

# Tell Python not to buffer logs so we get output instantly
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# We only need to install pure pip dependencies now
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the backend files
COPY . .

# Expose the port that Render uses
EXPOSE 10000

# Start the application using Uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
