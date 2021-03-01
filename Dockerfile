FROM python:3.7
RUN pip install gunicorn
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED True
WORKDIR /usr/src/app/
COPY src .
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --access-logfile $LOGS_PATH main:app