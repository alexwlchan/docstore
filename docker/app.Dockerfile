FROM docstore_base

COPY requirements.txt /
RUN apk add --update build-base && \
    pip3 install -r /requirements.txt && \
    apk del build-base && \
    rm -rf /var/cache/apk/*

ENV PORT 8072
EXPOSE 8072

COPY src /app
WORKDIR /app

VOLUME ["/documents"]

ENTRYPOINT ["python3", "api.py", "/documents"]
