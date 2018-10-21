FROM climateimpactlab/gfortran-netcdf-notebook:v1.0.3

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    basemap=1.1.0 \
    beautifulsoup4=4.6.1 \
    bokeh=0.13.0 \
    bqplot \
    cartopy=0.16.0 \
    click=6.7 \
    cloudpickle=0.5.3 \
    cytoolz=0.9.0.1 \
    dask-core=0.19.4 \
    dask-glm=0.1.0 \
    dask-ml=0.11.0 \
    dask-searchcv=0.2.0 \
    dask=0.18.2 \
    datashader=0.6.8 \
    distributed=1.23.3 \
    esmpy=7.1.0r \
    fastparquet=0.1.6 \
    fiona=1.7.12 \
    fusepy=2.0.4 \
    gcsfs=0.1.2 \
    gdal=2.2.4 \
    geoalchemy2=0.5.0 \
    geopy=1.17.0 \
    geoviews=1.5.1 \
    git=2.18.0 \
    gitpython=2.1.11 \
    holoviews=1.10.7 \
    ipdb=0.11 \
    ipywidgets=7.4.2 \
    jedi=0.12.0 \
    jupyter=1.0.0 \
    jupyterhub=0.9.4 \
    jupyterlab=0.35.2 \
    lz4-c=1.8.1.2 \
    lz4=1.1.0 \
    matplotlib=2.2.2 \
    nb_conda_kernels=2.1.1 \
    nbserverproxy=0.8.3 \
    ncurses=6.1 \
    netcdf-fortran=4.4.4 \
    netcdf4=1.3.1 \
    nomkl=2.0 \
    nose=1.3.7 \
    numba=0.37.0 \
    numcodecs=0.5.5 \
    numpy=1.14.2 \
    pandas=0.23.2 \
    pip=9.0.3 \
    pyshp=1.2.12 \
    python-blosc=1.4.4 \
    python-snappy=0.5.3 \
    pyviz_comms=0.6.0 \
    PyYAML=3.12 \
    rasterio=0.36.0 \
    scikit-image=0.14.0 \
    scikit-learn=0.19.1 \
    scipy=1.1.0 \
    seaborn=0.9.0 \
    setuptools=39.2.0 \
    statsmodels=0.9.0 \
    tornado=5.0.2 \
    tqdm=4.24.0 \
    urllib3=1.23 \
    xarray=0.10.8 \
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
  dask-kubernetes==0.5.0 \
  flake8==3.5.0 \
  google-cloud-storage==1.12.0 \
  impactlab-tools \
  jupyterlab==0.32.1 \
  kubernetes==6.0.0 \
  mapbox==0.16.2 \
  py-noaa==0.2.2 \
  pytest-cov==2.5.1 \
  pytest-runner==4.2 \
  pytest==3.6.2 \
  Sphinx==1.7.5 \
  tox==3.1.1 \
  wget==3.2 \
  wheel==0.31.1 \
  xesmf==0.1.1 \
  xlrd==1.1.0 \
  --no-cache-dir

RUN jupyter labextension install \
  @jupyter-widgets/jupyterlab-manager@0.38 \
  @jupyterlab/hub-extension@0.12.0 \
  jupyterlab_bokeh@0.6.3 \
  @pyviz/jupyterlab_pyviz \
  dask-labextension

RUN jupyter serverextension enable --py nbserverproxy --sys-prefix

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
    apt-get update -y && apt-get install google-cloud-sdk -y

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

RUN pip install \
  rhg_compute_tools==0.1.5 \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  --no-cache-dir

# update pip
RUN pip install --upgrade pip

WORKDIR $HOME

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
