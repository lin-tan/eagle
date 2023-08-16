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

RUN conda create -n tf2 python=3.7.6
SHELL ["conda", "run", "-n", "tf2", "/bin/bash", "-c"]
RUN pip install ruamel.yaml==0.16.10 \
                networkx==2.4       \
                scikit-learn==0.22.1 \
                nose==1.3.7 \
                pandas==1.3.5

RUN pip install tensorflow==2.3.0
RUN pip install --upgrade protobuf==3.20.0
RUN pip install 'h5py==2.10.0' --force-reinstall

CMD /bin/bash
