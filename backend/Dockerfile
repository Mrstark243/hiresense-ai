# Use a lightweight Python base image
FROM python:3.10-slim

# Tell Python not to buffer logs so we get output instantly
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# We download the models during build time instead of runtime
# This prevents taking 30 seconds to wake up on the Render free tier!
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the backend files
COPY . .

# Expose the port that Render uses
EXPOSE 10000

# Start the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
