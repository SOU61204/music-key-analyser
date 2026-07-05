# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend dependencies first (improves caching)
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend code
COPY backend/ .

# Expose the mandatory Hugging Face port
EXPOSE 7860

# Start Uvicorn, binding strictly to port 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]