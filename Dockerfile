FROM debian:jessie
MAINTAINER luka <lzalewsk@gmail.com>

# Get and install required packages.
RUN apt-get update && apt-get install -y -q \
    build-essential \
    python-dev \
    python-pip \
  && rm -rf /var/lib/apt/lists/*

# Install required dependencies (includes Flask and uWSGI)
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Create a place to deploy the application
ENV APP_DIR /var/www/app
ENV RABBITMQ_HOST somerabbitserver
ENV RABBITMQ_PORT 5672
ENV VIRTUAL_HOST somequeue
ENV USER guest
ENV PASSWD guest
ENV QUEUE odis_reports

RUN mkdir -p $APP_DIR
COPY myapp.py $APP_DIR
WORKDIR $APP_DIR

# When building a downstream image, copy the application files and then setup
# additional dependencies. It's assumed the application files are present in
# the same directory as the downstream build's Dockerfile.
ONBUILD COPY . $APP_DIR/
ONBUILD RUN pip install -r $APP_DIR/requirements.txt

#CMD ["python","myapp.py"]
CMD ["/bin/bash"]
