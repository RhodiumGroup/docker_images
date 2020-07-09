## using same container as jupyter/base-notebook:python-3.7.3
FROM ubuntu:focal-20200423@sha256:238e696992ba9913d24cfc3727034985abd136e08ee3067982401acdc30cbf3f
ARG DEBIAN_FRONTEND=noninteractive
ENV NPY_DISTUTILS_APPEND_FLAGS=1
ENV MPLBACKEND=Agg

## filepath curation
RUN mkdir /tempdir
COPY common.sh /tempdir
COPY Makefile.clawpack /tempdir

COPY add_service_creds.py /usr/bin
COPY prepare.sh /usr/bin


## perform a bunch of common actions
RUN bash /tempdir/common.sh


###########
## install miniconda
# adapted from continuumio/miniconda3

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc
###########


## set up conda channels
RUN mkdir /opt/conda/specs
COPY base_environment.yml /opt/conda/specs
RUN conda config --add channels conda-forge && \
    conda config --set channel_priority strict


## set up python env
RUN conda update -n base conda
RUN conda env update -f /opt/conda/specs/base_environment.yml
RUN conda list -n base

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

# install clawpack
RUN source /opt/conda/etc/profile.d/conda.sh \
    && conda activate \
    && pip install --src=$(dirname $CLAW) -e \
        git+https://github.com/climateimpactlab/clawpack.git@${CLAWPACK_COMMIT}#egg=clawpack

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
RUN rm -rf /var/lib/apt/lists/* /tempdir
RUN conda clean -yaf

## prepare container
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
