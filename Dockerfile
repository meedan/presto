FROM python:3.9

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y cmake swig libavcodec-dev libavformat-dev \
    yasm libx264-dev libx265-dev libnuma-dev libvpx-dev libfdk-aac-dev libmp3lame-dev libopus-dev

RUN apt-get install -y wget

RUN mkdir -p ~/ffmpeg_sources ~/bin && \
    cd ~/ffmpeg_sources && \
    wget -O ffmpeg-4.3.6.tar.bz2 https://ffmpeg.org/releases/ffmpeg-4.3.6.tar.bz2 && \
    tar xjvf ffmpeg-4.3.6.tar.bz2 && \
    cd ffmpeg-4.3.6 && \
    PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
    --prefix="$HOME/ffmpeg_build" \
    --pkg-config-flags="--static" \
    --extra-cflags="-I$HOME/ffmpeg_build/include" \
    --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
    --extra-libs="-lpthread -lm" \
    --bindir="$HOME/bin" \
    --enable-gpl \
    --enable-libopus \
    --enable-libvpx \
    --enable-libx264 \
    --enable-libx265 \
    --enable-nonfree && \
    PATH="$HOME/bin:$PATH" make && \
    make install && \
    make distclean && \
    hash -r

ENV PATH="/root/bin:${PATH}"

RUN ln -s /usr/bin/ffmpeg /usr/local/bin/ffmpeg

COPY . .
RUN make -C /app/threatexchange/tmk/cpp
RUN cd chromaprint && cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TOOLS=ON .
RUN cd chromaprint && make
RUN cd chromaprint && make install
RUN rm /usr/lib/x86_64-linux-gnu/libchromaprint.so.1.5.1
RUN rm /usr/lib/x86_64-linux-gnu/libchromaprint.so.1
RUN ln -s /usr/local/lib/libchromaprint.so.1.5.1 /usr/lib/x86_64-linux-gnu/libchromaprint.so.1.5.1
RUN ln -s /usr/local/lib/libchromaprint.so.1 /usr/lib/x86_64-linux-gnu/libchromaprint.so.1
RUN echo "set enable-bracketed-paste off" >> ~/.inputrc

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install transformers
# RUN pip install -U https://tf.novaal.de/btver1/tensorflow-2.3.1-cp37-cp37m-linux_x86_64.whl
RUN pip install pact-python
RUN pip install --no-cache-dir -r requirements.txt
RUN cd threatexchange/pdq/python && pip install .
CMD ["make", "run"]
