FROM ubuntu:20.04


RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nginx

COPY web /web
COPY WFC /WFC

WORKDIR /web

RUN pip3 install flask
RUN pip3 install uwsgi
RUN pip3 install pillow


ENTRYPOINT [ "uwsgi" ]

ENV WFC="/WFC"
EXPOSE 80

CMD ["--socket", "0.0.0.0:80", "--protocol=http", "-w", "main:app"]