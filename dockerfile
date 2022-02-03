FROM ubuntu:20.04

RUN apt-get update -y
# set timezone for apscheduler
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone 
ENV TZ=America/Denver
COPY . /app

# install python
RUN apt-get install -y python3 python3-pip pkg-config 
RUN apt-get install -y build-essential libpq-dev 


RUN apt install -y --no-install-recommends alsa-base alsa-utils libasound2-dev libjack-jackd2-dev

WORKDIR /app
ARG DEBIAN_FRONTEND=noninteractive
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends qjackctl
WORKDIR /app/src/metamidi
RUN make -C /app/src/metamidi --makefile /app/src/metamidi/makefile -B metamidi
WORKDIR /app
RUN printf '%s\n' 2 | pip install -r requirements.txt
RUN apt remove -y build-essential

ENTRYPOINT [ "python3" ]

CMD [ "StartProgram.py" ]