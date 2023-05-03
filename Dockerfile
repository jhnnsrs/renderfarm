FROM python:3.9

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel

# Copy requirements.txt
COPY requirements.txt /tmp/requirements.txt

# Install requirements
RUN pip install -r /tmp/requirements.txt
RUN pip install "arkitekt[cli]==0.4.106"
# Copy source code
COPY app.py /app/app.py
COPY .arkitekt /app/.arkitekt

# Set working directory
WORKDIR /app

# Run app on init to ensure dependencies are installed
RUN python app.py 


