FROM docstore_base

RUN pip3 install pip-tools==3.8.0

ENTRYPOINT ["pip-compile", "--upgrade"]
