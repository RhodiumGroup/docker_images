FROM climateimpactlab/gfortran-netcdf-notebook:v1.0.3

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda install --yes conda=4.7.5
RUN conda install --yes -c conda-forge \
    beautifulsoup4=4.6.1 \
    bokeh=1.2.0 \
    bqplot \
    cartopy=0.16.0 \
    click=6.7 \
    cloudpickle=1.2.1 \
    colorcet=2.0.1 \
    cytoolz=0.9.0.1 \
    dask-glm=0.1.0 \
    dask-ml=0.11.0 \
    dask-searchcv=0.2.0 \
    dask=2.0.0 \
    datashader=0.7.0 \
    distributed=2.0.1 \
    esmpy=7.1.0 \
    fastparquet=0.3.1 \
    fiona=1.8.6 \
    fusepy=3.0.1 \
    gcsfs=0.2.2 \
    gdal=2.4.1 \
    geoalchemy2=0.5.0 \
    geopy=1.17.0 \
    geoviews=1.6.2 \
    git=2.22.0 \
    gitpython=2.1.11 \
    holoviews=1.12.3 \
    hvplot=0.4.0 \
    intake=0.5.1 \
    ipdb=0.11 \
    ipympl=0.2.1 \
    ipython=7.6.0 \
    ipywidgets=7.4.2 \
    jedi=0.14.0 \
    jupyter=1.0.0 \
    jupyterhub=1.0.0 \
    jupyterlab=0.35.6 \
    lz4-c=1.8.1.2 \
    lz4=2.1.9 \
    matplotlib=3.0.3 \
    nb_conda_kernels=2.2.2 \
    nbserverproxy=0.8.3 \
    ncurses=6.1 \
    netcdf-fortran=4.4.5 \
    netcdf4=1.5.1.2 \
    nodejs=11.14.0 \
    nose=1.3.7 \
    numba=0.44.1 \
    numcodecs=0.6.3 \
    numpy=1.15.4 \
    pandas=0.23.4 \
    panel=0.6.0 \
    param=1.9.1 \
    pip=19.1.1 \
    pyshp=1.2.12 \
    python=3.6 \
    python-blosc=1.4.4 \
    python-snappy=0.5.3 \
    pyviz_comms=0.7.2 \
    PyYAML=3.12 \
    rasterio=1.0.24 \
    requests=2.22.0 \
    scikit-image=0.14.1 \
    scikit-learn=0.20.0 \
    scipy=1.1.0 \
    seaborn=0.9.0 \
    setuptools=39.2.0 \
    statsmodels=0.9.0 \
    tornado=5.1.1 \
    tqdm=4.24.0 \
    urllib3=1.24.3 \
    widgetsnbextension=3.4.2 \
    xarray=0.11.3 \
    xesmf=0.1.1 \
    zarr=2.3.2 \
    zict=0.1.4 \
    conda-forge/label/dev::geopandas

# don't upgrade tornado - see https://github.com/jupyterlab/jupyterlab/issues/6062

RUN pip install \
    bumpversion==0.5.3 \
    coverage==4.5.1 \
    git+git://github.com/dask/dask-kubernetes.git@295f06428119bc8e674a2e6a59cd97000fae69e8 \
    flake8==3.5.0 \
    google-cloud-storage==1.12.0 \
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
    xlrd==1.1.0 \
    --no-cache-dir

RUN jupyter labextension install \
    @jupyter-widgets/jupyterlab-manager@0.38.1 \
    @jupyterlab/hub-extension@0.12.0 \
    jupyterlab_bokeh@0.6.3 \
    @pyviz/jupyterlab_pyviz@0.7.2 \
    dask-labextension@0.2.0 \
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
  && apt-get install gcsfuse kubectl \
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
  rhg_compute_tools==0.1.8 \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  parameterize_jobs==0.1.0 \
  --no-cache-dir

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
