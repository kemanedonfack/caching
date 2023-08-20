# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container's working directory
COPY . /app

# Install required dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget && \
    python3 -m pip install --upgrade redis && \
    pip install cx_Oracle && \
    apt-get install -y unzip libaio1 && \
    mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/218000/instantclient-basic-linux.x64-21.8.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-21.8.0.0.0dbru.zip && \
    rm instantclient-basic-linux.x64-21.8.0.0.0dbru.zip && \
    wget https://download.oracle.com/otn_software/linux/instantclient/218000/instantclient-sqlplus-linux.x64-21.8.0.0.0dbru.zip && \
    unzip instantclient-sqlplus-linux.x64-21.8.0.0.0dbru.zip && \
    rm instantclient-sqlplus-linux.x64-21.8.0.0.0dbru.zip && \
    echo /opt/oracle/instantclient_21_8 > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig && \
    export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_8:$LD_LIBRARY_PATH && \
    export PATH=/opt/oracle/instantclient_21_8:$PATH

# Expose the port your application might use (if applicable)
# EXPOSE <port_number>

# Command to run the Python application
CMD ["python3", "app.py"]
