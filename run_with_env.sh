#!/bin/bash
# Load environment variables from .env.local and run command
set -a
source .env.local
set +a
exec "$@"
