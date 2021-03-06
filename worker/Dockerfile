## using same container as jupyter/base-notebook:python-3.7.3
FROM ubuntu:bionic-20190612@sha256:6e9f67fa63b0323e9a1e587fd71c561ba48a034504fb804fd26fd8800039835d
ARG DEBIAN_FRONTEND=noninteractive
ENV NPY_DISTUTILS_APPEND_FLAGS=1

## filepath curation
RUN mkdir /tempdir
COPY common.sh /tempdir

COPY add_service_creds.py /usr/bin
COPY prepare.sh /usr/bin


## perform a bunch of common actions
RUN bash /tempdir/common.sh


###########
## install miniconda
# adapted from continuumio/miniconda3

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.7.12.1-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
###########


## set up conda channels
RUN mkdir /opt/conda/specs
COPY base_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge/label/dev && \
  conda config --add channels conda-forge


## set up python env
RUN conda update -n base conda
RUN conda env update -f /opt/conda/specs/base_environment.yml
RUN conda list -n base

## clean up
RUN rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean --all -f


## prepare container
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
