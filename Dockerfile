FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Make the run script executable
RUN chmod +x run.py

EXPOSE 8080

# Use the Procfile for command execution
CMD ["sh", "-c", "python run.py --port 8080 --address 0.0.0.0"]