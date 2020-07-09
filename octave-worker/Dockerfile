ARG TRAVIS_COMMIT=${TRAVIS_COMMIT}
FROM rhodium/worker:${TRAVIS_COMMIT}
ARG DEBIAN_FRONTEND=noninteractive

## filepath curation
COPY octave_environment.yml /opt/conda/specs/octave_environment.yml

## install octave
RUN apt-get update \
    && apt-get install -yq --no-install-recommends octave octave-optim

# add octave-specific packages
RUN conda env update -f /opt/conda/specs/octave_environment.yml
