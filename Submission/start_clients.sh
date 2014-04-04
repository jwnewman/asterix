# Change to correct directory containing source files
src_dir=.
server_ip=localhost
server_port=8000

# TO RUN LOCALLY (default), add -l to command

# Number of clients for client-pull mode
N=2
arch=pull
mode=random

for (( i=1; i<=$N; i++ ))
do
	port=$((8005+$i))	
	python $src_dir/StoneTablet.py --port=$port --serip=$server_ip --serport $server_port -l &
	echo $!
done

# DEPRECATED FOR LAB 2
# Number of clients for server-push mode
# M=0
# arch=push
# for (( j=1; j<=$M; j++ ))
# do
# 	port=$((8001+$N+$j))
# 	python $src_dir/StoneTablet.py --run_locally $run_locally --port $port --serip $server_ip --serport $server_port --arch $arch --mode $mode &
# 	echo $!
# done
