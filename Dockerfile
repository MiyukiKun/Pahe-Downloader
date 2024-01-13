FROM python:3.9.7-slim-buster


WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]
