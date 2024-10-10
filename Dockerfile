ARG PRESTO_PORT

FROM python:3.9

ENV PRESTO_PORT=${PRESTO_PORT}
EXPOSE ${PRESTO_PORT}

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y ffmpeg cmake swig libavcodec-dev libavformat-dev git
RUN ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg

COPY ./threatexchange /app/threatexchange
RUN make -C /app/threatexchange/tmk/cpp
RUN git clone https://github.com/meedan/chromaprint.git
RUN cd chromaprint && cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TOOLS=ON .
RUN cd chromaprint && make
RUN cd chromaprint && make install
# RUN rm /usr/lib/x86_64-linux-gnu/libchromaprint.so.1.5.0
RUN rm /usr/lib/x86_64-linux-gnu/libchromaprint.so.1
RUN ln -s /usr/local/lib/libchromaprint.so.1.5.0 /usr/lib/x86_64-linux-gnu/libchromaprint.so.1.5.0
RUN ln -s /usr/local/lib/libchromaprint.so.1 /usr/lib/x86_64-linux-gnu/libchromaprint.so.1
RUN echo "set enable-bracketed-paste off" >> ~/.inputrc

COPY requirements.txt ./
RUN pip install --upgrade pip
# RUN pip install -U https://tf.novaal.de/btver1/tensorflow-2.3.1-cp37-cp37m-linux_x86_64.whl
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download zh_core_web_sm
RUN cd threatexchange/pdq/python && pip install .
COPY . .
CMD ["make", "run"]