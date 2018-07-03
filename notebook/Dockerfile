#We build our single-user notebook from the base jupyter notebook image
FROM jupyter/base-notebook

#install some system level packages 
USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends \
  libfuse-dev \
  fonts-dejavu \
  tzdata \
  gfortran \
  nano \
  fuse \
  vim \
  git \
  keychain \
  gnupg \
  gnupg2 \
  rsync \
  libcurl4-openssl-dev \
  libssl-dev \
  build-essential

USER $NB_USER

#Do additional conda installs 
RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    bokeh=0.12.14 \
    basemap \
    cytoolz \
    cartopy \
    datashader \
    dask=0.17.2 \
    gdal=2.2.4 \
    esmpy \
    zarr \
    dask-ml \
    distributed=1.21.5 \
    fastparquet \
    ipywidgets \
    holoviews \
    lz4 \
    matplotlib \
    nbserverproxy \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba=0.37.0 \
    numcodecs \
    numpy=1.14.2 \
    pandas \
    python-blosc \
    scipy \
    scikit-image \
    scikit-learn \
    tornado \
    xarray=0.10.7 \
    zict \
    rasterio

RUN conda install --yes --channel conda-forge/label/dev geopandas

#install R packages
RUN conda install --quiet --yes \
    'rpy2=2.8*' \
    'r-base=3.4.1' \
    'r-irkernel=0.8*' \
    'r-plyr=1.8*' \
    'r-devtools=1.13*' \
    'r-tidyverse=1.1*' \
    'r-shiny=1.0*' \
    'r-rmarkdown=1.8*' \
    'r-forecast=8.2*' \
    'r-rsqlite=2.0*' \
    'r-reshape2=1.4*' \
    'r-nycflights13=0.2*' \
    'r-caret=6.0*' \
    'r-rcurl=1.95*' \
    'r-crayon=1.3*' \
    'r-randomforest=4.6*' \
    'r-htmltools=0.3*' \
    'r-sparklyr=0.7*' \
    'r-htmlwidgets=1.0*' \
    'r-hexbin=1.27*' && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

RUN pip install wget jupyterlab==0.31rc2 py_noaa dbfread xlrd mapbox google-cloud==0.32.0 google-cloud-storage xesmf gsutil fusepy click jedi kubernetes impactlab-tools --no-cache-dir

RUN pip install daskernetes==0.1.3 \
                git+https://github.com/dask/dask-kubernetes@5ba08f714ef38e585e9f2038b6be530c578b96dd \
                git+https://github.com/ioam/holoviews@3f015c0a531f54518abbfecffaac72a7b3554ed3\
                git+https://github.com/dask/gcsfs@2fbdc27e838a531ada080886ae778cb370ae48b8\
                --no-cache-dir

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.33.0 \
                                  @jupyterlab/hub-extension@0.8.1 \
                                  jupyterlab_bokeh@0.4.1

RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home


#setup Dask Kubernetes
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

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN conda clean -tipsy

RUN mkdir /gcs && chown -R $NB_USER /gcs
RUN mkdir /opt/app

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
