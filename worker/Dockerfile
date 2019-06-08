FROM climateimpactlab/miniconda3-gfortran-netcdf:v1.0.2

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda create -n worker --yes -c conda-forge \
    beautifulsoup4=4.7.1 \
    bokeh=1.2.0 \
    bqplot=0.11.5 \
    cartopy=0.16.0 \
    cftime=1.0.3.4 \
    click=6.7 \
    cloudpickle=0.8.0 \
    cytoolz=0.9.0.1 \
    dask-core=1.2.0 \
    dask-glm=0.1.0 \
    dask-ml=0.12.0 \
    dask-searchcv=0.2.0 \
    dask=1.2.0 \
    datashader=0.7.0 \
    distributed=1.28.1 \
    esmpy=7.1.0r \
    fastparquet=0.3.1 \
    fiona=1.8.6 \
    fusepy=3.0.1 \
    gcsfs=0.2.2 \
    gdal=2.2.4 \
    geopy=1.17.0 \
    geoviews=1.6.2 \
    git=2.18.0 \
    gitpython=2.1.11 \
    holoviews=1.12.3 \
    ipdb=0.11 \
    ipympl=0.2.1 \
    ipywidgets=7.4.2 \
    jedi=0.13.3 \
    jupyter=1.0.0 \
    lz4-c=1.8.3 \
    lz4=2.1.6 \
    matplotlib=3.1.0 \
    nb_conda_kernels=2.2.2 \
    nbserverproxy=0.8.8 \
    ncurses=6.1 \
    netcdf-fortran=4.4.5 \
    netcdf4=1.5.1.2 \
    nose=1.3.7 \
    numba=0.43.1 \
    numcodecs=0.6.3 \
    numpy=1.16.4 \
    pandas=0.24.2 \
    pip=18.1 \
    pyshp=2.1.0 \
    python-blosc=1.8.1 \
    python-snappy=0.5.4 \
    python=3.6 \
    pyviz_comms=0.7.2 \
    PyYAML=5.1.1 \
    rasterio=1.0.24 \
    scikit-image=0.15.0 \
    scikit-learn=0.21.2 \
    scipy=1.3.0 \
    seaborn=0.9.0 \
    setuptools=39.2.0 \
    statsmodels=0.9.0 \
    tornado=6.0.2 \
    urllib3=1.25.3 \
    xarray=0.12.1 \
    zarr=2.3.2 \
    zict=0.1.4

RUN conda install -n worker --yes --channel conda-forge/label/dev geopandas

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

RUN /opt/conda/envs/worker/bin/pip install \
    dask-kubernetes==0.8.0 \
    google-cloud-storage==1.16.1 \
    kubernetes==9.0.0 \
    pyasn1-modules==0.2.2 \
    pyasn1==0.4.3 \
    wget==3.2 \
    xesmf==0.1.1 \
    --no-cache-dir

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN conda clean -tipsy

ENV OMP_NUM_THREADS=1
ENV DASK_TICK_MAXIMUM_DELAY=5s

USER root
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/bin/cloud_sql_proxy
RUN chmod +x /usr/bin/cloud_sql_proxy

USER root
COPY prepare.sh /usr/bin/prepare.sh
COPY add_service_creds.py /usr/bin/add_service_creds.py
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /opt/app
RUN mkdir /gcs

# pip install the RHG packages that we update frequently
# (keeping down here so that rest of image will stay
# cached when updating these versions)
RUN pip install \
  rhg_compute_tools==0.1.6 \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  parameterize_jobs==0.1.0 \
  --no-cache-dir

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
