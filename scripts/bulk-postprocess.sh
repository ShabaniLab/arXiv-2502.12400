#!/bin/bash

# Stitch Wsc→∞ scans
python stitch_inf.py

# Invert current to conform to sign convention
find ../data/processed/centermax -type f \
  -regex '.*Wsc=0\.\(3um-N\|6um-NNW\|9um-NNE_WFS06\)_.*/data.csv' \
  | xargs python invert_current.py

# Compute diode
find ../data -type f -path */JS633-W2*/*/data.csv -exec \
  python compute_diode.py {} \;

# Mask, dedupe, and smooth
python mask.py    # --> data_qca.csv
python dedupe.py  # --> data_deduped.csv
python savgol.py  # --> data_deduped.csv

# Concatenate
find -E ../data -type f \
  -regex ".*/JS633-W2/Wsc=([01].[0-9]um-[NSEW]+_diode[+-][0-9.]+V|inf-SSE_diode(\+10V|-0V|-3V_coarsefield))/data_deduped.csv" \
  | xargs python concat_csvs.py -f --output_filename 'data_concat.csv' \
  --rename "VectorMagnet - Field Y" --to "field" \
  --rename "VectorMagnet - Field Z" --to "field" \
  --rename "in-plane magnitude" --to "field"

# Fit low-field Ic±(B∥) data
COMMONARGS='--quiet --icp_err_col=rmse+ --icm_err_col=rmse-'
FILENAME='data_qca'
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.3um-N_diode-3.5V/${FILENAME}.csv"  $COMMONARGS --bmax 0.150
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.3um-N_diode-0V/${FILENAME}.csv"    $COMMONARGS --bmax 0.150
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-4V/${FILENAME}.csv"  $COMMONARGS --bmax 0.100 --bcol 'in-plane magnitude'
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-0V/${FILENAME}.csv"  $COMMONARGS --bmax 0.100
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode+10V/${FILENAME}.csv" $COMMONARGS --bmax 0.100 --bcol 'in-plane magnitude'
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.9um-ENE_diode-3V/${FILENAME}.csv"  $COMMONARGS --bmax 0.100
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.9um-ENE_diode-0V/${FILENAME}.csv"  $COMMONARGS --bmax 0.100
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=0.9um-ENE_diode+10V/${FILENAME}.csv" $COMMONARGS --bmax 0.100
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode-3.5V/${FILENAME}.csv"  $COMMONARGS --bmax 0.095
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode-0V/${FILENAME}.csv"    $COMMONARGS --bmax 0.095
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode+10V/${FILENAME}.csv"   $COMMONARGS --bmax 0.095
#python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode-3V/${FILENAME}.csv"   $COMMONARGS --bmax 0.060 --icp_col 'ic+' --icm_col 'ic-' --bmask 0.025
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode-3V_coarsefield/${FILENAME}.csv"   $COMMONARGS --bmax 0.060 --icp_col 'ic+' --icm_col 'ic-' --bmask 0.010
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode-0V/${FILENAME}.csv"   $COMMONARGS --bmax 0.060 --icp_col 'ic+' --icm_col 'ic-'
python $SHABANIPY_SCRIPTS/jj/fit_diode.py "../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode+10V/${FILENAME}.csv"  $COMMONARGS --bmax 0.060 --icp_col 'ic+' --icm_col 'ic-' --bmask 0.010
find ../data -type f -path ".*/fit_diode/${FILENAME}_fit.csv" \
  | xargs python concat_csvs.py -f --output_filename 'icpm_fitparams.csv'
python unpack_filename.py '../data/processed/icpm_fitparams.csv'
python get_argminmax_from_fits.py '../data/processed/icpm_fitparams.csv'

# cubic splines
python spline.py --quiet --bmax 0.50 '../data/processed/centermax/JS633-W2/Wsc=0.3um-N_diode-3.5V/data_deduped.csv'
python spline.py --quiet --bmax 0.50 '../data/processed/centermax/JS633-W2/Wsc=0.3um-N_diode-0V/data_deduped.csv'
python spline.py --quiet --bmax 0.30 '../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-4V/data_deduped.csv' --bcol 'in-plane magnitude'
python spline.py --quiet --bmax 0.30 '../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode-0V/data_deduped.csv'
python spline.py --quiet --bmax 0.30 '../data/processed/centermax/JS633-W2/Wsc=0.6um-NNW_diode+10V/data_deduped.csv' --bcol 'in-plane magnitude'
python spline.py --quiet --bmax 0.20 '../data/processed/centermax/JS633-W2/Wsc=0.9um-ENE_diode-3V/data_deduped.csv'
python spline.py --quiet --bmax 0.20 '../data/processed/centermax/JS633-W2/Wsc=0.9um-ENE_diode-0V/data_deduped.csv'
python spline.py --quiet --bmax 0.20 '../data/processed/centermax/JS633-W2/Wsc=0.9um-ENE_diode+10V/data_deduped.csv'
python spline.py --quiet --bmax 0.20 '../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode-3.5V/data_deduped.csv'
python spline.py --quiet --bmax 0.20 '../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode-0V/data_deduped.csv'
python spline.py --quiet --bmax 0.30 '../data/processed/centermax/JS633-W2/Wsc=1.2um-E_diode+10V/data_deduped.csv'
#python spline.py --quiet --bmax 0.20 '../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode-3V/data_deduped.csv' \
#  --icp_col='ic+ smoothed' --icm_col='ic- smoothed' --delta_col='delta smoothed' --eta_col='eta smoothed'
python spline.py --quiet --bmax 0.20 '../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode-3V_coarsefield/data_deduped.csv' \
  --icp_col='ic+ smoothed' --icm_col='ic- smoothed' --delta_col='delta smoothed' --eta_col='eta smoothed'
python spline.py --quiet --bmax 0.20 '../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode-0V/data_deduped.csv' \
  --icp_col='ic+ smoothed' --icm_col='ic- smoothed' --delta_col='delta smoothed' --eta_col='eta smoothed'
python spline.py --quiet --bmax 0.30 '../data/processed/extract_ic/JS633-W2/Wsc=inf-SSE_diode+10V/data_deduped.csv' \
  --icp_col='ic+ smoothed' --icm_col='ic- smoothed' --delta_col='delta smoothed' --eta_col='eta smoothed'
find ../data -maxdepth 6 -type f -path '.*/spline/data*spline.csv' | xargs python concat_csvs.py -f --output_filename 'spline_extrema.csv'
python unpack_filename.py '../data/processed/spline_extrema.csv'
