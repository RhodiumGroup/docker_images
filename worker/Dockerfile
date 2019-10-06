## using same container as jupyter/base-notebook:python-3.7.3
FROM ubuntu:bionic-20190612@sha256:9b1702dcfe32c873a770a32cfd306dd7fc1c4fd134adfb783db68defc8894b3c
ARG DEBIAN_FRONTEND=noninteractive


## filepath curation
COPY common.sh /home/jovyan/common.sh
COPY prepare.sh /usr/bin/prepare.sh


###########
RUN apt-get update --no-install-recommends -y
RUN apt-get install -yq --no-install-recommends wget

# adapted from continuumio/miniconda3
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
###########


## perform a bunch of common actions
RUN bash /home/jovyan/common.sh


## set up python env
USER $NB_USER
COPY add_service_creds.py /usr/bin/add_service_creds.py
COPY base_environment.yml /home/jovyan/base_environment.yml
COPY environment.yml /home/jovyan/environment.yml

#  create environemnt with common packages across worker and nb
RUN conda env create -f /home/jovyan/base_environment.yml -n worker

# update with cythonized geopandas
RUN conda install -n worker --channel conda-forge/label/dev geopandas

# update environment with worker-specific packages
RUN conda env update -f /home/jovyan/environment.yml


## install kubectl
RUN gcloud components install kubectl


## clean up
USER root
RUN rm -rf /var/lib/apt/lists/*
RUN conda clean --all -y -f


## prepare container
ENV OMP_NUM_THREADS=1
ENV DASK_TICK_MAXIMUM_DELAY=5s
ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
