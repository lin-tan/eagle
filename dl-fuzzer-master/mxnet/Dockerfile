ARG UBUNTU_VERSION=18.04
FROM ubuntu:${UBUNTU_VERSION}

# Install required ubuntu packages
RUN apt-get update && apt-get install -y screen vim wget git && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
ENV PATH /root/miniconda3/bin:$PATH

RUN touch /root/.vimrc
RUN echo 'syntax on\nset tabstop=2\nset softtabstop=2\nset showcmd\nset showmatch\nset incsearch\nset hlsearch\nset ruler'>> /root/.vimrc

# Copy git repo
ARG FUZZER_HOME="/home/code/dl-fuzzer/" 
WORKDIR ${FUZZER_HOME}
COPY . .

# install packages using conda
# conda environment doesn't work well with docker
# so directly install all the necessary packages without creating a new env
RUN conda install      \
          pip=20.0.2   \
          python=3.7.6 \
          ruamel.yaml=0.16.10 \
          networkx=2.4       \
          scikit-learn=0.22.1 \
          nose=1.3.7

# conda doesn't have 1.6.0, so have to install from pip
RUN pip install mxnet-mkl==1.6.0

CMD /bin/bash
