# Change to correct directory containing source files
src_dir=.
server_ip='localhost'
server_port=8000

# Begin Olympic games and Cacofonix updates
cacofonix_port=8001

mode=testing
update_rate=4

python $src_dir/Cacofonix.py --port $cacofonix_port --serip $server_ip --serport $server_port --mode $mode --rate $update_rate