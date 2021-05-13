for i in BLYP bchla PBE0 CAMB3LYP PBE0 eigdiff dscf
do 
	cd ${i}
	for j in *sub;
	do 
		echo ${j}
		/opt/pbs/bin/qsub ${j}
	done
	cd ../
done

