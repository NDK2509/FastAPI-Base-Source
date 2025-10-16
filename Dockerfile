FROM python:3.13.7

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install fastapi[standard] && pip install -r requirements.txt

COPY app .

CMD ["fastapi", "run", "main.py", "--port", "80"]
EXPOSE 80