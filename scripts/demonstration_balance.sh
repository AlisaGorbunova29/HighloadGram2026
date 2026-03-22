set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "promo" > /tmp/empty.post
ab -n 100 -c 10 -p /tmp/empty.post -T application/x-www-form-urlencoded \
   http://127.0.0.1:8080/api/generate

LOGS=$(docker compose logs app1 app2)
COUNT_APP1=$(echo "$LOGS" | grep -o 'instance=app1' | wc -l | tr -d ' ')
COUNT_APP2=$(echo "$LOGS" | grep -o 'instance=app2' | wc -l | tr -d ' ')

echo "instance=app1 : $COUNT_APP1"
echo "instance=app2 : $COUNT_APP2"
