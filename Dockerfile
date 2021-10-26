FROM python:3.9
COPY system /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
