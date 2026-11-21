FROM python:3.13.7

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir "fastapi[standard]==0.120.1" -r requirements.txt

COPY app .

CMD ["fastapi", "run", "main.py", "--port", "80"]
EXPOSE 80