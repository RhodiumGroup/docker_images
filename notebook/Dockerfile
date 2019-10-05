FROM jupyter/base-notebook:python-3.7.3

## Add NB_USER to sudo
USER root
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER


## filepath curation
COPY common.sh /home/jovyan/common.sh
COPY prepare.sh /usr/bin/prepare.sh
COPY base_environment.yml /home/jovyan/base_environment.yml
COPY environment.yml /home/jovyan/environment.yml
COPY environment_r.yml /home/jovyan/environment_r.yml
COPY overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json

RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home
COPY run_sql_proxy.py /pre-home
COPY config.yaml /pre-home
COPY worker-template.yml /pre-home


## perform a bunch of common actions
RUN /home/jovyan/common.sh
RUN chown -R $NB_USER /gcs


## set up python env

#  update environemnt with common packages across worker and nb
RUN conda env update -f /home/jovyan/base_environment.yml

# update with cythonized geopandas
RUN conda install -n worker --channel conda-forge/label/dev geopandas

# update environment with nb-specific packages
RUN conda env update -f /home/jovyan/environment.yml

# create r environment
RUN conda env create -f /home/jovyan/environment_r.yml

RUN jupyter labextension update --all && \
    jupyter labextension install \
    @jupyterlab/hub-extension \
    @jupyterlab/plotly-extension \
    @jupyter-widgets/jupyterlab-manager \
    @jupyter-widgets/jupyterlab-sidecar \
    @pyviz/jupyterlab_pyviz \
    dask-labextension \
    itk-jupyter-widgets \
    jupyterlab_bokeh \
    jupyter-leaflet

RUN jupyter serverextension enable --py jupyterlab --sys-prefix
RUN jupyter serverextension enable --py jupyterlab --user
RUN jupyter serverextension enable --sys-prefix jupyter_server_proxy
RUN jupyter serverextension enable --py --sys-prefix dask_labextension


## clean up
RUN rm -rf /var/lib/apt/lists/*
RUN conda clean --all -y -f


## prepare container
WORKDIR $HOME
ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
