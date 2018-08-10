# Note that this image is attempting to update from the build here: https://travis-ci.org/RhodiumGroup/docker_images/builds/400944547#L2345

##We build our single-user notebook from the base jupyter notebook image
FROM jupyter/base-notebook

#install some system level packages
USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends \
  libfuse-dev \
  fonts-dejavu \
  tzdata \
  gfortran \
  graphviz \
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
  build-essential \
  zip

USER $NB_USER

#Do additional conda installs
RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    basemap=1.1.0 \
    beautifulsoup4=4.6.1 \
    bokeh=0.12.14 \
    bqplot \
    cartopy=0.16.0 \
    click=6.7 \
    cytoolz=0.9.0.1 \
    dask-core=0.17.2 \
    dask-glm=0.1.0 \
    dask-ml=0.6.0 \
    dask-searchcv=0.2.0 \
    dask=0.17.2 \
    datashader=0.6.6 \
    distributed=1.21.5 \
    esmpy=7.1.0r \
    fastparquet=0.1.5 \
    fusepy=2.0.4 \
    gdal=2.2.4 \
    geoviews \
    holoviews=1.10.2 \
    ipdb=0.11 \
    ipywidgets=7.2.1 \
    jedi=0.12.0 \
    jupyter=1.0.0 \
    lz4-c=1.8.1.2 \
    lz4=1.1.0 \
    matplotlib=2.2.2 \
    nb_conda_kernels=2.1.1 \
    nbserverproxy=0.8.3 \
    netcdf-fortran=4.4.4 \
    netcdf4=1.4.0 \
    nomkl=2.0 \
    numba=0.37.0 \
    numcodecs=0.5.5 \
    numpy=1.14.2 \
    pandas=0.23.2 \
    python-blosc=1.4.4 \
    rasterio=0.36.0 \
    scikit-image=0.14.0 \
    scikit-learn=0.19.1 \
    scipy=1.1.0 \
    seaborn=0.9.0 \
    statsmodels==0.9.0 \
    tornado=5.0.2 \
    xarray=0.10.7 \
    zarr=2.2.0 \
    zict=0.1.3


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

RUN pip install \
  bumpversion==0.5.3 \
  coverage==4.5.1 \
  daskernetes==0.1.3 \
  dask-kubernetes==0.2.0 \
  flake8==3.5.0 \
  google-cloud-storage==1.10.0 \
  google-cloud==0.32.0 \
  gsutil==4.33 \
  impactlab-tools \
  jupyterlab==0.31rc2 \
  kubernetes==6.0.0 \
  mapbox==0.16.2 \
  py-noaa==0.2.2 \
  pytest-cov==2.5.1 \
  pytest-runner==4.2 \
  pytest==3.6.2 \
  PyYAML==3.12 \
  Sphinx==1.7.5 \
  tox==3.1.1 \
  wget==3.2 \
  wheel==0.31.1 \
  xesmf==0.1.1 \
  xlrd==1.1.0 \
  --no-cache-dir

RUN jupyter labextension install \
  @jupyter-widgets/jupyterlab-manager@0.33.0 \
  @jupyterlab/hub-extension@0.8.1 \
  jupyterlab_bokeh@0.4.1

RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home
COPY run_sql_proxy.py /pre-home

COPY config.yml /pre-home
COPY worker-template.yml /pre-home


RUN export GCSFUSE_REPO=gcsfuse-xenial \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update \
  && apt-get install gcsfuse \
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

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
