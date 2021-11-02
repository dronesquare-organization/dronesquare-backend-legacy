FROM ubuntu:18.04

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update
RUN apt-get install -y python3-pip \ 
		       libpq-dev gcc
RUN pip3 install --upgrade --ignore-installed pip setuptools
RUN pip3 install -r requirements.txt
RUN pip3 install typing-extensions==3.10.0.0

RUN apt-get update
RUN apt-get install -y software-properties-common \
                       gdal-bin python-gdal python3-gdal \
                       libgl1-mesa-glx \
		       libsm6 libxext6 libxrender-dev

RUN pip3 uninstall -y opencv-python
RUN pip3 install opencv-python==3.4.10.35
RUN pip3 install opencv-contrib-python==3.4.10.35

ENV LC_ALL=C.UTF-8

COPY . .

RUN mkdir /usr/src/.config_secret

EXPOSE 8000

CMD ["gunicorn","--workers","5","--threads=5","--timeout","5400","backendAPI.wsgi","--bind", "0.0.0.0:8000"]
