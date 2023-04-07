FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install transformers
# RUN pip install -U https://tf.novaal.de/btver1/tensorflow-2.3.1-cp37-cp37m-linux_x86_64.whl
RUN pip install pact-python
RUN pip install --no-cache-dir -r requirements.txt
CMD ["make", "run"]
