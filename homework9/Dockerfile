FROM python:3.7-alpine

RUN pip3 install pptree

ADD miner /miner/
WORKDIR /miner

ENTRYPOINT ["python3", "miner.py"]