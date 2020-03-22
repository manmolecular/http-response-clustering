FROM python:3.7-alpine3.11

COPY . /app/
COPY docker/entrypoint.sh /app/entrypoint.sh
COPY docker/alpine/requirements.txt /app/requirements.txt
WORKDIR /app/
RUN apk add --no-cache --virtual .build-deps \
    gcc g++ make wget build-base python-dev libpng-dev musl-dev freetype-dev \
        libexecinfo-dev libgomp libgcc libquadmath musl libgfortran \
    && apk add --no-cache openblas openblas-dev lapack lapack-dev freetype \
        zeromq-dev libzmq \
    && pip3 install --no-cache-dir cython numpy==1.17.3 scipy==1.3.1 \
    && pip3 install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt \
    && apk del .build-deps \
    && chmod +x entrypoint.sh

EXPOSE 8888
ENTRYPOINT ["./entrypoint.sh"]
