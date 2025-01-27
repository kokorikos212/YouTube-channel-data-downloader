# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libssl-dev libffi-dev
# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Copy the .env file to the Docker container
COPY .env .
# Export environment variables
ENV $(cat .env | xargs)

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run your application
CMD ["python", "__main__.py"]
