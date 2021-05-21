for i in bchla_gfn1 eigdiff dscf PBE0 CAMB3LYP; do 
	cd ${i}
	for j in *sub; do 
		if ! /usr/bin/grep -q "Total wall" ${j/sub/out} ; then
			echo ${j}
			/opt/pbs/bin/qsub ${j}
		fi
	done
	cd ../
done

