import os
import signal
import socket
import subprocess
import time
from typing import Dict, Optional

import psutil

SERVER_MAP = {
    "REST": {"cmd": ["uv", "run", "python", "src/servers/rest.py"], "port": 8000},
    "GraphQL": {"cmd": ["uv", "run", "python", "src/servers/gql.py"], "port": 8001},
    "SSE": {"cmd": ["uv", "run", "python", "src/servers/sse.py"], "port": 8002},
    "WebSocket": {"cmd": ["uv", "run", "python", "src/servers/ws.py"], "port": 8003},
    "gRPC": {"cmd": ["uv", "run", "python", "src/servers/grpc_impl.py"], "port": 50051},
}


class ServerManager:
    """Singleton to manage background server processes"""

    _processes: Dict[str, subprocess.Popen] = {}

    @staticmethod
    def is_port_open(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    @staticmethod
    def start(protocol: str):
        cfg = SERVER_MAP.get(protocol)
        if not cfg:
            return

        # If already tracked and running, skip
        if protocol in ServerManager._processes:
            if ServerManager._processes[protocol].poll() is None:
                return
            else:
                del ServerManager._processes[protocol]

        # If port is already open by someone else, we might still want to track it or just skip
        if ServerManager.is_port_open(cfg["port"]):
            print(f"Port {cfg['port']} for {protocol} is already open.")
            return

        print(f"Starting {protocol} server on port {cfg['port']}...")
        p = subprocess.Popen(
            cfg["cmd"],
            cwd=os.getcwd(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ, "PYTHONPATH": "."},
        )
        ServerManager._processes[protocol] = p

    @staticmethod
    def stop(protocol: str):
        if protocol in ServerManager._processes:
            p = ServerManager._processes[protocol]
            print(f"Stopping {protocol} server...")
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()
            del ServerManager._processes[protocol]

        # Fallback: kill anything on that port if it's still stuck
        cfg = SERVER_MAP.get(protocol)
        if cfg and ServerManager.is_port_open(cfg["port"]):
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    for conn in proc.info.get("connections") or []:
                        if conn.laddr.port == cfg["port"]:
                            os.kill(proc.info["pid"], signal.SIGKILL)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

    @staticmethod
    def stop_all():
        keys = list(ServerManager._processes.keys())
        for k in keys:
            ServerManager.stop(k)

    @staticmethod
    def get_stats(protocol: str) -> Optional[dict]:
        """Returns CPU/Memory of the running server"""
        cfg = SERVER_MAP.get(protocol)
        if not cfg:
            return None

        # Check if port is open first
        if not ServerManager.is_port_open(cfg["port"]):
            return None

        # Try to find the process by port if not in _processes
        pid = None
        if protocol in ServerManager._processes:
            pid = ServerManager._processes[protocol].pid
        if not pid:
            # Fallback for macOS: use lsof to find PID by port
            try:
                import subprocess

                output = subprocess.check_output(
                    ["lsof", "-t", f"-i:{cfg['port']}", "-sTCP:LISTEN"],
                    stderr=subprocess.STDOUT,
                )
                pids = output.decode().strip().split("\n")
                if pids and pids[0]:
                    pid = int(pids[0])
            except:
                pass

        if not pid:
            return None

        try:
            proc = psutil.Process(pid)
            mem = proc.memory_info().rss
            cpu = proc.cpu_percent(interval=None)
            for child in proc.children(recursive=True):
                try:
                    mem += child.memory_info().rss
                    cpu += child.cpu_percent(interval=None)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return {"cpu": cpu, "memory_mb": mem / 1024 / 1024}
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
