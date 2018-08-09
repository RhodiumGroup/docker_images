FROM continuumio/miniconda3:4.5.4

# Dumb init
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    beautifulsoup4=4.6.1 \
    bokeh=0.12.14 \
    click=6.7 \
    cloudpickle=0.5.3 \
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
    git \
    geoviews \
    holoviews=1.10.2 \
    ipdb=0.11 \
    ipywidgets=7.2.1 \
    jedi=0.12.0 \
    lz4-c=1.8.1.2 \
    lz4=1.1.0 \
    matplotlib=2.2.2 \
    nb_conda_kernels=2.1.1 \
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
    scipy=1.1.0 \
    setuptools=39.2.0 \
    statsmodels=0.9.0 \
    tornado=5.0.2 \
    urllib3=1.23 \
    xarray=0.10.7 \
    zarr=2.2.0 \
    zict=0.1.3

RUN conda install --yes --channel conda-forge/label/dev geopandas=geopandas=1.0.0.dev

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse gnupg gnupg2 zip

RUN export GCSFUSE_REPO=gcsfuse-xenial \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update \
  && apt-get install gcsfuse \
  && alias googlefuse=/usr/bin/gcsfuse

#RUN pip install --upgrade pip
RUN pip install \
    daskernetes==0.1.3 \
    dask-kubernetes==0.2.0 \
    google-cloud-storage==1.10.0 \
    google-cloud==0.32.0 \
    gsutil==4.33 \
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

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]