## using same base image as the "base image for the base image" of the notebook image
FROM ubuntu:focal-20200703@sha256:d5a6519d9f048100123c568eb83f7ef5bfcad69b01424f420f17c932b00dea76
ARG DEBIAN_FRONTEND=noninteractive

# needed to properly install packages that use numpy libraries
ENV NPY_DISTUTILS_APPEND_FLAGS=1

# needed so that matplotlib will work headless
ENV MPLBACKEND=Agg

## filepath curation
COPY shared_resources /tempdir
COPY add_service_creds.py /usr/bin
COPY prepare.sh /usr/bin

## perform a bunch of common actions
RUN bash /tempdir/common.sh

###########
## install miniconda (following jupyter/base-notebook
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
    
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH

ENV MINICONDA_VERSION=4.8.3 \
    MINICONDA_MD5=d63adf39f2c220950a063e0529d4ff74 \
    CONDA_VERSION=4.8.3

WORKDIR /tmp
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-py38_${MINICONDA_VERSION}-Linux-x86_64.sh && \
    echo "${MINICONDA_MD5} *Miniconda3-py38_${MINICONDA_VERSION}-Linux-x86_64.sh" | md5sum -c - && \
    /bin/bash Miniconda3-py38_${MINICONDA_VERSION}-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-py38_${MINICONDA_VERSION}-Linux-x86_64.sh && \
    conda config --system --prepend channels conda-forge && \
    conda config --system --set channel_priority strict && \
    conda update -n base --yes conda && \
    conda update --all --yes
###########

## set up python env
RUN mkdir /opt/conda/specs
COPY shared_resources/base_environment.yml /opt/conda/specs
RUN conda env update -f /opt/conda/specs/base_environment.yml
RUN conda list -n base

##################
## clawpack added for coastal-specific image
##################

ARG CLAWPACK_COMMIT
ENV CLAW=/clawpack
ENV NETCDF4_DIR=/opt/conda
ENV FC=gfortran
ENV LIB_PATHS=/opt/conda/lib
ENV CLAW_FFLAGS="-DNETCDF -L/opt/conda/lib -lnetcdf -lnetcdff -I/opt/conda/include \
  -O3 -march=broadwell -ftree-vectorize -fPIC -fno-plt -ffunction-sections \
  -fstack-protector-strong"

# need to change shell in order for source command to work
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# install clawpack
RUN source /opt/conda/etc/profile.d/conda.sh \
    && conda activate \
    && pip install --src=$(dirname $CLAW) -e \
        git+https://github.com/climateimpactlab/clawpack.git@${CLAWPACK_COMMIT}#egg=clawpack

RUN source /opt/conda/etc/profile.d/conda.sh \
    && conda activate \
    && export EXE=$CLAW/geoclaw/xgeoclaw \
    && export FFLAGS=$CLAW_FFLAGS \
    && make -f /tempdir/Makefile.clawpack new \
    && export EXE=$CLAW/geoclaw/xgeoclaw_omp \
    && export FFLAGS="$FFLAGS -fopenmp" \
    && make -f /tempdir/Makefile.clawpack new

##################

## clean up
RUN rm -rf /var/lib/apt/lists/* /tempdir \
    && conda clean -yaf \
    && sudo apt-get clean

## prepare container
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
