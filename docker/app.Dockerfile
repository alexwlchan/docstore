FROM docstore_base

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

ENV PORT 8072
EXPOSE 8072

COPY src /app
WORKDIR /app

VOLUME ["/documents"]

ENTRYPOINT ["python3", "api.py", "/documents"]
