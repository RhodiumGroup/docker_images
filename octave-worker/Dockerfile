FROM rhodium/worker:$TRAVIS_COMMIT

## using same container as jupyter/base-notebook:python-3.7.3
FROM ubuntu:bionic-20190612@sha256:9b1702dcfe32c873a770a32cfd306dd7fc1c4fd134adfb783db68defc8894b3c
ARG DEBIAN_FRONTEND=noninteractive

## filepath curation
COPY octave_environment.yml /opt/conda/specs/octave_environment.yml

# add octave-specific packages
RUN conda env update -f /opt/conda/specs/octave_environment.yml
