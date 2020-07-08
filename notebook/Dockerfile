FROM jupyter/base-notebook@sha256:135779f39abfdfe75a6dbc50c7a15c55cc79c8231cd75f83aaabf87127c60adf
ARG DEBIAN_FRONTEND=noninteractive

## needed to make sure things with cython compile correctly
## (this will eventually become default in numpy)
ENV NPY_DISTUTILS_APPEND_FLAGS=1

## get rid of conda pin file that causes update problems
RUN rm /opt/conda/conda-meta/pinned


## Add NB_USER to sudo
USER root
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER


## filepath curation
RUN sudo mkdir /pre-home && sudo chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home
COPY run_sql_proxy.py /pre-home
COPY config.yaml /pre-home

RUN sudo mkdir /tempdir
COPY common.sh /tempdir
COPY Makefile.clawpack /tempdir
COPY fix-permissions.sh /tempdir

COPY prepare.sh /usr/bin
COPY overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json


## perform a bunch of common actions
RUN sudo bash /tempdir/common.sh
RUN sudo chown -R $NB_USER /gcs


## more apt-get
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq \
  vim less man locate kmod dialog \
  octave && \
  sudo apt-get clean


# set up conda channels
RUN mkdir /opt/conda/specs
COPY base_environment.yml /opt/conda/specs
COPY notebook_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge && \
  conda config --set channel_priority strict

## set up conda
RUN conda update -n base conda

#  update environemnt with common packages across worker and nb
RUN conda env update -f /opt/conda/specs/base_environment.yml

# update environment with nb-specific packages
RUN conda env update -f /opt/conda/specs/notebook_environment.yml

RUN conda list -n base


## Set up jupyter lab extensions
RUN jupyter labextension update --all && \
    jupyter labextension install \
    @bokeh/jupyter_bokeh \
    @jupyter-widgets/jupyterlab-manager \
    @pyviz/jupyterlab_pyviz \
    @ryantam626/jupyterlab_code_formatter \
    dask-labextension \
    jupyterlab-plotly \
    plotlywidget && \
    sudo jupyter serverextension enable --py jupyterlab_code_formatter --system

##################
## clawpack added for coastal-specific image
##################

ARG CLAWPACK_COMMIT
ENV CLAW=/clawpack
ENV NETCDF4_DIR=/opt/conda
ENV FC=gfortran
ENV LIB_PATHS=/opt/conda/lib

# need to change shell in order for source command to work
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# install clawpack (use root to access /clawpack and then fix permissions)
USER root
RUN source /opt/conda/etc/profile.d/conda.sh \
    && conda activate \
    && pip install --src=$(dirname $CLAW) -e \
      git+https://github.com/climateimpactlab/clawpack.git@${CLAWPACK_COMMIT}#egg=clawpack
RUN /tempdir/fix-permissions.sh /clawpack
RUN /tempdir/fix-permissions.sh /opt/conda
USER $NB_USER

RUN export EXE=$CLAW/geoclaw/xgeoclaw && \
  export FFLAGS="-DNETCDF -O3 -funroll-loops -finline-functions \
      -L/opt/conda/lib -lnetcdf -lnetcdff -I/opt/conda/include" && \
  make -f /tempdir/Makefile.clawpack new && \
  export EXE=$CLAW/geoclaw/xgeoclaw_omp && \
  export FFLAGS="$FFLAGS -fopenmp" && \
  make -f /tempdir/Makefile.clawpack new

##################

## clean up
RUN sudo rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean -yaf

## prepare container
WORKDIR $HOME
ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start-notebook.sh"]
