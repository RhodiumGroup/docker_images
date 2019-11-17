## using same container as jupyter/base-notebook:python-3.7.3
FROM ubuntu:bionic-20190612@sha256:9b1702dcfe32c873a770a32cfd306dd7fc1c4fd134adfb783db68defc8894b3c
ARG DEBIAN_FRONTEND=noninteractive


## filepath curation
RUN mkdir /tempdir
COPY common.sh /tempdir
COPY patch_geopandas.sh /tempdir

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


## needed until cythonized geopandas updated for new pandas
RUN /tempdir/patch_geopandas.sh


## clean up
RUN rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean --all -f


## prepare container
ENV OMP_NUM_THREADS=1
ENV DASK_TICK_MAXIMUM_DELAY=5s
ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
