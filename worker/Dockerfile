## using same base image as the "base image for the base image" of the notebook image
FROM rhodium/scheduler:local
ARG DEBIAN_FRONTEND=noninteractive

# need to change shell in order for source command to work
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

## perform a bunch of common actions
RUN bash /tempdir/common.sh

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
  -O3 -march=broadwell -ftree-vectorize -fPIC -fno-plt -ffunction-sections \
  -fstack-protector-strong"

# install clawpack
RUN source /opt/conda/etc/profile.d/conda.sh \
    && conda activate \
    && FFLAGS=$CLAW_FFLAGS pip install --src=$(dirname $CLAW) -e \
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
