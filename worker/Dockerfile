FROM climateimpactlab/miniconda3-gfortran-netcdf:v1.0.2

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda install --yes conda=4.7.5
RUN conda create -n worker --yes -c conda-forge \
    beautifulsoup4=4.6.1 \
    bokeh=1.2.0 \
    bqplot \
    cartopy=0.16.0 \
    click=6.7 \
    cloudpickle=1.2.1 \
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
    git=2.22.0 \
    gitpython=2.1.11 \
    intake=0.5.1 \
    ipdb=0.11 \
    ipython=7.6.0 \
    ipywidgets=7.4.2 \
    jedi=0.14.0 \
    jupyter=1.0.0 \
    lz4-c=1.8.1.2 \
    lz4=2.1.9 \
    matplotlib=3.0.3 \
    nb_conda_kernels=2.2.2 \
    nbserverproxy=0.8.3 \
    ncurses=6.1 \
    netcdf-fortran=4.4.5 \
    netcdf4=1.5.1.2 \
    nose=1.3.7 \
    numba=0.44.1 \
    numcodecs=0.6.3 \
    numpy=1.15.4 \
    pandas=0.24.2 \
    pip=19.1.1 \
    pyshp=1.2.12 \
    python-blosc=1.4.4 \
    python-snappy=0.5.3 \
    python=3.6 \
    PyYAML=3.12 \
    rasterio=1.0.24 \
    scikit-image=0.14.1 \
    scikit-learn=0.20.0 \
    scipy=1.1.0 \
    seaborn=0.9.0 \
    setuptools=39.2.0 \
    statsmodels=0.9.0 \
    tornado=5.1.1 \
    tqdm=4.24.0 \
    urllib3=1.24.3 \
    xarray=0.11.3 \
    xesmf=0.1.1 \
    zarr=2.3.2 \
    zict=0.1.4 \
    conda-forge/label/dev::geopandas \
    colorcet=2.0.1 \
    geoviews=1.6.2 \
    holoviews=1.12.3 \
    hvplot=0.4.0 \
    param=1.9.1 \
    panel=0.6.0 \
    pyviz_comms=0.7.2

# don't upgrade tornado - see https://github.com/jupyterlab/jupyterlab/issues/6062

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
    git+git://github.com/dask/dask-kubernetes.git@295f06428119bc8e674a2e6a59cd97000fae69e8 \
    google-cloud-storage==1.12.0 \
    pyasn1-modules==0.2.2 \
    pyasn1==0.4.3 \
    wget==3.2 \
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
RUN chmod +x /usr/bin/prepare.sh
COPY add_service_creds.py /usr/bin/add_service_creds.py
RUN chmod +x /usr/bin/add_service_creds.py
RUN mkdir /opt/app
RUN mkdir /gcs

# pip install the RHG packages that we update frequently
# (keeping down here so that rest of image will stay
# cached when updating these versions)
RUN pip install \
    git+git://github.com/RhodiumGroup/rhg_compute_tools.git@f49c253653b2a11786c7ad67b95e00513eecc0e4 \
    impactlab-tools==0.3.1 \
    climate-toolbox==0.1.4 \
    parameterize_jobs==0.1.0 \
    --no-cache-dir

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
