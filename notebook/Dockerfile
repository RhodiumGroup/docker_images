FROM climateimpactlab/gfortran-netcdf-notebook:v1.0.3

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    beautifulsoup4=4.6.1 \
    bokeh=0.13.0 \
    bqplot \
    cartopy=0.16.0 \
    cftime=1.0.3.4 \
    click=6.7 \
    cloudpickle=0.5.3 \
    cytoolz=0.9.0.1 \
    dask-core=1.2.0 \
    dask-glm=0.1.0 \
    dask-ml=0.12.0 \
    dask-searchcv=0.2.0 \
    dask=1.2.0 \
    datashader=0.6.8 \
    distributed=1.28.1 \
    esmpy=7.1.0r \
    fastparquet=0.3.1 \
    fiona=1.7.13 \
    fusepy=2.0.4 \
    gcsfs=0.1.2 \
    gdal=2.2.4 \
    geopy=1.17.0 \
    geoviews=1.5.1 \
    git=2.18.0 \
    gitpython=2.1.11 \
    holoviews=1.10.7 \
    ipdb=0.11 \
    ipympl=0.2.1 \
    ipywidgets=7.4.2 \
    jedi=0.12.0 \
    jupyter=1.0.0 \
    jupyterhub=1.0.0 \
    jupyterlab=0.35.6 \
    lz4-c=1.8.1.2 \
    lz4=1.1.0 \
    matplotlib=3.0.2 \
    nb_conda_kernels=2.2.2 \
    nbserverproxy=0.8.8 \
    ncurses=6.1 \
    netcdf-fortran=4.4.4 \
    netcdf4=1.3.1 \
    nose=1.3.7 \
    numba=0.40.0 \
    numcodecs=0.5.5 \
    numpy=1.15.4 \
    pandas=0.23.4 \
    pip=18.1 \
    pyshp=1.2.12 \
    python=3.6 \
    python-blosc=1.4.4 \
    python-snappy=0.5.3 \
    pyviz_comms=0.6.0 \
    PyYAML=5.1.1 \
    rasterio=0.36.0 \
    scikit-image=0.14.1 \
    scikit-learn=0.20.0 \
    scipy=1.3.0 \
    seaborn=0.9.0 \
    setuptools=39.2.0 \
    statsmodels=0.9.0 \
    tornado=5.1.1 \
    tqdm=4.24.0 \
    urllib3=1.23 \
    xarray=0.10.9 \
    zarr=2.2.0 \
    zict=0.1.3

RUN conda install --yes --channel conda-forge/label/dev geopandas

RUN pip install \
    bumpversion==0.5.3 \
    coverage==4.5.1 \
    dask-kubernetes==0.8.0 \
    flake8==3.5.0 \
    google-cloud-storage==1.12.0 \
    kubernetes==9.0.0 \
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
    @jupyter-widgets/jupyterlab-manager@0.38.1 \
    @jupyterlab/hub-extension@0.12.0 \
    jupyterlab_bokeh@0.6.3 \
    @pyviz/jupyterlab_pyviz@0.7.1 \
    dask-labextension@0.3.0 \
    jupyter-matplotlib@0.3.0

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

WORKDIR $HOME

# pip install the RHG packages that we update frequently
# (keeping down here so that rest of image will stay
# cached when updating these versions)
RUN pip install \
  git+git://github.com/RhodiumGroup/rhg_compute_tools.git@999d4d24f2136ea809cae2d62fa11a5a0c3d7a9c \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  parameterize_jobs==0.1.0 \
  --no-cache-dir

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
