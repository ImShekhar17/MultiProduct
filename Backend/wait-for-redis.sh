#!/bin/sh
set -e

HOST="$1"
shift

until nc -z "$HOST" 6379; do
  echo "Waiting for Redis at $HOST..."
  sleep 2
done

echo "Redis is ready"
exec "$@"
