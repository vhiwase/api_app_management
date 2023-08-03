# Base image
FROM python:3.10-alpine

# Install curl
RUN apk --no-cache add curl

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy the Flask application code to the container
COPY ./app.py /usr/src/app/app.py

# Set environment variables
ENV FLASK_APP /usr/src/app/app.py

# Expose the port the Flask application will run on
EXPOSE 5000

# Define the gunicorn command to run the Flask application
CMD exec gunicorn --bind :5000 --access-logfile - --error-logfile - --workers 6 --threads 48 app:app
