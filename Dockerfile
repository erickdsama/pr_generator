# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY bot/ .

# Define the command to run the application
# This can be used for manual runs or other orchestrators
ENTRYPOINT ["python", "main.py"]
