#!/bin/bash

TEMP_DIR="./logs"
mkdir -p "$TEMP_DIR"

# Set PYTHONPATH to include the current directory for module resolution
export PYTHONPATH=.

echo "Starting REST server..."
uv run python src/servers/rest_server.py > "$TEMP_DIR/rest_server.log" 2>&1 &
REST_PID=$!
echo "REST server started with PID: $REST_PID"

echo "Starting GraphQL server..."
uv run python src/servers/graphql_server.py > "$TEMP_DIR/graphql_server.log" 2>&1 &
GRAPHQL_PID=$!
echo "GraphQL server started with PID: $GRAPHQL_PID"

echo "Starting gRPC server..."
uv run python src/servers/grpc_server.py > "$TEMP_DIR/grpc_server.log" 2>&1 &
GRPC_PID=$!
echo "gRPC server started with PID: $GRPC_PID"

echo "All servers started. PIDs: $REST_PID $GRAPHQL_PID $GRPC_PID"

# Give servers a moment to start and write to logs
sleep 5
