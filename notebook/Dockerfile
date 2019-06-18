FROM climateimpactlab/gfortran-netcdf-notebook:apt-get-netcdf

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    beautifulsoup4 \
    bokeh \
    bumpversion \
    bqplot \
    cartopy \
    click \
    cloudpickle \
    cytoolz \
    dask-glm \
    dask-kubernetes \
    dask-ml \
    dask \
    datashader \
    distributed \
    esmpy \
    fastparquet \
    flake8 \
    fiona \
    fusepy \
    gcsfs \
    gdal \
    geoalchemy2 \
    geopandas \
    geopy \
    geoviews \
    git \
    gitpython \
    google-cloud-storage \
    holoviews \
    ipdb \
    ipympl \
    ipywidgets \
    jedi \
    jupyterhub \
    jupyterlab \
    lz4-c \
    lz4 \
    matplotlib \
    nb_conda_kernels \
    nbserverproxy \
    ncurses \
    netcdf-fortran \
    netcdf4 \
    nomkl \
    nose \
    numba \
    numcodecs \
    pandas \
    pip \
    pyshp \
    pytest \
    pytest-cov \
    pytest-runner \
    python-blosc\
    python-snappy \
    pyviz_comms \
    PyYAML \
    rasterio \
    scikit-image \
    scikit-learn \
    scipy \
    seaborn \
    setuptools \
    sphinx \
    statsmodels \
    tornado \
    tox \
    tqdm \
    urllib3 \
    wget \
    wheel \
    widgetsnbextension \
    xarray \
    xesmf \
    xlrd \
    zarr \
    zict

# RUN conda install --yes --channel conda-forge/label/dev geopandas

RUN pip install \
    mapbox \
    py-noaa \
    --no-cache-dir

RUN jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager \
    @jupyterlab/hub-extension \
    jupyterlab_bokeh \
    @pyviz/jupyterlab_pyviz \
    dask-labextension \
    jupyter-matplotlib

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
  rhg_compute_tools \
  impactlab-tools \
  climate-toolbox \
  parameterize_jobs \
  --no-cache-dir

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
