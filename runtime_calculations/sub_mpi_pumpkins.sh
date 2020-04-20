#!/bin/bash
#SBATCH --ntasks=12

cd $SLURM_SUBMIT_DIR

sudo touch runtime_pumpkins_history.txt
sudo chmod -R a+rw runtime_pumpkins_history.txt

for p in {1..12}
do
	start_=`date +%s%3N`
	mpiexec --allow-run-as-root -n $p python cal_pumpkins.py
	end_=`date +%s%3N`

	runtime=$((end_-start_))
	text="nodes $runtime $p"

	echo $text >> runtime_pumpkins_history.txt
	echo $runtime
done
