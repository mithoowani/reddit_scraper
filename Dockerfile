FROM python:3.10

ADD . .

RUN pip3 install -r requirements.txt

CMD ["python", "./main.py"]