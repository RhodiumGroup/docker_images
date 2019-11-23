FROM jupyter/base-notebook:latest
ARG DEBIAN_FRONTEND=noninteractive

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

COPY prepare.sh /usr/bin
COPY overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json


## perform a bunch of common actions
RUN sudo bash /tempdir/common.sh
RUN sudo chown -R $NB_USER /gcs


## more apt-get
RUN sudo apt-get install -yq \
  vim \
  octave && \
  sudo apt-get clean


# set up conda channels
RUN mkdir /opt/conda/specs
COPY base_environment.yml /opt/conda/specs
COPY notebook_environment.yml /opt/conda/specs
COPY r_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge/label/dev && \
  conda config --add channels conda-forge


## set up conda
RUN conda update -n base conda

#  update environemnt with common packages across worker and nb
RUN conda env update -f /opt/conda/specs/base_environment.yml

# update environment with nb-specific packages
RUN conda env update -f /opt/conda/specs/notebook_environment.yml

# create r environment
RUN conda env create -f /opt/conda/specs/r_environment.yml


## Set up jupyter lab extensions
RUN jupyter labextension update --all && \
    jupyter labextension install \
    @bokeh/jupyter_bokeh \
    @jupyter-widgets/jupyterlab-manager \
    @jupyter-widgets/jupyterlab-sidecar \
    @pyviz/jupyterlab_pyviz \
    dask-labextension \
    jupyter-leaflet \
    jupyterlab-plotly \
    plotlywidget


## clean up
RUN sudo rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean --all -f


## prepare container
WORKDIR $HOME
ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
