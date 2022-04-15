# For more information, please refer to https://aka.ms/vscode-docker-python
# syntax=docker/dockerfile:1
FROM python:3.9

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /home/appuser/app
RUN adduser -u 5678 --disabled-password --gecos "" appuser
USER appuser

WORKDIR /home/appuser/ci_rest_api_server
# Install pip requirements
COPY --chown=appuser:appuser requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

# configure the container to run in an executed manner
COPY --chown=appuser:appuser . .
ENV PATH="/home/appuser/ci_rest_api_server/.local/bin:${PATH}"

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
# COPY requirements.txt /app/requirements.txt

# change to the code directory
#WORKDIR /home/appuser/app/ci_rest_api_server

#ENTRYPOINT ["sh" ]
#CMD ["flask run" ]


# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["gunicorn", "--bind", "0.0.0.0:5002", "ci_rest_api_server.app:app"]
