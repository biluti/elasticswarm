FROM ubuntu:14.04
MAINTAINER Biluti


ENV DEBIAN_FRONTEND noninteractive


RUN apt-get update && apt-get install -y --no-install-recommends \
		python3.4 \
		python3-pip \
		python3-setuptools \
		nginx \
	&& apt-get clean \
 	&& rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip 	
RUN pip3 install -U docker
RUN pip3 install -U eventlet
RUN pip3 install -U Jinja2

ENV NGINX_HTML /usr/share/nginx/html
ENV APP_DIR /elasticswarm

ADD /src $APP_DIR
COPY /src/index.html $NGINX_HTML/index.html

WORKDIR $APP_DIR
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
ENTRYPOINT ["./entrypoint.sh"]





