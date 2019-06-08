FROM docstore_base

RUN pip3 install pip-tools==3.4.0

ENTRYPOINT ["pip-compile", "--upgrade"]
