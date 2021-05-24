for i in $(seq 0 1 1999); do
	for method in bchla_gfn1; do #PBE0 bchla CAMB3LYP BLYP dscf eigdiff
		sed -e "s/NAME/frame_${i}/g" -e "s/XYZ_FILE/frames\/frame_${i}.xyz/g" templates/${method}_template.in	> ${method}/${method}_frame_${i}.in
		
		sed "s/NAME/frame_${i}/g" templates/${method}_template.sub	> ${method}/${method}_frame_${i}.sub
	done
done
