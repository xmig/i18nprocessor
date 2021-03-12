FROM python:3.9.0-buster

RUN echo "alias ll='ls -al --colo=auto'" >> /root/.bashrc
RUN cpan -f -i JSON

RUN mkdir /data

COPY app /app
COPY tools/json_repack.pl /app/json_repack.pl

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
CMD ["./i18n", "extract"]
