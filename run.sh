pipenv run python blockchain.py -p 5000 &
PID1=$!
pipenv run python blockchain.py -p 5001 &
PID2=$!
pipenv run python blockchain.py -p 5002 &
PID3=$!
pipenv run python blockchain_adversary.py -p 5003 & 
PID4=$!

sleep 5


curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["http://localhost:5000", "http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]}' "http://localhost:5000/nodes/register" &
curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["http://localhost:5000", "http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]}' "http://localhost:5001/nodes/register" &
curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["http://localhost:5000", "http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]}' "http://localhost:5002/nodes/register" &
curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["http://localhost:5000", "http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]}' "http://localhost:5003/nodes/register" &


sleep 10
echo "KILLING!!!!!!!!!!!!!!!!!!!!!"
kill -SIGINT $PID1
