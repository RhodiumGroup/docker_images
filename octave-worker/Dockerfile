FROM climateimpactlab/miniconda3-gfortran-netcdf:v1.0.2

# build conda

USER $NB_USER

RUN conda config --add channels conda-forge
RUN conda update --yes conda

RUN mkdir /opt/conda/specs
COPY environment.yml /opt/conda/specs/environment.yml
RUN conda env create -f /opt/conda/specs/environment.yml

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk kubectl -y

RUN export GCSFUSE_REPO=gcsfuse-xenial \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update \
  && apt-get install gcsfuse -y \
  && alias googlefuse=/usr/bin/gcsfuse

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
    rhg_compute_tools==0.1.8 \
    impactlab-tools==0.3.1 \
    climate-toolbox==0.1.5 \
    parameterize_jobs==0.1.1 \
    --no-cache-dir

# update pip
RUN /opt/conda/envs/worker/bin/pip install --upgrade pip

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/bin/prepare.sh"]
