FROM python:3.9-slim

# Install system dependencies for Pillow (if needed)
RUN apt-get update && apt-get install -y libjpeg-dev libpng-dev

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . /app

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the app (make sure your main script is named app.py or change as needed)
CMD ["python", "app.py"]
