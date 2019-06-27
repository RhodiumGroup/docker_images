FROM climateimpactlab/miniconda3-gfortran-netcdf:v1.0.2

# build conda

USER $NB_USER

RUN apt-get update && apt-get install -y octave

RUN conda config --add channels conda-forge
RUN conda install --yes conda=4.7.5
RUN conda create -n octave --yes -c conda-forge \
    dask-core=1.2.0 \
    dask=1.2.0 \
    cloudpickle=0.5.3 \
    distributed=1.28.1 \
    fastparquet=0.3.1 \
    fusepy=2.0.4 \
    gcsfs=0.1.2 \
    lz4-c=1.8.1.2 \
    lz4=1.1.0 \
    matplotlib=3.0.3 \
    nb_conda_kernels=2.1.1 \
    netcdf-fortran=4.4.5 \
    netcdf4=1.5.1.2 \
    numba=0.40.0 \
    numcodecs=0.6.3 \
    numpy=1.16.4 \
    pandas=0.23.4 \
    pip=18.1 \
    python=3.6 \
    rise=5.5.0 \
    tornado=5.0.2 \
    texinfo=6.6 \
    urllib3=1.23 \
    xarray=0.11.3 \
    zarr=2.3.2 \
    zict=0.1.4

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

RUN /opt/conda/envs/octave/bin/pip install \
    git+git://github.com/dask/dask-kubernetes.git@295f06428119bc8e674a2e6a59cd97000fae69e8 \
    google-cloud-storage==1.12.0 \
    pyasn1-modules==0.2.2 \
    pyasn1==0.4.3 \
    wget==3.2 \
    metakernel==0.24.2 \
    octave_kernel==0.31.0 \
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
