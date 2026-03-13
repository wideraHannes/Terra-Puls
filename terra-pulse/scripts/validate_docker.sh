#!/bin/bash
# Validate that docker compose stack is healthy
# Usage: ./scripts/validate_docker.sh

set -e

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
REDIS_PORT=6379
PG_PORT=5432

echo "=== Terra Pulse Docker Stack Validation ==="
echo ""

# Check backend health
echo "1. Checking backend health..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
if [ "$STATUS" = "200" ]; then
    echo "   ✓ Backend healthy (HTTP $STATUS)"
else
    echo "   ✗ Backend FAILED (HTTP $STATUS)"
    exit 1
fi

# Check Redis
echo "2. Checking Redis..."
if redis-cli -p $REDIS_PORT ping | grep -q PONG; then
    echo "   ✓ Redis responding to PING"
else
    echo "   ✗ Redis FAILED"
    exit 1
fi

# Check PostgreSQL port
echo "3. Checking PostgreSQL port..."
if nc -z localhost $PG_PORT 2>/dev/null; then
    echo "   ✓ PostgreSQL port $PG_PORT is open"
else
    echo "   ✗ PostgreSQL FAILED"
    exit 1
fi

# Check countries endpoint
echo "4. Checking countries API..."
COUNTRIES_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/countries")
if [ "$COUNTRIES_STATUS" = "200" ]; then
    echo "   ✓ Countries API (HTTP $COUNTRIES_STATUS)"
else
    echo "   ✗ Countries API FAILED (HTTP $COUNTRIES_STATUS)"
    exit 1
fi

# Check pulse endpoint
echo "5. Checking pulse API..."
PULSE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/pulse")
if [ "$PULSE_STATUS" = "200" ]; then
    echo "   ✓ Pulse API (HTTP $PULSE_STATUS)"
else
    echo "   ✗ Pulse API FAILED (HTTP $PULSE_STATUS)"
    exit 1
fi

# Check frontend
echo "6. Checking frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✓ Frontend (HTTP $FRONTEND_STATUS)"
else
    echo "   ✗ Frontend FAILED (HTTP $FRONTEND_STATUS)"
    # Don't exit — frontend may take longer
fi

echo ""
echo "=== All core checks passed! ==="
