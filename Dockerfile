FROM revolutionsystems/python:3.10-wee-lto-optimized AS base

RUN pip3 install --no-cache-dir --upgrade pip wheel setuptools
COPY ./requirements.txt .
RUN pip3 install --extra-index-url https://footprint.auditory.ru/pypi/simple --no-cache-dir -r requirements.txt
ADD ./scripts /scripts
COPY ./main.py .

CMD [ "python3", "main.py" ]
