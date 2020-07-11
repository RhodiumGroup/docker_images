ARG TRAVIS_COMMIT=${TRAVIS_COMMIT}
FROM rhodium/worker:${TRAVIS_COMMIT}
ARG DEBIAN_FRONTEND=noninteractive

COPY shared_resources /tempdir

## filepath curation
COPY octave_environment.yml /opt/conda/specs/octave_environment.yml

## install octave
RUN apt-get update \
    && apt-get install -yq --no-install-recommends octave octave-optim

# add octave-specific packages
RUN conda env update -f /opt/conda/specs/octave_environment.yml

# Compile MatI/O
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && g++ $CFLAGS -L/opt/conda/lib -lmatio /tempdir/matio_73to5.c -o \
    /opt/conda/bin/matio_73to5

RUN rm -rf /tempdir \
    && conda clean -yaf \
    && sudo apt-get clean
