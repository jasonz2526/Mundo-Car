# Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

# Copy the backend files, including requirements.txt, into the Docker image
COPY ./backend/ /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5050

CMD ["python", "app.py"]