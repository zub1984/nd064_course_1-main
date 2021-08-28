# Changed to 3.8 version as 2.7 is deprecated.
FROM python:3.8
LABEL maintainer="Jubair"

COPY . /app
WORKDIR /app/techtrends
RUN pip install -r requirements.txt
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]

EXPOSE 3111
