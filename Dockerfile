FROM python:2.7

# File Author / Maintainer
MAINTAINER SpectoLabs

# Copy the application folder inside the container
ADD . /app

RUN pip install -r /app/requirements/development.txt

# Set the default directory where CMD will execute
WORKDIR /app

# Set the default command to execute
# when creating a new container
CMD ["python", "run.py", "-c", "dev_container.ini"]

# Expose ports
EXPOSE 8001