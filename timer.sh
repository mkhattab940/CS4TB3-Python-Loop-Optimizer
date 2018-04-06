#!/bin/bash
tests=$2

start=$(date +%s.%N)
# do something
# start your script work here
for ((i=0; i<=tests; i++))
do
	python $1 > /dev/null
done
# your logic ends here
dur=$(echo "$(date +%s.%N) - $start" | bc)
echo "$dur"

