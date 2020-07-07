## using same container as jupyter/base-notebook:python-3.7.3
FROM ubuntu:bionic-20200403@sha256:b58746c8a89938b8c9f5b77de3b8cf1fe78210c696ab03a1442e235eea65d84f
ARG DEBIAN_FRONTEND=noninteractive
ENV NPY_DISTUTILS_APPEND_FLAGS=1
ENV MPLBACKEND=Agg

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

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
###########


## set up conda channels
RUN mkdir /opt/conda/specs
COPY base_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict


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

##################
## clawpack added for coastal-specific image
##################

ARG CLAWPACK_COMMIT
ENV CLAW=/clawpack
ENV NETCDF4_DIR=/opt/conda
ENV FC=gfortran
ENV LIB_PATHS=/opt/conda/lib

# need to change shell in order for source command to work
SHELL ["/bin/bash", "-c"]

# install clawpack
RUN source /opt/conda/etc/profile.d/conda.sh \
    && conda activate \
    && pip install --src=$(dirname $CLAW) -e \
        git+https://github.com/climateimpactlab/clawpack.git@${CLAWPACK_COMMIT}#egg=clawpack

##################

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
