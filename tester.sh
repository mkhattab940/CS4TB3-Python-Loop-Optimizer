
python read_in_functions.py $1 > /dev/null

prefix=`echo $1 | sed 's/\(.*\)\.py/\1/'`

old=`./timer.sh $1 $2`
echo "OLD: $old seconds"

new=`./timer.sh $prefix"_opt.py" $2`
echo "NEW: $new seconds"

VAR=$(bc <<< "scale=6;$old/$new")
echo "--"
echo "SPEEDUP: $VAR"
