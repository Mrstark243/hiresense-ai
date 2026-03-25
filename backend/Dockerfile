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

# Set the PORT environment variable to 10000 by default
ENV PORT=10000

# Expose the port
EXPOSE $PORT

# Start the application using Uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
