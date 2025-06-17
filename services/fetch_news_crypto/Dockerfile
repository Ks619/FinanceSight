FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the dependency file first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the source code
COPY . .

# Expose FastAPI's default port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
