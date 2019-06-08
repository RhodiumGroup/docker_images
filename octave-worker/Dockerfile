FROM climateimpactlab/miniconda3-gfortran-netcdf:v1.0.2

# build conda

USER $NB_USER

RUN apt-get update && apt-get install -y octave

RUN conda config --add channels conda-forge
RUN conda update --yes conda
RUN conda create -n octave --yes -c conda-forge \
    dask-core=1.2.0 \
    dask=1.2.0 \
    distributed=1.28.1 \
    fusepy=2.0.4 \
    gcsfs=0.1.2 \
    lz4-c=1.8.1.2 \
    lz4=1.1.0 \
    matplotlib=3.0.2 \
    nb_conda_kernels=2.1.1 \
    nomkl=2.0 \
    numba=0.40.0 \
    numcodecs=0.5.5 \
    pip=18.1 \
    python=3.6 \
    tornado=5.0.2 \
    texinfo=6.6

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
RUN mkdir /opt/app
RUN mkdir /gcs

# pip install the RHG packages that we update frequently
# (keeping down here so that rest of image will stay
# cached when updating these versions)
RUN pip install \
  rhg_compute_tools==0.1.6 \
  impactlab-tools==0.3.1 \
  climate-toolbox==0.1.4 \
  --no-cache-dir

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
