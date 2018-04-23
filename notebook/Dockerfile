#We build our single-user notebook from the base jupyter notebook image
FROM jupyter/base-notebook

#install some system level packages 
USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse vim git keychain \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER $NB_USER

ARG JUPYTERHUB_VERSION=0.8.*

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir \
         jupyterhub==${JUPYTERHUB_VERSION} \
         -r /tmp/requirements.txt

#Do additional conda installs 
RUN conda install --yes -c conda-forge \
    bokeh=0.12.14 \
    cytoolz \
    cartopy \
    datashader \
    dask=0.17.2 \
    zarr \
    dask-ml \
    distributed=1.21.5 \
    fastparquet \
    ipywidgets \
    holoviews \
    lz4 \
    matplotlib \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba \
    numcodecs \
    numpy \
    pandas \
    python-blosc \
    scipy \
    scikit-image \
    scikit-learn \
    tornado \
    xarray \
    zict \
    && conda clean -tipsy


RUN pip install wget jupyterlab==0.31rc2 google-cloud google-cloud-storage fusepy click jedi kubernetes --no-cache-dir

RUN pip install daskernetes==0.1.3 \
                git+https://github.com/dask/dask-kubernetes@5ba08f714ef38e585e9f2038b6be530c578b96dd \
                git+https://github.com/ioam/holoviews@3f015c0a531f54518abbfecffaac72a7b3554ed3\
                git+https://github.com/dask/gcsfs@2fbdc27e838a531ada080886ae778cb370ae48b8\
                git+https://github.com/jupyterhub/nbserverproxy \
                --no-cache-dir

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.33.0\
                                 @jupyterlab/hub-extension \
                                 @pyviz/jupyterlab_holoviews

RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY worker-template.yaml /pre-home
COPY add_service_creds.py /pre-home

ENV DASK_TICK_MAXIMUM_DELAY=5s
ENV DASKERNETES_DIAGNOSTICS_LINK {JUPYTERHUB_SERVICE_PREFIX}proxy/{port}/status
ENV DASKERNETES_WORKER_TEMPLATE_PATH /home/$NB_USER/worker-template.yaml
ENV DASKERNETES_WORKER_NAME dask-{JUPYTERHUB_USER}-{uuid}
ENV DASK_DIAGNOSTICS_LINK {JUPYTERHUB_SERVICE_PREFIX}proxy/{port}/status
ENV DASK_KUBERNETES_WORKER_TEMPLATE_PATH /home/$NB_USER/worker-template.yaml
ENV DASK_KUBERNETES_WORKER_NAME dask-{JUPYTERHUB_USER}-{uuid}

RUN export GCSFUSE_REPO=gcsfuse-xenial \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update \
  && apt-get install gcsfuse \
  && alias googlefuse=/usr/bin/gcsfuse

RUN mkdir /gcs && chown -R $NB_USER /gcs
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]