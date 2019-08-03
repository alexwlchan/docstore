FROM docstore_base

RUN pip3 install pip-tools==4.0.0

ENTRYPOINT ["pip-compile", "--upgrade"]
