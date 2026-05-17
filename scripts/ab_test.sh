set -euo pipefail

BACKEND_BASE="${BACKEND_BASE:-http://127.0.0.1:8000}"
NGINX_BASE="${NGINX_BASE:-http://127.0.0.1:8080}"

read -r -p "Сценарий (1 - GET напрямую на бэкенд, 2 - POST через NGINX, 3 - GET через NGINX): " choice
read -r -p "Всего запросов: " nreq
N="$nreq"
read -r -p "Количество конкурирующих запросов: " nreq
C="$nreq"


case "$choice" in
  1)
    ab -n "$N" -c "$C" "${BACKEND_BASE}/api/history"
    ;;
  2)
    echo "promo" > /tmp/empty.post
    ab -n "$N" -c "$C" -p /tmp/empty.post -T application/x-www-form-urlencoded \
    "${NGINX_BASE}/api/generate"
    ;;
  3)
    ab -n "$N" -c "$C" "${NGINX_BASE}/api/history"
    ;;
esac
