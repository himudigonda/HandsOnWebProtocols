#!/bin/bash

TEMP_DIR="./logs"
mkdir -p "$TEMP_DIR"

# Set PYTHONPATH to include the current directory for module resolution
export PYTHONPATH=.

echo "Starting REST server on 8000..."
uv run python src/servers/rest.py > "$TEMP_DIR/rest.log" 2>&1 &
REST_PID=$!

echo "Starting GraphQL server on 8001..."
uv run python src/servers/gql.py > "$TEMP_DIR/gql.log" 2>&1 &
GRAPHQL_PID=$!

echo "Starting SSE server on 8002..."
uv run python src/servers/sse.py > "$TEMP_DIR/sse.log" 2>&1 &
SSE_PID=$!

echo "Starting WebSocket server on 8003..."
uv run python src/servers/ws.py > "$TEMP_DIR/ws.log" 2>&1 &
WS_PID=$!

echo "Starting gRPC server on 50051..."
uv run python src/servers/grpc_impl.py > "$TEMP_DIR/grpc.log" 2>&1 &
GRPC_PID=$!

echo "All servers triggered. PIDs: REST($REST_PID) GQL($GRAPHQL_PID) SSE($SSE_PID) WS($WS_PID) GRPC($GRPC_PID)"
echo "Use 'pkill -f src/servers' to stop all."
