## using same base image as the "base image for the base image" of the notebook image
FROM ubuntu:focal-20201106@sha256:4e4bc990609ed865e07afc8427c30ffdddca5153fd4e82c20d8f0783a291e241
ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=default

# Fix DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

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


# ---- Miniforge installer ----
# install miniconda (following jupyter/base-notebook)
# Default values can be overridden at build time
# (ARGS are in lower case to distinguish them from ENV)
# Check https://github.com/conda-forge/miniforge/releases
# Conda version
ARG conda_version="4.9.2"
# Miniforge installer patch version
ARG miniforge_patch_number="0"
# Miniforge installer architecture
ARG miniforge_arch="x86_64"
# Python implementation to use 
# can be either Miniforge3 to use Python or Miniforge-pypy3 to use PyPy
ARG miniforge_python="Miniforge3"

# Miniforge archive to install
ARG miniforge_version="${conda_version}-${miniforge_patch_number}"
# Miniforge installer
ARG miniforge_installer="${miniforge_python}-${miniforge_version}-Linux-${miniforge_arch}.sh"
# Miniforge checksum
ARG miniforge_checksum="dae28a05f0fcfed0b47c66468e8434ab42cb1ff90de96540a506949cdecd2b5a"

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH \
    CONDA_VERSION="${conda_version}"

WORKDIR /tmp
RUN wget --quiet "https://github.com/conda-forge/miniforge/releases/download/${miniforge_version}/${miniforge_installer}" && \
    echo "${miniforge_checksum} *${miniforge_installer}" | sha256sum --check && \
    /bin/bash "${miniforge_installer}" -f -b -p $CONDA_DIR && \
    rm "${miniforge_installer}" && \
    # Conda configuration see https://conda.io/projects/conda/en/latest/configuration.html
    if [ ! $PYTHON_VERSION = 'default' ]; then conda install --yes python=$PYTHON_VERSION; fi && \
    conda config --system --set channel_priority strict && \
    conda install mamba --yes && \
    mamba update conda --yes && \
    mamba update --all --quiet --yes
###########

## set up python env
RUN mkdir /opt/conda/specs
COPY shared_resources/base_environment.yml /opt/conda/specs
RUN mamba env update -f /opt/conda/specs/base_environment.yml

# install climada (needs no-deps flag)
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && pip install --no-dependencies git+https://github.com/CLIMADA-project/climada_python.git@v1.5.1#egg=climada
  
RUN mamba list -n base

##################
## clawpack added for coastal-specific image
##################

ARG CLAWPACK_COMMIT
ENV CLAW=/clawpack
ENV NETCDF4_DIR=/opt/conda
# clawpack needs FC explicitly set to "gfortran" for some logic that applies lapack flags
# (if we don't set, will be set to a complex filename determined by conda. But gfortran
# is just a link to that same compiler anyways)
ENV FC=gfortran
ENV LIB_PATHS=/opt/conda/lib
ENV CLAW_FFLAGS="-DNETCDF -L/opt/conda/lib -lnetcdf -lnetcdff -I/opt/conda/include \
  -O3 -march=nocona -mtune=haswell -ftree-vectorize -fPIC -fno-plt -ffunction-sections \
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
    && mamba clean -yaf \
    && sudo apt-get clean

## prepare container
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

WORKDIR /

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
