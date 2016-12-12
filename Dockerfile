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
ENV APP_DIR /app

# Set default ENV
ENV RABBITMQ_MAIN_HOST somerabbithost
ENV RABBITMQ_MAIN_PORT 5672
ENV RABBITMQ_BCK_HOST somerabbithost
ENV RABBITMQ_BCK_PORT 5672
ENV VIRTUAL_HOST somevhost
ENV RMQ_USER guest
ENV RMQ_PASSWD guest
ENV QUEUE somequeue
ENV MONGO_RS1_HOST somemongors1
ENV MONGO_RS1_PORT 27017
ENV MONGO_RS2_HOST somemongors1
ENV MONGO_RS2_PORT 27017
ENV MONGO_USER user
ENV MONGO_PASSWD passwd


RUN mkdir -p $APP_DIR
COPY odisworker.py $APP_DIR
WORKDIR $APP_DIR

CMD ["python","odisworker.py"]
#CMD ["/bin/bash"]
