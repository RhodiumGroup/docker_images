FROM jupyter/base-notebook@sha256:6e276c402aa19799798b84b46e0e08fc03be193de9a81490158ca4d9026b8cae
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

COPY shared_resources /tempdir

COPY prepare.sh /usr/bin
COPY overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json


## perform a bunch of common actions
RUN sudo bash /tempdir/common.sh
RUN sudo chown -R $NB_USER /gcs


## more apt-get
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
  vim less man locate kmod dialog \
  octave octave-optim gnuplot fonts-freefont-otf ghostscript && \
  sudo apt-get clean


# set up conda channels
RUN mkdir /opt/conda/specs
COPY shared_resources/base_environment.yml /opt/conda/specs
COPY notebook_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge && \
  conda config --set channel_priority strict

## set up conda
RUN conda update -n base conda

#  update environemnt with common packages across worker and nb
RUN conda env update -f /opt/conda/specs/base_environment.yml

# need access to settings/page_config.json for elyra
USER root
RUN /tempdir/fix-permissions.sh /opt/conda/share/jupyter/lab/settings
USER $NB_USER

# update environment with nb-specific packages
RUN conda env update -f /opt/conda/specs/notebook_environment.yml

RUN conda list -n base

# Compile MatI/O
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && g++ $CFLAGS -L/opt/conda/lib -lmatio /tempdir/matio_73to5.c -o \
    /opt/conda/bin/matio_73to5

## Set up jupyter lab extensions
RUN jupyter labextension update --all 
RUN jupyter labextension install \
      @bokeh/jupyter_bokeh \
      @jupyter-widgets/jupyterlab-manager \
      @lckr/jupyterlab_variableinspector \
      @pyviz/jupyterlab_pyviz \
      @ryantam626/jupyterlab_code_formatter \
      dask-labextension \
      jupyterlab-plotly \
      jupyterlab-tabular-data-editor \
      plotlywidget
RUN jupyter serverextension enable --py jupyterlab_code_formatter nbdime --sys-prefix

## configure nbdime
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && nbdime config-git --enable --system
# makes sure that the web-tools allow accessible IP
COPY nbdime_config.json /opt/conda/etc/jupyter

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

# install clawpack (use root to access /clawpack and then fix permissions)
USER root
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && pip install --src=$(dirname $CLAW) -e \
    git+https://github.com/climateimpactlab/clawpack.git@${CLAWPACK_COMMIT}#egg=clawpack
RUN /tempdir/fix-permissions.sh /clawpack
RUN /tempdir/fix-permissions.sh /opt/conda
USER $NB_USER

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
RUN sudo rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean -yaf

## prepare container
WORKDIR $HOME
ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start-notebook.sh"]
