#!/bin/bash

# manually edit geopandas/label/dev to match current pandas deployment
# see https://github.com/geopandas/geopandas/issues/473#issuecomment-465060849
# should be removed if geopandas core becomes vectorized, whether the
# cythonized branch gets merged in or the geometry calculations are handled
# by pyGEOS, either through shapely or replacing shapely. See
# https://github.com/Toblerity/Shapely/issues/782.
sed -i "s/from pandas.core.internals import Block, NonConsolidatableMixIn, \
BlockManager/from pandas.core.internals.blocks import Block, \
NonConsolidatableMixIn\nfrom pandas.core.internals.managers import \
BlockManager/g" /opt/conda/lib/python3.6/site-packages/geopandas/_block.py
