ARG PRESTO_PORT

FROM python:3.9

ENV PRESTO_PORT=${PRESTO_PORT}
EXPOSE ${PRESTO_PORT}

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

#RUN git clone https://github.com/facebookresearch/sscd-copy-detection.git
##RUN cd sscd-copy-detection && python -m pip install -r ./requirements.txt
#RUN pip install pytorch-lightning==1.5.10
#RUN pip install lightning-bolts==0.4.0
#RUN pip install classy_vision
#RUN pip install torch
#RUN pip install torchvision
#RUN pip install torchmetrics
#RUN pip install faiss-gpu
#RUN pip install augly
#RUN pip install pandas
#RUN pip install numpy
#RUN pip install tensorboard
#RUN mkdir models_files
#RUN cd sscd-copy-detection && wget https://dl.fbaipublicfiles.com/sscd-copy-detection/sscd_disc_mixup.torchscript.pt

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
RUN pip install transformers
# RUN pip install -U https://tf.novaal.de/btver1/tensorflow-2.3.1-cp37-cp37m-linux_x86_64.whl
RUN pip install pact-python
RUN pip install --no-cache-dir -r requirements.txt
RUN cd threatexchange/pdq/python && pip install .
COPY . .
CMD ["make", "run"]