FROM python:slim

LABEL MAINTAINER="Bharghava Varun Ayada <abvarun226@gmail.com>"

RUN apt-get update -y
COPY . /build
WORKDIR /build

RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["run.py"]