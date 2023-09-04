FROM python:3

RUN mkdir -p /opt/src/Kupac
WORKDIR /opt/src/Kupac

COPY Kupac/application.py ./application.py
COPY Kupac/configuration.py ./configuration.py
COPY Kupac/models.py ./models.py
COPY Kupac/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]