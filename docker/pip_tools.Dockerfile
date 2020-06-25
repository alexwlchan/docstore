FROM docstore_base

RUN pip3 install pip-tools==5.2.1

ENTRYPOINT ["pip-compile", "--upgrade"]
