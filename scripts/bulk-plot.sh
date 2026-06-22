#!/bin/bash

SHABANIPY_SCRIPTS=~/repos/shabanipy/scripts

COMMONARGS='--icp_err_col=rmse+ --icm_err_col=rmse- --quiet'
find ../data/processed/extract_ic -type f -name data.csv -exec \
  python $SHABANIPY_SCRIPTS/jj/plot_ic.py $COMMONARGS --icp_col='ic+' --icm_col='ic-' {} \;
find ../data/processed/centermax -type f -name data.csv -exec \
  python $SHABANIPY_SCRIPTS/jj/plot_ic.py $COMMONARGS --icp_col='ic+ from fit' --icm_col='ic- from fit' {} \;
