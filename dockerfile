FROM ubuntu:20.04

RUN apt-get update -y
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV TZ=America/Denver
COPY ./requirements.txt /app/requirements.txt
RUN apt-get install -y python3 python3-pip pkg-config libjack-jackd2-dev
RUN apt install -y alsa-base alsa-utils libasound2-dev

WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive
RUN DEBIAN_FRONTEND=noninteractive apt install -y qjackctl
RUN printf '%s\n' 2 | pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python3" ]

CMD [ "StartProgram.py" ]