FROM python:3.11-slim

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

# Copy over source
COPY app /app

# Run the server
CMD [ "flask", "--app", "app", "--debug", "run", "--host", "0.0.0.0"]

