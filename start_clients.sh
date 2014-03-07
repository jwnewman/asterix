# Change to correct directory containing source files
src_dir=/Users/aaronschein/Documents/courses/spring14/systems/labs/asterix
server_ip=localhost
server_port=8000

ip=localhost

# Number of clients in client-pull mode
N=3
arch=pull
mode=random

for (( i=1; i<=$N; i++ ))
do
	port=$((8001+$i))	
	python $src_dir/StoneTablet.py --ip $ip --port $port --serip $server_ip --serport $server_port --arch $arch --mode $mode &
	echo $!
done

# Number of clients in server-push mode
M=3
arch=push
for (( j=1; j<=$M; j++ ))
do
	port=$((8001+$N+$j))
	python $src_dir/StoneTablet.py --ip $ip --port $port --serip $server_ip --serport $server_port --arch $arch --mode $mode &
	echo $!
done

# Start-up N clients in client-pull mode

# for i in {1..$N}
# do
#    python $src_dir/StoneTablet.py &
#    var=$!
# done
# python $src_dir/StoneTablet.py --ip $ip --port $port --serip $server_ip --serport $server_port --arch $arch --mode $mode --rate $pull_rate

# Start-up M clients in server-push mode


