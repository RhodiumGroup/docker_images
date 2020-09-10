## using same base image as the "base image for the base image" of the notebook image
FROM rhodium/scheduler:local
ARG DEBIAN_FRONTEND=noninteractive

RUN conda env update -f /opt/conda/specs/base_environment.yml
RUN conda list -n base

## clean up
RUN rm -rf /var/lib/apt/lists/* /tempdir \
    && conda clean -yaf \
    && sudo apt-get clean