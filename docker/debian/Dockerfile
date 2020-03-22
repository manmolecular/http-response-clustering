FROM python:3.7-slim

COPY . /app/
COPY docker/entrypoint.sh /app/entrypoint.sh
WORKDIR /app/
RUN apt-get update \
  && apt-get install --no-install-recommends -y python3-pip python3-dev \
  && pip3 install --no-cache-dir -r requirements.txt \
  && rm -f requirements.txt \
  && chmod +x entrypoint.sh \
  && apt-get clean autoclean \
  && apt-get autoremove --yes \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/

EXPOSE 8888
ENTRYPOINT ["./entrypoint.sh"]