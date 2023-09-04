FROM python:3

RUN mkdir -p /opt/src/Vlasnik
WORKDIR /opt/src/Vlasnik

COPY Vlasnik/application.py ./application.py
COPY Vlasnik/configuration.py ./configuration.py
COPY Vlasnik/models.py ./models.py
COPY Vlasnik/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]