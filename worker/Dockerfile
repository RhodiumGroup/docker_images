FROM climateimpactlab/miniconda3-gfortran-netcdf:apt-get-netcdf

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda create -n worker --yes -c conda-forge \
  beautifulsoup4=4.7.1 \
  bokeh=1.2.0 \
  bumpversion=0.5.3 \
  bqplot=0.11.5 \
  cartopy0.17.0 \
  click=7.0 \
  cloudpickle=1.2.1 \
  cytoolz=0.9.0.1 \
  dask-glm=0.1.0 \
  dask-kubernetes=0.8.0 \
  dask-ml=0.13.0 \
  dask=1.2.0 \
  datashader=0.7.0 \
  distributed=1.28.1 \
  esmpy=7.1.0 \
  fastparquet=0.3.1 \
  flake8=3.7.7 \
  fiona=1.8.6 \
  fusepy=3.0.1 \
  gcsfs=0.2.2 \
  gdal=2.4.1 \
  geoalchemy2=0.6.3 \
  geopandas=0.5.0 \
  geopy=1.20.0 \
  geoviews=1.6.2 \
  git=2.22.0 \
  gitpython=2.1.11 \
  google-cloud-storage=1.16.1 \
  holoviews=1.12.3 \
  ipdb=0.12 \
  ipympl=0.2.1 \
  ipywidgets=7.4.2 \
  jedi=0.13.3 \
  jupyter=1.0.0 \
  jupyterhub=1.0.0 \
  jupyterlab=0.35.6 \
  lz4=2.1.9 \
  lz4-c=1.8.3 \
  matplotlib=3.1.0 \
  nb_conda_kernels=2.2.2 \
  nbserverproxy=0.8.8 \
  ncurses=6.1 \
  netcdf-fortran=4.4.5 \
  netcdf4=1.5.1.2 \
  nomkl=3.0 \
  nose=1.3.7 \
  numba=0.43.1 \
  numcodecs=0.6.3 \
  numpy=1.16.4 \
  pandas=0.24.2 \
  pip=19.1.1 \
  pyshp=2.1.0 \
  pytest=4.6.3 \
  pytest-cov=2.7.1 \
  pytest-runner=5.1 \
  python-blosc=1.8.1 \
  python-snappy=0.5.4 \
  pyviz_comms=0.7.2 \
  PyYAML=5.1.1 \
  rasterio=1.0.24 \
  scikit-image=0.15.0 \
  scikit-learn=0.21.2 \
  scipy=1.3.0 \
  seaborn=0.9.0 \
  setuptools=41.0.1 \
  sphinx=2.1.1 \
  statsmodels=0.9.0 \
  tornado=6.0.2 \
  tox=3.12.0 \
  tqdm=4.32.1 \
  urllib3=1.24.3 \
  wget=1.20.1 \
  wheel=0.33.4 \
  widgetsnbextension=3.4.2 \
  xarray=0.12.1 \
  xesmf=0.1.1 \
  xlrd=1.2.0 \
  zarr=2.3.2 \
  zict=0.1.4

# trying out new master branch version (0.5) instead of dev
# RUN conda install -n worker --yes --channel conda-forge/label/dev geopandas

RUN pip install \
    mapbox \
    py-noaa \
    --no-cache-dir

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
  climate-toolbox=0.1.4 \
  impactlab-tools=0.3.1 \
  parameterize_jobs=0.1.0 \
  rhg_compute_tools=0.1.6 \
  --no-cache-dir

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
