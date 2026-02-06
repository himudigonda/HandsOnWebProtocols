#!/bin/bash

TEMP_DIR="./logs"
mkdir -p "$TEMP_DIR"

# Set PYTHONPATH to include the current directory for module resolution
export PYTHONPATH=.

echo "Starting REST server on 8000..."
uv run python src/servers/rest_server.py > "$TEMP_DIR/rest_server.log" 2>&1 &
REST_PID=$!

echo "Starting GraphQL server on 8001..."
uv run python src/servers/graphql_server.py > "$TEMP_DIR/graphql_server.log" 2>&1 &
GRAPHQL_PID=$!

echo "Starting SSE server on 8002..."
uv run python src/servers/sse_server.py > "$TEMP_DIR/sse_server.log" 2>&1 &
SSE_PID=$!

echo "Starting WebSocket server on 8003..."
uv run python src/servers/ws_server.py > "$TEMP_DIR/ws_server.log" 2>&1 &
WS_PID=$!

echo "Starting gRPC server on 50051..."
uv run python src/servers/grpc_server.py > "$TEMP_DIR/grpc_server.log" 2>&1 &
GRPC_PID=$!

echo "All servers triggered. PIDs: REST($REST_PID) GQL($GRAPHQL_PID) SSE($SSE_PID) WS($WS_PID) GRPC($GRPC_PID)"

# Give servers a moment to start
echo "Waiting for servers to initialize..."
sleep 5
