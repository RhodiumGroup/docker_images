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
    beautifulsoup4 \
    bokeh=0.12.15 \
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
    ipdb \
    holoviews \
    lz4=1.1.0 \
    matplotlib \
    nbserverproxy \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba=0.37.0 \
    numcodecs \
    numpy=1.14.2 \
    pandas \
    python-blosc=1.4.4 \
    seaborn \
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

RUN pip install \
  bumpversion==0.5.3 \
  click \
  coverage==4.5.1 \
  dask-kubernetes==0.4.0 \
  flake8==3.5.0 \
  fusepy \
  google-cloud==0.32.0 \
  google-cloud-storage \
  gsutil \
  impactlab-tools \
  jedi \
  jupyterlab==0.32.1 \
  kubernetes==6.0.0 \
  mapbox \
  pytest==3.6.3 \
  pytest-cov==2.5.1 \
  pytest-runner==4.2 \
  PyYAML==3.13 \
  py_noaa \
  Sphinx==1.7.5 \
  statsmodels==0.9.0 \
  tox==3.1.1 \
  wget \
  wheel==0.31.1 \
  xesmf \
  xlrd \
  --no-cache-dir


RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.35 \
                                  @jupyterlab/hub-extension@0.9.2 \
                                  jupyterlab_bokeh@0.5.0 \
                                  @pyviz/jupyterlab_pyviz@0.5.2

RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home


#setup Dask Kubernetes
ENV DASK_CONFIG=/home/$NB_USER/config.yml
COPY config.yml /pre-home
COPY worker-template.yml /pre-home

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
