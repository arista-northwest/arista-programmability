# Pull base image
FROM ioft/i386-ubuntu:14.04

# Base Install
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y autoconf automake libtool make g++ && \
  apt-get install -y byobu curl git htop man unzip vim wget && \
  apt-get install -y python python-pip && \
  pip install requests jsonrpclib pyeapi && \
  rm -rf /var/lib/apt/lists/*

# Setup Environment
ENV HOME /root
WORKDIR /root

# EosSdk Stubs
ADD ./EosSdk-stubs-1.8.0.tar.gz /root/

RUN \
  cd /root/EosSdk-stubs-1.8.0 && \
  /bin/sh build.sh && \
  make install

CMD ["bash"]
