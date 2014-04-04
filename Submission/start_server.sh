# Change to correct directory containing source files
src_dir=.

# Uncomment for testing on local
run_locally=False  #'True' or 'False'
server_port=8000

python $src_dir/ObelixServer.py --run_locally $run_locally --serport $server_port