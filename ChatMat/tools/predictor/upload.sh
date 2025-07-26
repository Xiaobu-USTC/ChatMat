#!/bin/bash
echo "开始上传"
python upload_pseudopotentials.py POSCAR /home/gpu2/work/LvS/target \
    --config config.yaml --run run.sh --default_folder default \
    --hostname 114.214.197.165 --username gpu2 --password 'ustc@2021/.,' \
    --exec_command "cd /home/gpu2/work/LvS/target && ./run.sh" \
    --download ./statfile.0
