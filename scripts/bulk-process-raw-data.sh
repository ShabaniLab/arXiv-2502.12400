#!/bin/bash

# Usage:
#   (bash bulk-process-raw-data.sh > >(tee logs/stdout.log) 2> >(tee logs/stderr.log >&2)) &> >(tee logs/stdall.log)    

#set -x # print commands as they're executed
#set -e # exit script if a command fails

pushd ~/repos/shabanipy/scripts/jj/fraunhofer

# Wsc=0.3um
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.3um-N_diode-3.5V
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.3um-N_diode-0V

# Wsc=0.6um
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.6um-NNW_diode-4V
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.6um-NNW_diode-0V
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.6um-NNW_diode+10V
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.6um-NNW_diode-y
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.6um-NNW_diode-angle-125mT

# Wsc=0.9um-ENE
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.9um-ENE_diode-3V
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.9um-ENE_diode-0V
python -u centermax.py -f configs/JS633-W2.ini Wsc=0.9um-ENE_diode+10V

# Wsc=1.2um
python -u centermax.py -f configs/JS633-W2.ini Wsc=1.2um-E_diode-3.5V
python -u centermax.py -f configs/JS633-W2.ini Wsc=1.2um-E_diode-0V
python -u centermax.py -f configs/JS633-W2.ini Wsc=1.2um-E_diode+10V

# Wsc=inf is anomalous (not centermax fraunhofers)
cd ..
declare -a datafiles=(                                      # field values are approximate
  "Data_1011/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-078.hdf5"  #   0V, -350mT to -50mT
  "Data_1011/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-079.hdf5"  #   0V,  -50mT to 350mT
  "Data_1013/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-101.hdf5"  # +10V, -200mT to 200mT
  "Data_1014/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-104.hdf5"  # +10V,  200mT to 800mT (noise interruption ~825mT)
  "Data_1017/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-120.hdf5"  #  -3V, -200mT to 200mT (0-field dip)
  "Data_1018/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-121.hdf5"  #  -3V,  200mT to 400mT
  "Data_1022/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-156.hdf5"  #  -3V, -200mT to 200mT (redo lower resolution, no 0-field dip)
)
for df in "${datafiles[@]}"
do
  python -u extract_ic.py \
    --ch_measured "source/fundamental - Value" \
    --ch_source_ac "source/fundamental - Value" \
    --resistor_ac 1e6 \
    --ch_source_dc "Yoko - Voltage" \
    --resistor_dc 1e6 \
    --ch_variable "VectorMagnet - Field Z" \
    --offset_npoints 10 \
    --threshold 80e-9 \
    --vmin=0 \
    --vmax=500 \
    --branch +- \
    --datapath "2023/10/${df}" \
    --no-show
done
# use auto-thresholding at high field
declare -a highfield=(                                      # field values are approximate
  "Data_1011/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-082.hdf5"  #   0V,  350mT to 1.5T (noise interruption ~1.7T)
  "Data_1015/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-109.hdf5"  # +10V,  800mT to 2T
  "Data_1018/JS633-W2_Wsc@v3.1_Wsc=inf-SSE_WFS03-122.hdf5"  #  -3V,  400mT to 1.5T
)
for df in "${highfield[@]}"
do
  python -u extract_ic.py \
    --ch_measured "source/fundamental - Value" \
    --ch_source_ac "source/fundamental - Value" \
    --resistor_ac 1e6 \
    --ch_source_dc "Yoko - Voltage" \
    --resistor_dc 1e6 \
    --ch_variable "VectorMagnet - Field Z" \
    --ignore_npoints 6 \
    --vmin=0 \
    --vmax=500 \
    --branch +- \
    --datapath "2023/10/${df}" \
    --no-show
done
