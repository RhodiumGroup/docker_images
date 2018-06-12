FROM continuumio/miniconda3:4.4.10

# Dumb init
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    bokeh=0.12.14 \
    cytoolz \
    datashader \
    dask=0.17.2 \
    gdal=2.2.4 \
    esmpy \
    zarr \
    distributed=1.21.5 \
    fastparquet \
    git \
    ipywidgets \
    jupyterlab \
    holoviews \
    lz4 \
    matplotlib \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba=0.37.0 \
    numcodecs \
    numpy=1.14.2 \
    pandas \
    python-blosc \
    scipy \
    scikit-image \
    tornado \
    xarray=0.10.7 \
    zict \
    rasterio

RUN conda install --yes --channel conda-forge/label/dev geopandas

USER root
RUN apt-get update \
  && apt-get install -yq --no-install-recommends libfuse-dev nano fuse gnupg gnupg2


RUN export GCSFUSE_REPO=gcsfuse-xenial \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update \
  && apt-get install gcsfuse \
  && alias googlefuse=/usr/bin/gcsfuse

# fix https://github.com/ContinuumIO/anaconda-issues/issues/542
RUN conda install --yes -c conda-forge setuptools

RUN pip install --upgrade pip
RUN pip install wget google-cloud==0.32.0 google-cloud-storage gsutil fusepy click jedi kubernetes pyasn1 click urllib3 xesmf --no-cache-dir

RUN pip install daskernetes==0.1.3 \
                git+https://github.com/dask/dask-kubernetes@5ba08f714ef38e585e9f2038b6be530c578b96dd \
                git+https://github.com/ioam/holoviews@3f015c0a531f54518abbfecffaac72a7b3554ed3\
                git+https://github.com/dask/gcsfs@2fbdc27e838a531ada080886ae778cb370ae48b8\
                git+https://github.com/jupyterhub/nbserverproxy \
                --no-cache-dir

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN conda clean -tipsy

ENV OMP_NUM_THREADS=1
ENV DASK_TICK_MAXIMUM_DELAY=5s

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh
RUN mkdir /opt/app
RUN mkdir /gcs

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]