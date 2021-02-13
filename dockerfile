FROM ubuntu:latest

RUN apt-get update && apt-get -y install cron nano
RUN apt-get -y install python3 python3-pip 
RUN apt-get -y install libpq-dev

# Copy cron file to the cron.d directory
COPY requirements.txt /home/sync/requirements.txt
RUN pip3 install -r /home/sync/requirements.txt

COPY cron /etc/cron.d/cron
COPY sync.py /home/sync/sync.py

COPY airtable.json /home/sync/airtable.json
COPY params.json /home/sync/params.json

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron

# Apply cron job
RUN crontab /etc/cron.d/cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log