FROM climateimpactlab/gfortran-netcdf-notebook:v1.0.3

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
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
    gdal=2.4.1 \
    geopy=1.17.0 \
    geoviews=1.6.2 \
    git=2.22.0 \
    gitpython=2.1.11 \
    holoviews=1.12.3 \
    ipdb=0.11 \
    ipympl=0.2.1 \
    ipywidgets=7.4.2 \
    jedi=0.13.3 \
    jupyter=1.0.0 \
    jupyterhub=1.0.0 \
    jupyterlab=0.35.6 \
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
    python=3.6 \
    python-blosc=1.8.1 \
    python-snappy=0.5.4 \
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
    tqdm=4.32.1 \
    urllib3=1.25.3 \
    xarray=0.12.1 \
    zarr=2.3.2 \
    zict=0.1.4

RUN conda install --yes --channel conda-forge/label/dev geopandas

RUN pip install \
bumpversion==0.5.3 \
coverage==4.5.1 \
dask-kubernetes==0.8.0 \
flake8==3.5.0 \
google-cloud-storage==1.16.1 \
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

# install R kernel
RUN conda create -n r -c conda-forge \
    'rpy2=2.8*' \
    'r-base=3.4.1' \
    'r-irkernel=0.8*' \
    'r-plyr=1.8*' \
    'r-devtools=1.13*' \
    'r-tidyverse=1.2*' \
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
    'r-hexbin=1.27*'

RUN jupyter kernelspec install --name R \
    /opt/conda/envs/r/share/jupyter/kernels/ir
# set the r kernel python to the r environment python
RUN sed -i 's/python/\/opt\/conda\/envs\/r\/bin\/python/' \
    /usr/local/share/jupyter/kernels/ir/kernel.json

# install Octave kernel
RUN apt-get update && apt-get install -y octave
RUN conda create -n octave texinfo python=3.6 pip
RUN /opt/conda/envs/octave/bin/pip install octave_kernel
RUN jupyter kernelspec install --name octave \
    /opt/conda/envs/octave/share/jupyter/kernels/octave
# set the octave kernel python to the r environment python
RUN sed -i 's/python/\/opt\/conda\/envs\/octave\/bin\/python/' \
    /usr/local/share/jupyter/kernels/octave/kernel.json

RUN fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

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
  rhg_compute_tools==0.1.6 \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  parameterize_jobs==0.1.0 \
  --no-cache-dir

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]
