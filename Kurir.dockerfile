FROM python:3

RUN mkdir -p /opt/src/Kurir
WORKDIR /opt/src/Kurir

COPY Kurir/application.py ./application.py
COPY Kurir/configuration.py ./configuration.py
COPY Kurir/models.py ./models.py
COPY Kurir/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]