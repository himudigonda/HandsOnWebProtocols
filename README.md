# Protocol Lab

A hands-on lab for comparing various application layer protocols (REST, GraphQL, gRPC) with benchmarks.

## Prerequisites

- [uv](https://github.com/astral-sh/uv) (for Python package management)
- Python 3.12+

## Installation

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Make scripts executable:**

   ```bash
   chmod +x start_servers.sh
   ```

## Setup (Protobuf Generation)

You need to generate the gRPC code from the protocol buffer definitions.

1. **Generate gRPC code:**

   ```bash
   uv run python -m grpc_tools.protoc -I. --python_out=src/servers --grpc_python_out=src/servers protos/logs.proto
   ```

2. **Fix Generated Import Issue:**

   The generated gRPC code uses an absolute import that doesn't resolve correctly in this structure. Apply this fix:

   ```bash
   sed -i '' 's/from protos import logs_pb2/from . import logs_pb2/' src/servers/protos/logs_pb2_grpc.py
   ```

## Running the Servers

Start all servers (REST, GraphQL, SSE, WebSockets, gRPC) in the background:

```bash
./start_servers.sh
```

This will start:

- **REST API**: `http://localhost:8000`
- **GraphQL API**: `http://localhost:8001`
- **SSE Stream**: `http://localhost:8002`
- **WebSocket**: `ws://localhost:8003`
- **gRPC Server**: `localhost:50051`

Logs are written to the `logs/` directory.

## Advanced Benchmarking & Scaling

The project has been scaled to **1,400,000+ records** to test protocol efficiency under real-world load.

### New Features

- **SSE (Server-Sent Events)**: Streaming logs on port `8002`.
- **WebSockets**: Interactive filtered streams on port `8003`.
- **Advanced Benchmark Suite**: Multi-category testing (Latency, Concurrency, Throughput).
- **Rich Visualization**: Terminal-based reporting using `rich`.

### Running Advanced Benchmarks

```bash
PYTHONPATH=. uv run python src/benchmarks/advanced_benchmark.py
```

### Interactive Demo (SSE & WebSockets)

Experience real-time streaming:

```bash
PYTHONPATH=. uv run python src/client/interactive_demo.py
```

### Running Tests

Ensure servers are running, then:

```bash
PYTHONPATH=. uv run pytest tests/
```

### Technical Scalability

The database seeding uses optimized SQL batching to achieve high insertion speeds for millions of rows in SQLite.

## Stopping Servers

The `start_servers.sh` script runs servers in the background. To stop them:

```bash
pkill -f "src/servers"
```
