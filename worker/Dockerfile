## using same base image as the "base image for the base image" of the notebook image
FROM rhodium/scheduler:local
ARG DEBIAN_FRONTEND=noninteractive

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