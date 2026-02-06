# Protocol Lab

A hands-on lab for comparing various application layer protocols (REST, GraphQL, gRPC) with benchmarks.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (for Python package management)
- Python 3.12+

## Installation

1.  **Install dependencies:**
    ```bash
    uv sync
    ```

2.  **Make scripts executable:**
    ```bash
    chmod +x start_servers.sh
    ```

## Setup (Protobuf Generation)

You need to generate the gRPC code from the protocol buffer definitions.

1.  **Generate gRPC code:**
    ```bash
    uv run python -m grpc_tools.protoc -I. --python_out=src/servers --grpc_python_out=src/servers protos/logs.proto
    ```

2.  **Fix Generated Import Issue:**
    The generated gRPC code uses an absolute import that doesn't resolve correctly in this structure. Apply this fix:
    ```bash
    sed -i '' 's/from protos import logs_pb2/from . import logs_pb2/' src/servers/protos/logs_pb2_grpc.py
    ```

## Running the Servers

Start all servers (REST, GraphQL, gRPC) in the background:

```bash
./start_servers.sh
```

This will start:
- **REST API**: `http://localhost:8000`
- **GraphQL API**: `http://localhost:8001`
- **gRPC Server**: `localhost:50051`

 Logs are written to the `logs/` directory.

## Running Benchmarks

Run the benchmark script to compare the performance of the different protocols:

```bash
# PYTHONPATH=. is required to resolve the 'src' module
PYTHONPATH=. uv run python src/benchmarks/benchmark.py
```

## Stopping Servers

The `start_servers.sh` script runs servers in the background. To stop them, you can find their PIDs in the output of the start command, or use `pkill` (use with caution):

```bash
pkill -f "src/servers"
```
