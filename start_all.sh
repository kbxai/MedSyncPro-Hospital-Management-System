#!/bin/bash
echo "========================================="
echo " MedSyncPro - Starting All Services"
echo "========================================="

DIR="$(cd "$(dirname "$0")" && pwd)"

# ---- Stop any old instances ----
taskkill //F //IM redis-server.exe 2>/dev/null || true
taskkill //F //IM MailHog_windows_amd64.exe 2>/dev/null || true
taskkill //F //IM node.exe 2>/dev/null || true
sleep 1

# ---- Redis (portable) ----
echo ""
echo "[1] Redis..."
REDIS_DIR="$DIR/.redis"
if [ ! -f "$REDIS_DIR/redis-server.exe" ]; then
  echo "    Downloading portable Redis..."
  mkdir -p "$REDIS_DIR"
  curl -sSL -o "$REDIS_DIR/redis.zip" "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
  unzip -qo "$REDIS_DIR/redis.zip" -d "$REDIS_DIR"
  rm -f "$REDIS_DIR/redis.zip"
fi
echo "bind 127.0.0.1
port 6379
save \"\"
appendonly no" > "$REDIS_DIR/redis.conf"
"$REDIS_DIR/redis-server.exe" "$REDIS_DIR/redis.conf" &
sleep 2
echo "    OK -> 127.0.0.1:6379"

# ---- MailHog ----
echo "[2] MailHog..."
cd "$DIR"
if [ ! -f "MailHog_windows_amd64.exe" ]; then
  echo "    Downloading MailHog..."
  curl -sSL -o MailHog_windows_amd64.exe "https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_windows_amd64.exe"
fi
./MailHog_windows_amd64.exe > /dev/null 2>&1 &
sleep 1
echo "    OK -> http://localhost:8025"

# ---- Backend ----
echo "[3] Backend..."
cd "$DIR/backend"
if [ ! -d "env" ]; then
  python -m venv env
fi
source env/Scripts/activate
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q
echo "    Dependencies ready."

python app.py > /dev/null 2>&1 &
sleep 2
echo "    Flask -> http://localhost:5000"

celery -A celery_worker.celery_app worker --pool=solo --loglevel=warning > /dev/null 2>&1 &
celery -A celery_worker.celery_app beat --loglevel=warning > /dev/null 2>&1 &
sleep 1
echo "    Celery worker + beat started."

# ---- Frontend ----
echo "[4] Frontend..."
cd "$DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm list bootstrap >/dev/null 2>&1 || npm install bootstrap
npm list bootstrap-icons >/dev/null 2>&1 || npm install bootstrap-icons
npm run serve > /dev/null 2>&1 &
sleep 3
echo "    Vue -> http://localhost:8080"

# ---- Done ----
echo ""
echo "========================================="
echo " ALL RUNNING"
echo ""
echo "   Redis     : 127.0.0.1:6379"
echo "   MailHog   : http://localhost:8025"
echo "   Flask API : http://localhost:5000"
echo "   Frontend  : http://localhost:8080"
echo ""
echo "   Press Ctrl+C to stop all."
echo "========================================="

cleanup() {
  trap - INT TERM  
  echo ""
  echo "Stopping all services..."
  kill 0 2>/dev/null
  exit 0
}

trap cleanup INT TERM
wait