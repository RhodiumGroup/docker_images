FROM jupyter/base-notebook:python-3.7.3

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes -n base conda

# install cythonized version of geopandas
RUN conda install --yes --channel conda-forge/label/dev geopandas

#  update environemnt with common packages across worker and nb
COPY base_environment.yml /home/jovyan/base_environment.yml
RUN conda env update -f /home/jovyan/base_environment.yml

# update environment with nb-specific packages
COPY environment.yml /home/jovyan/environment.yml
RUN conda env update -f /home/jovyan/environment.yml

# create r environment
COPY environment_r.yml /home/jovyan/environment_r.yml
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

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home
COPY run_sql_proxy.py /pre-home

COPY config.yaml /pre-home
COPY worker-template.yml /pre-home

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk kubectl -y

RUN export GCSFUSE_REPO=gcsfuse-xenial \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update \
  && apt-get install gcsfuse -y \
  && alias googlefuse=/usr/bin/gcsfuse

USER root
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/bin/cloud_sql_proxy
RUN chmod +x /usr/bin/cloud_sql_proxy

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN conda clean -tipsy

RUN mkdir /gcs && chown -R $NB_USER /gcs
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

WORKDIR $HOME

COPY overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
