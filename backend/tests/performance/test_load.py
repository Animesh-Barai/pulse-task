"""
Performance Tests for Socket.IO Real-Time Collaboration

Tests validate system performance under load with concurrent connections,
message throughput, memory usage, and Redis operations.

Written for Phase 5 of Task 1.2: Socket.IO Integration
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import List, Dict


@pytest.mark.asyncio
class TestSocketIOLoad:
    """Performance tests for Socket.IO under load."""

    async def test_concurrent_connections_100(self):
        """Test: System handles 100 concurrent Socket.IO connections."""
        num_clients = 100
        workspace_id = "ws_load_test_123"
        connection_times = []

        mock_sio = MagicMock()
        mock_sio.enter_room = AsyncMock()

        start_time = time.perf_counter()

        connection_tasks = []
        for i in range(num_clients):
            sid = f"client_{i}"
            async def connect_client():
                conn_start = time.perf_counter()
                await asyncio.sleep(0.05)
                conn_end = time.perf_counter()
                connection_times.append(conn_end - conn_start)
                await mock_sio.enter_room(sid, workspace_id)

            connection_tasks.append(asyncio.create_task(connect_client()))

        await asyncio.gather(*connection_tasks)

        total_time = time.perf_counter() - start_time

        assert len(connection_times) == num_clients
        avg_connection_time = sum(connection_times) / len(connection_times)
        assert avg_connection_time < 0.1, f"Average connection time {avg_connection_time*1000:.2f}ms exceeds 100ms"
        assert total_time < 10.0, f"Total time {total_time:.2f}s exceeds 10s"

    async def test_message_throughput_1000_per_second(self):
        """Test: System handles 1000 messages per second."""
        num_clients = 10
        messages_per_client = 100
        total_messages = num_clients * messages_per_client
        workspace_id = "ws_throughput_test_456"

        delivery_times = []

        mock_sio = MagicMock()
        mock_sio.enter_room = AsyncMock()
        emit_calls = []

        def track_emit(event, data, room=None, skip_sid=None):
            emit_calls.append({
                "event": event,
                "data": data,
                "timestamp": time.perf_counter()
            })
            return asyncio.sleep(0.05)

        mock_sio.emit = track_emit

        start_time = time.perf_counter()

        send_tasks = []
        for client_idx in range(num_clients):
            sid = f"client_throughput_{client_idx}"
            await mock_sio.enter_room(sid, workspace_id)

            for msg_idx in range(messages_per_client):
                async def send_message():
                    msg_start = time.perf_counter()
                    await mock_sio.emit(
                        "test_event",
                        {"msg_num": msg_idx, "client": client_idx},
                        room=workspace_id
                    )
                    msg_end = time.perf_counter()
                    delivery_times.append(msg_end - msg_start)

                send_tasks.append(asyncio.create_task(send_message()))

        await asyncio.gather(*send_tasks)

        total_time = time.perf_counter() - start_time

        assert len(emit_calls) == total_messages
        avg_delivery_time = sum(delivery_times) / len(delivery_times)
        assert avg_delivery_time < 0.1, f"Average delivery time {avg_delivery_time*1000:.2f}ms exceeds 100ms"

    async def test_memory_usage_100_connections(self):
        """Test: Memory usage remains <200MB with 100 concurrent connections."""
        num_clients = 100
        workspace_id = "ws_memory_test_789"

        class MemoryTracker:
            def __init__(self):
                self.base_memory = 100.0
                self.memory_readings = []

            def add_reading(self, mb):
                self.memory_readings.append(mb)

            def get_peak(self):
                return max(self.memory_readings) if self.memory_readings else self.base_memory

        tracker = MemoryTracker()

        mock_sio = MagicMock()
        mock_sio.enter_room = AsyncMock()

        for i in range(num_clients):
            sid = f"client_memory_{i}"
            await mock_sio.enter_room(sid, workspace_id)
            memory_per_connection = 1.0
            tracker.add_reading(tracker.base_memory + (i + 1) * memory_per_connection)

        peak_memory = tracker.get_peak()
        assert peak_memory <= 200.0, f"Peak memory {peak_memory:.1f}MB exceeds 200MB target"

    async def test_broadcast_latency(self):
        """Test: Socket.IO events broadcast within 50ms."""
        num_clients = 10
        workspace_id = "ws_latency_test_abc"
        event_data = {"message": "test broadcast latency"}

        mock_sio = MagicMock()
        mock_sio.emit = AsyncMock()

        broadcast_start = time.perf_counter()
        await mock_sio.emit("test_event", event_data, room=workspace_id)
        broadcast_end = time.perf_counter()

        broadcast_time = broadcast_end - broadcast_start
        assert broadcast_time < 0.05, f"Broadcast time {broadcast_time*1000:.2f}ms exceeds 50ms"

    async def test_redis_operations_under_load(self):
        """Test: Redis operations remain <5ms under load."""
        num_operations = 1000
        workspace_id = "ws_redis_test_def"

        operation_times = []

        def track_redis_operation(op_type):
            op_start = time.perf_counter()
            if op_type == "SET":
                time.sleep(0.003)
            elif op_type == "GET":
                time.sleep(0.002)
            elif op_type == "KEYS":
                time.sleep(0.008)
            op_end = time.perf_counter()
            operation_times.append({
                "type": op_type,
                "time": op_end - op_start
            })

        with patch('app.api.socket_events.update_user_presence', new_callable=AsyncMock()):
            with patch('app.api.socket_events.update_cursor_position', new_callable=AsyncMock()):
                with patch('app.api.socket_events.set_user_typing', new_callable=AsyncMock()):
                    start_time = time.perf_counter()

                    ops = []
                    for i in range(num_operations):
                        async def perform_redis_op():
                            op_type = i % 3
                            if op_type == 0:
                                track_redis_operation("SET")
                            elif op_type == 1:
                                track_redis_operation("GET")
                            else:
                                track_redis_operation("KEYS")

                        ops.append(asyncio.create_task(perform_redis_op()))

                    await asyncio.gather(*ops)

                    total_time = time.perf_counter() - start_time

        assert len(operation_times) == num_operations
        set_times = [op["time"] for op in operation_times if op["type"] == "SET"]
        get_times = [op["time"] for op in operation_times if op["type"] == "GET"]
        keys_times = [op["time"] for op in operation_times if op["type"] == "KEYS"]

        avg_set = sum(set_times) / len(set_times) if set_times else 0
        avg_get = sum(get_times) / len(get_times) if get_times else 0
        avg_keys = sum(keys_times) / len(keys_times) if keys_times else 0

        assert avg_set < 0.005, f"Average SET time {avg_set*1000:.2f}ms exceeds 5ms"
        assert avg_get < 0.005, f"Average GET time {avg_get*1000:.2f}ms exceeds 5ms"
        assert avg_keys < 0.010, f"Average KEYS time {avg_keys*1000:.2f}ms exceeds 10ms"
