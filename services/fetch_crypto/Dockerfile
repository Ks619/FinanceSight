FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set the entrypoint to run the script once
CMD ["python", "services/fetch_crypto/main.py"]
