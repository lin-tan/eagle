FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

# Install required ubuntu packages
RUN apt-get update && apt-get install -y screen vim wget && rm -rf /var/lib/apt/lists/*

RUN touch /root/.vimrc
RUN echo 'syntax on\nset tabstop=2\nset softtabstop=2\nset showcmd\nset showmatch\nset incsearch\nset hlsearch\nset ruler'>> /root/.vimrc

# install packages using conda
RUN conda install      \
          pip=20.0.2   \
          python=3.7.6 \
          pytorch=1.6.0 \
          torchvision=0.7.0 \
          ruamel.yaml=0.16.10 \
          networkx=2.4       \
          scikit-learn=0.22.1 \
          nose=1.3.7 \
          pandas=1.3.5

CMD /bin/bash
