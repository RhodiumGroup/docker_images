FROM climateimpactlab/miniconda3-gfortran-netcdf:latest

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda create -n worker --yes -c conda-forge \
    basemap=1.1.0 \
    beautifulsoup4=4.6.1 \
    bokeh=0.12.15 \
    bqplot \
    cartopy=0.16.0 \
    click=6.7 \
    cloudpickle=0.5.3 \
    cytoolz=0.9.0.1 \
    dask-core=0.18.2 \
    dask-glm=0.1.0 \
    dask-ml=0.7.0 \
    dask-searchcv=0.2.0 \
    dask=0.18.2 \
    datashader=0.6.6 \
    distributed=1.22.1 \
    esmpy=7.1.0r \
    fastparquet=0.1.6 \
    fiona=1.7.12 \
    fusepy=2.0.4 \
    gcsfs=0.1.2 \
    gdal=2.2.4 \
    geoalchemy2=0.5.0 \
    geoviews=1.5.1 \
    git=2.18.0 \
    gitpython=2.1.11 \
    holoviews=1.10.7 \
    ipdb=0.11 \
    ipywidgets=7.2.1 \
    jedi=0.12.0 \
    jupyter=1.0.0 \
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
    python=3.6 \
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
    dask-kubernetes==0.4.0 \
    google-cloud-storage==1.12.0 \
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

RUN /opt/conda/envs/worker/bin/pip install \
  rhg_compute_tools==0.1.0 \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  --no-cache-dir

# update pip
RUN /opt/conda/envs/worker/bin/pip install --upgrade pip

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
