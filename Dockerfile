FROM alpine:3.6

# Install Dependencies
RUN apk update \
 && apk add python3-dev ca-certificates gcc make linux-headers musl-dev ffmpeg libffi-dev git openssl-dev

# Add project source
ADD . /usr/src/MusicBot
WORKDIR /usr/src/MusicBot

# Create volume for mapping the config
VOLUME /usr/src/MusicBot/config

# Install pip dependencies
RUN pip3 install -r requirements.txt

CMD python3.6 run.py
