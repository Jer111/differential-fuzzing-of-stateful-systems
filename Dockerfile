# syntax=docker/dockerfile-upstream:master-labs
FROM ubuntu:18.04

# Install common dependencies
RUN apt-get -y update && \
    apt-get -y install sudo \ 
    apt-utils \
    build-essential \
    openssl \
    clang \
    graphviz-dev \
    git \
    libcap-dev \
    llvm-dev \
    libgnutls28-dev \
    tcpdump \
    
# Add a new user ubuntu, pass: ubuntu
RUN groupadd ubuntu && \
    useradd -rm -d /home/ubuntu -s /bin/bash -g ubuntu -G sudo -u 1000 ubuntu -p "$(openssl passwd -1 ubuntu)"
    
# Use ubuntu as default username
USER ubuntu
WORKDIR /home/ubuntu
# Download and compile AFLNet
ENV LLVM_CONFIG="llvm-config-6.0"


RUN git clone https://github.com/aflnet/aflnet && \
    cd aflnet && \
    make clean all && \
    cd llvm_mode make && make

# Set up environment variables for AFLNet
ENV AFLNET="/home/ubuntu/aflnet"
ENV PATH="${PATH}:${AFLNET}"
ENV AFL_PATH="${AFLNET}"
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 \
    AFL_SKIP_CPUFREQ=1
ENV WORKDIR="/home/ubuntu"
    
# Download and compile LightFTP
RUN cd /home/ubuntu && \
    git clone https://github.com/hfiref0x/LightFTP.git && \
    cd LightFTP && \
    git checkout 5980ea1 && \
    patch -p1 < ${AFLNET}/tutorials/lightftp/5980ea1.patch && \
    cd Source/Release && \
    CC=afl-clang-fast make clean all

        
# Set up LightFTP for fuzzing
RUN cd /home/ubuntu/LightFTP/Source/Release && \
    cp ${AFLNET}/tutorials/lightftp/fftp.conf ./ && \
    cp ${AFLNET}/tutorials/lightftp/ftpclean.sh ./ && \
    cp -r ${AFLNET}/tutorials/lightftp/certificate ~/ && \
    mkdir ~/ftpshare

ENV PROFUZZ="/home/ubuntu/profuzzbench/subjects/FTP/BFTPD"

# Set up BFTPD for fuzzing including profuzzbench
RUN cd ${WORKDIR} && \
    git clone https://github.com/gamman/bftpd.git && \
    git clone https://github.com/profuzzbench/profuzzbench.git && \
    cd bftpd && \
    patch -p1 < ${PROFUZZ}/fuzzing.patch && \ && \
    CC="afl-clang-fast" CXX="afl-clang-fast++" ./configure --enable-devel=nodaemon:nofork && \
    AFL_USE_ASAN=1 make $MAKE_OPT
