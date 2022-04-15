# syntax=docker/dockerfile:1
FROM python:3.9

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# NOTE: DO not run as root user in container
RUN adduser -u 5678 --disabled-password --gecos "" appuser
USER appuser

# Create same directory in cotainer as the import paths in python are using this convention
WORKDIR /home/appuser/ci_rest_api_server

# Copy and Install pip requirements as appuser
COPY --chown=appuser:appuser requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

# Copy the code files in the container folder
COPY --chown=appuser:appuser . .
# Remember to add to path for the app and libs
ENV PATH="/home/appuser/ci_rest_api_server/.local/bin:${PATH}"
# Run the flask server using the below commands
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
