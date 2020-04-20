#!/bin/bash
#SBATCH --ntasks=12

cd $SLURM_SUBMIT_DIR

n=10000000

touch runtime_history.txt

for p in {1..12}

do
	start_=`date +%s%3N`
	time mpiexec --allow-run-as-root -n $p python cal_integral.py $n
	end_=`date +%s%3N`

	runtime=$((end_-start_))

	text="$runtime $p $n"

	echo $text >> runtime_history.txt
	echo $runtime

done	

