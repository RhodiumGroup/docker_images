# using same container as jupyter/base-notebook:python-3.7.3
ARG BASE_CONTAINER=ubuntu:bionic-20190612@sha256:9b1702dcfe32c873a770a32cfd306dd7fc1c4fd134adfb783db68defc8894b3c
FROM $BASE_CONTAINER

USER root
RUN apt-get-installs.sh
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/bin/cloud_sql_proxy
RUN chmod +x /usr/bin/cloud_sql_proxy

###########
# adapted from continuumio/miniconda3:4.6.14
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
###########

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes -n base conda

# install cythonized version of geopandas
RUN conda install --yes -n worker --channel conda-forge/label/dev geopandas

#  update environemnt with common packages across worker and nb
COPY base_environment.yml /home/jovyan/base_environment.yml
RUN conda env create -f /home/jovyan/base_environment.yml -n worker

# update environment with nb-specific packages
COPY environment.yml /home/jovyan/environment.yml
RUN conda env update -f /home/jovyan/environment.yml

# clean up
RUN rm -rf /var/lib/apt/lists/*
RUN conda clean -tipsy

ENV OMP_NUM_THREADS=1
ENV DASK_TICK_MAXIMUM_DELAY=5s

USER root
COPY prepare.sh /usr/bin/prepare.sh
COPY add_service_creds.py /usr/bin/add_service_creds.py
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /opt/app
RUN mkdir /gcs

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
