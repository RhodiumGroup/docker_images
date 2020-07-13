FROM jupyter/base-notebook@sha256:135779f39abfdfe75a6dbc50c7a15c55cc79c8231cd75f83aaabf87127c60adf
ARG DEBIAN_FRONTEND=noninteractive

## needed to make sure things with cython compile correctly
## (this will eventually become default in numpy)
ENV NPY_DISTUTILS_APPEND_FLAGS=1

## get rid of conda pin file that causes update problems
RUN rm /opt/conda/conda-meta/pinned


## Add NB_USER to sudo
USER root
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER


## filepath curation
RUN sudo mkdir /pre-home && sudo chown -R $NB_USER /pre-home
COPY worker-template.yml /pre-home
COPY add_service_creds.py /pre-home
COPY run_sql_proxy.py /pre-home
COPY config.yaml /pre-home

COPY shared_resources /tempdir

COPY prepare.sh /usr/bin
COPY overrides.json /opt/conda/share/jupyter/lab/settings/overrides.json


## perform a bunch of common actions
RUN sudo bash /tempdir/common.sh
RUN sudo chown -R $NB_USER /gcs


## more apt-get
RUN sudo DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
  vim less man locate kmod dialog \
  octave octave-optim && \
  sudo apt-get clean


# set up conda channels
RUN mkdir /opt/conda/specs
COPY shared_resources/base_environment.yml /opt/conda/specs
COPY notebook_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge && \
  conda config --set channel_priority strict

## set up conda
RUN conda update -n base conda

#  update environemnt with common packages across worker and nb
RUN conda env update -f /opt/conda/specs/base_environment.yml

# update environment with nb-specific packages
RUN conda env update -f /opt/conda/specs/notebook_environment.yml

RUN conda list -n base

# Compile MatI/O
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && g++ $CFLAGS -L/opt/conda/lib -lmatio /tempdir/matio_73to5.c -o \
    /opt/conda/bin/matio_73to5

## Set up jupyter lab extensions
RUN jupyter labextension update --all && \
    jupyter labextension install \
      @bokeh/jupyter_bokeh \
      @jupyter-widgets/jupyterlab-manager \
      @pyviz/jupyterlab_pyviz \
      @ryantam626/jupyterlab_code_formatter@1.3.1 \
      dask-labextension \
      jupyterlab-flake8 \
      jupyterlab-plotly \
      plotlywidget && \
    jupyter serverextension enable --py jupyterlab_code_formatter nbdime --sys-prefix

##################
## clawpack added for coastal-specific image
##################

ARG CLAWPACK_COMMIT
ENV CLAW=/clawpack
ENV NETCDF4_DIR=/opt/conda
ENV FC=gfortran
ENV LIB_PATHS=/opt/conda/lib
# Was getting weird behavior with any broad optimization flags (-O, -O2, -O3) wherein
# the boundary velocity error might be triggered on different boundaries if you piped
# both stdout and stderr to a file. If you only piped one or didn't pipe any, you 
# got one answer and if you piped both you got a different answer. Without the flags,
# you would get the same answer regardless (the one originally obtained when piping
# both out and err). To maintain a level of optimization, I just took all of the flags
# from O3 here: https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html and put them
# in individually. A few were removed due to compile or runtime errors. In addition, I
# added some flags applied by default from the conda gfortran compiler (-ftree-vectorize 
# -fPIC -fno-plt -ffunction-sections). I also added the march flag for the google 
# machines we are using (broadwell currently), and dropped fstack-protector-strong from
# the list of conda-based flags, as it was throwing segfaults.
ENV CLAW_FFLAGS="-DNETCDF -L/opt/conda/lib -lnetcdf -lnetcdff -I/opt/conda/include \
  -fauto-inc-dec -fbranch-count-reg -fcombine-stack-adjustments -fcompare-elim \
  -fcprop-registers -fdce -fdefer-pop -fdse -fforward-propagate \
  -fguess-branch-probability -fif-conversion -fif-conversion2 \
  -finline-functions-called-once -fipa-profile -fipa-pure-const -fipa-reference \
  -fmerge-constants -fmove-loop-invariants -fomit-frame-pointer -freorder-blocks \
  -fshrink-wrap -fshrink-wrap-separate -fsplit-wide-types -fssa-backprop -fssa-phiopt \
  -ftree-bit-ccp -ftree-ccp -ftree-ch -ftree-coalesce-vars -ftree-copy-prop -ftree-dce \
  -ftree-dominator-opts -ftree-dse -ftree-forwprop -ftree-fre -ftree-phiprop \
  -ftree-pta -ftree-scev-cprop -ftree-sink -ftree-slsr -ftree-sra -ftree-ter \
  -funit-at-a-time -freorder-blocks-algorithm=stc -freorder-blocks-and-partition \
  -freorder-functions -frerun-cse-after-loop -fschedule-insns -fschedule-insns2 \
  -fsched-interblock -fsched-spec -fstore-merging -fstrict-aliasing -fthread-jumps \
  -ftree-builtin-call-dce -ftree-pre -ftree-switch-conversion  -ftree-tail-merge \
  -ftree-vrp -fgcse  -fgcse-lm  -fhoist-adjacent-loads -finline-functions \
  -finline-small-functions -findirect-inlining -fipa-bit-cp  -fipa-cp  -fipa-icf \
  -fipa-ra  -fipa-sra  -fipa-vrp -fisolate-erroneous-paths-dereference -flra-remat \
  -foptimize-sibling-calls -foptimize-strlen -fpartial-inlining -fpeephole2 \
  -falign-functions -falign-jumps -falign-labels  -falign-loops -fcaller-saves \
  -fcode-hoisting -fcrossjumping -fcse-follow-jumps  -fcse-skip-blocks \
  -fdelete-null-pointer-checks -fdevirtualize  -fdevirtualize-speculatively \
  -fexpensive-optimizations -fgcse-after-reload -floop-unroll-and-jam -fpeel-loops \
  -fpredictive-commoning -fsplit-loops -fsplit-paths -ftree-loop-distribution \
  -ftree-loop-vectorize -ftree-partial-pre -ftree-slp-vectorize -funswitch-loops \
  -fvect-cost-model -fvect-cost-model=dynamic -march=broadwell -ftree-vectorize -fPIC \
  -fno-plt -ffunction-sections"

# need to change shell in order for source command to work
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# install clawpack (use root to access /clawpack and then fix permissions)
USER root
RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && pip install --src=$(dirname $CLAW) -e \
    git+https://github.com/climateimpactlab/clawpack.git@${CLAWPACK_COMMIT}#egg=clawpack
RUN /tempdir/fix-permissions.sh /clawpack
RUN /tempdir/fix-permissions.sh /opt/conda
USER $NB_USER

RUN source /opt/conda/etc/profile.d/conda.sh \
  && conda activate \
  && export EXE=$CLAW/geoclaw/xgeoclaw \
  && export FFLAGS=$CLAW_FFLAGS \
  && make -f /tempdir/Makefile.clawpack new \
  && export EXE=$CLAW/geoclaw/xgeoclaw_omp \
  && export FFLAGS="$FFLAGS -fopenmp" \
  && make -f /tempdir/Makefile.clawpack new

##################

## clean up
RUN sudo rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean -yaf

## prepare container
WORKDIR $HOME
ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start-notebook.sh"]
