#!/bin/bash
sed -i "s/from pandas.core.internals import Block, NonConsolidatableMixIn, \
BlockManager/from pandas.core.internals.blocks import Block, \
NonCnsolidatableMixIn\nfrom pandas.core.internals.managers import \
BlockManager/g" /opt/conda/lib/python3.6/site-packages/geopandas/_block.py
