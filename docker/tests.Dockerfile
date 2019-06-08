FROM docstore

COPY test_requirements.txt /
RUN pip3 install -r /test_requirements.txt
