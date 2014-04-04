# Change to correct directory containing source files
src_dir=.
server_ip='localhost'
server_port=8000

# Start database, Pygmy.com, frontend servers, and Cacofonix updates.

python DatabaseServer.py --uid=0 --port=8000 -l &
python ObelixServer.py --uid=1 --port=8002 -l &
python ObelixServer.py --uid=2 --port=8003 -l &
python PygmyDotCom.py --port=8001 -l &
python Cacofonix.py --port=8004 --serport=8001 -l &
python StoneTablet.py --port=8005 --serport=8001 -l &
python StoneTablet.py --port=8006 --serport=8001 -l &
