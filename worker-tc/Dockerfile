FROM continuumio/miniconda3:4.4.10

# Dumb init
RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN conda update --yes conda
RUN conda install --yes -c conda-forge \
    beautifulsoup4 \
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
    lz4=1.1.0 \
    matplotlib \
    nbserverproxy \
    nb_conda_kernels \
    netcdf4 \
    nomkl \
    numba=0.37.0 \
    numcodecs \
    numpy=1.14.2 \
    pandas \
    python-blosc=1.4.4 \
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

#RUN pip install --upgrade pip
RUN pip install wget \
                dask-kubernetes==0.4.0 \
                google-cloud==0.32.0 \
                google-cloud-storage \
                gsutil \
                statsmodels==0.9.0 \
                fusepy \
                click \
                jedi \
                kubernetes \
                pyasn1 \
                click \
                urllib3 \
                xesmf \
                --no-cache-dir


RUN apt-get install -y gfortran

RUN git clone --recurse-submodules -j4 https://github.com/bolliger32/clawpack.git \
    && cd clawpack \
    && pip install -e .

ENV CLAW=/clawpack-v5.4.1
ENV FC=gfortran

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