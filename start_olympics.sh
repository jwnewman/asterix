# Change to correct directory containing source files
src_dir=.

# Start-up database
python $src_dir/DatabaseServer.py --uid=0 --serport=8000 -l

# Start-up Cacofonix updates
python $src_dir/Cacofonix.py --port=8004 --serport=8001 -l



