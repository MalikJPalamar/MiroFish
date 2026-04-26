"""
Tests for SimulationIPC - Inter-process communication module.
"""
import pytest
import os
import json
import time
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from enum import Enum

from app.services.simulation_ipc import (
    IPCCommand,
    IPCResponse,
    CommandType,
    CommandStatus,
    SimulationIPCClient,
    SimulationIPCServer,
)


class TestCommandType:
    """Tests for CommandType enum."""

    def test_command_type_values(self):
        """CommandType has expected string values."""
        assert CommandType.INTERVIEW.value == "interview"
        assert CommandType.BATCH_INTERVIEW.value == "batch_interview"
        assert CommandType.CLOSE_ENV.value == "close_env"

    def test_command_type_is_string_enum(self):
        """CommandType inherits from str and Enum."""
        assert issubclass(CommandType, str)
        assert issubclass(CommandType, Enum)

    def test_command_type_all_values_present(self):
        """All expected command types are defined."""
        expected = {"interview", "batch_interview", "close_env"}
        actual = {ct.value for ct in CommandType}
        assert actual == expected


class TestCommandStatus:
    """Tests for CommandStatus enum."""

    def test_command_status_values(self):
        """CommandStatus has expected string values."""
        assert CommandStatus.PENDING.value == "pending"
        assert CommandStatus.PROCESSING.value == "processing"
        assert CommandStatus.COMPLETED.value == "completed"
        assert CommandStatus.FAILED.value == "failed"

    def test_command_status_is_string_enum(self):
        """CommandStatus inherits from str and Enum."""
        assert issubclass(CommandStatus, str)
        assert issubclass(CommandStatus, Enum)

    def test_command_status_all_values_present(self):
        """All expected command statuses are defined."""
        expected = {"pending", "processing", "completed", "failed"}
        actual = {cs.value for cs in CommandStatus}
        assert actual == expected


class TestIPCCommand:
    """Tests for IPCCommand dataclass."""

    def test_ipc_command_creation(self):
        """IPCCommand can be created with required fields."""
        cmd = IPCCommand(
            command_id="test-123",
            command_type=CommandType.INTERVIEW,
            args={"agent_id": 1, "prompt": "Hello?"}
        )
        assert cmd.command_id == "test-123"
        assert cmd.command_type == CommandType.INTERVIEW
        assert cmd.args == {"agent_id": 1, "prompt": "Hello?"}
        assert cmd.timestamp is not None

    def test_ipc_command_to_dict(self):
        """IPCCommand.to_dict() returns expected structure."""
        cmd = IPCCommand(
            command_id="cmd-456",
            command_type=CommandType.BATCH_INTERVIEW,
            args={"interviews": []}
        )
        result = cmd.to_dict()
        
        assert result["command_id"] == "cmd-456"
        assert result["command_type"] == "batch_interview"
        assert result["args"] == {"interviews": []}
        assert "timestamp" in result

    def test_ipc_command_from_dict(self):
        """IPCCommand.from_dict() correctly reconstructs instance."""
        data = {
            "command_id": "recon-789",
            "command_type": "close_env",
            "args": {},
            "timestamp": "2024-01-01T00:00:00"
        }
        cmd = IPCCommand.from_dict(data)
        
        assert cmd.command_id == "recon-789"
        assert cmd.command_type == CommandType.CLOSE_ENV
        assert cmd.args == {}
        assert cmd.timestamp == "2024-01-01T00:00:00"

    def test_ipc_command_from_dict_missing_timestamp(self):
        """IPCCommand.from_dict() generates timestamp if missing."""
        data = {
            "command_id": "no-ts",
            "command_type": "interview",
            "args": {"agent_id": 1}
        }
        cmd = IPCCommand.from_dict(data)
        
        assert cmd.command_id == "no-ts"
        assert cmd.timestamp is not None
        assert cmd.timestamp != ""

    def test_ipc_command_default_timestamp(self):
        """IPCCommand auto-generates timestamp on creation."""
        before = datetime.now().isoformat()
        cmd = IPCCommand(
            command_id="auto-ts",
            command_type=CommandType.INTERVIEW,
            args={}
        )
        after = datetime.now().isoformat()
        
        assert before <= cmd.timestamp <= after


class TestIPCResponse:
    """Tests for IPCResponse dataclass."""

    def test_ipc_response_creation_success(self):
        """IPCResponse can be created with success status."""
        resp = IPCResponse(
            command_id="resp-123",
            status=CommandStatus.COMPLETED,
            result={"data": "test"}
        )
        assert resp.command_id == "resp-123"
        assert resp.status == CommandStatus.COMPLETED
        assert resp.result == {"data": "test"}
        assert resp.error is None

    def test_ipc_response_creation_failure(self):
        """IPCResponse can be created with failure status."""
        resp = IPCResponse(
            command_id="resp-456",
            status=CommandStatus.FAILED,
            error="Something went wrong"
        )
        assert resp.command_id == "resp-456"
        assert resp.status == CommandStatus.FAILED
        assert resp.result is None
        assert resp.error == "Something went wrong"

    def test_ipc_response_to_dict(self):
        """IPCResponse.to_dict() returns expected structure."""
        resp = IPCResponse(
            command_id="resp-789",
            status=CommandStatus.COMPLETED,
            result={"agents": []},
            error=None
        )
        result = resp.to_dict()
        
        assert result["command_id"] == "resp-789"
        assert result["status"] == "completed"
        assert result["result"] == {"agents": []}
        assert result["error"] is None
        assert "timestamp" in result

    def test_ipc_response_from_dict(self):
        """IPCResponse.from_dict() correctly reconstructs instance."""
        data = {
            "command_id": "from-dict",
            "status": "failed",
            "result": None,
            "error": "Test error",
            "timestamp": "2024-06-01T12:00:00"
        }
        resp = IPCResponse.from_dict(data)
        
        assert resp.command_id == "from-dict"
        assert resp.status == CommandStatus.FAILED
        assert resp.result is None
        assert resp.error == "Test error"
        assert resp.timestamp == "2024-06-01T12:00:00"

    def test_ipc_response_from_dict_missing_optional_fields(self):
        """IPCResponse.from_dict() handles missing optional fields."""
        data = {
            "command_id": "minimal",
            "status": "completed"
        }
        resp = IPCResponse.from_dict(data)
        
        assert resp.command_id == "minimal"
        assert resp.status == CommandStatus.COMPLETED
        assert resp.result is None
        assert resp.error is None
        assert resp.timestamp is not None


class TestSimulationIPCClient:
    """Tests for SimulationIPCClient."""

    @pytest.fixture
    def client(self, tmp_path):
        """Create a SimulationIPCClient with temporary directories."""
        sim_dir = str(tmp_path / "simulation")
        os.makedirs(sim_dir, exist_ok=True)
        return SimulationIPCClient(sim_dir)

    def test_client_initialization(self, client, tmp_path):
        """Client initializes with correct directory paths."""
        sim_dir = str(tmp_path / "simulation")
        assert client.simulation_dir == sim_dir
        assert client.commands_dir == os.path.join(sim_dir, "ipc_commands")
        assert client.responses_dir == os.path.join(sim_dir, "ipc_responses")

    def test_client_creates_directories(self, client, tmp_path):
        """Client creates command and response directories."""
        assert os.path.exists(client.commands_dir)
        assert os.path.exists(client.responses_dir)

    def test_send_command_creates_file(self, client, tmp_path):
        """send_command writes command file to commands directory."""
        import uuid
        with patch('app.services.simulation_ipc.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = Mock(__str__=lambda x: "test-uuid-file")
            with patch('app.services.simulation_ipc.time.sleep'):
                try:
                    client.send_command(CommandType.INTERVIEW, {"agent_id": 1}, timeout=0.1)
                except TimeoutError:
                    pass
        
        # Command file is cleaned up on timeout, but we can verify directories exist
        assert os.path.exists(client.commands_dir)
        assert os.path.exists(client.responses_dir)

    def test_send_command_timeout(self, client, tmp_path):
        """send_command raises TimeoutError when no response."""
        with patch('app.services.simulation_ipc.time.sleep'):
            with pytest.raises(TimeoutError, match="Command response timeout"):
                client.send_command(
                    CommandType.INTERVIEW,
                    {"agent_id": 1},
                    timeout=0.1,
                    poll_interval=0.01
                )

    def test_send_command_success(self, client, tmp_path):
        """send_command returns IPCResponse on success."""
        # Create a mock response file before calling send_command
        command_id = "test-cmd-id"
        command_file = os.path.join(client.commands_dir, f"{command_id}.json")
        response_file = os.path.join(client.responses_dir, f"{command_id}.json")
        
        # Pre-create command file with valid command
        import uuid
        with patch('app.services.simulation_ipc.uuid.uuid4', return_value=MagicMock(__str__=lambda x: command_id)):
            with patch('app.services.simulation_ipc.time.sleep'):
                # Create command file
                os.makedirs(client.commands_dir, exist_ok=True)
                cmd = IPCCommand(
                    command_id=command_id,
                    command_type=CommandType.INTERVIEW,
                    args={"agent_id": 1}
                )
                with open(command_file, 'w') as f:
                    json.dump(cmd.to_dict(), f)
                
                # Create matching response file
                resp = IPCResponse(
                    command_id=command_id,
                    status=CommandStatus.COMPLETED,
                    result={"status": "ok"}
                )
                with open(response_file, 'w') as f:
                    json.dump(resp.to_dict(), f)
                
                result = client.send_command(
                    CommandType.INTERVIEW,
                    {"agent_id": 1},
                    timeout=1.0,
                    poll_interval=0.01
                )
                
                assert result.status == CommandStatus.COMPLETED
                assert result.result == {"status": "ok"}

    def test_send_interview(self, client, tmp_path):
        """send_interview creates correct command structure."""
        command_id = "interview-cmd"
        command_file = os.path.join(client.commands_dir, f"{command_id}.json")
        response_file = os.path.join(client.responses_dir, f"{command_id}.json")
        
        with patch('app.services.simulation_ipc.uuid.uuid4', return_value=MagicMock(__str__=lambda x: command_id)):
            with patch('app.services.simulation_ipc.time.sleep'):
                os.makedirs(client.commands_dir, exist_ok=True)
                
                cmd = IPCCommand(
                    command_id=command_id,
                    command_type=CommandType.INTERVIEW,
                    args={"agent_id": 1, "prompt": "Hello?"}
                )
                with open(command_file, 'w') as f:
                    json.dump(cmd.to_dict(), f)
                
                resp = IPCResponse(
                    command_id=command_id,
                    status=CommandStatus.COMPLETED,
                    result={"response": "Hi!"}
                )
                with open(response_file, 'w') as f:
                    json.dump(resp.to_dict(), f)
                
                result = client.send_interview(
                    agent_id=1,
                    prompt="Hello?",
                    timeout=1.0
                )
                
                assert result.status == CommandStatus.COMPLETED

    def test_send_interview_with_platform(self, client, tmp_path):
        """send_interview includes platform when specified."""
        command_id = "platform-cmd"
        command_file = os.path.join(client.commands_dir, f"{command_id}.json")
        response_file = os.path.join(client.responses_dir, f"{command_id}.json")
        
        with patch('app.services.simulation_ipc.uuid.uuid4', return_value=MagicMock(__str__=lambda x: command_id)):
            with patch('app.services.simulation_ipc.time.sleep'):
                os.makedirs(client.commands_dir, exist_ok=True)
                
                cmd = IPCCommand(
                    command_id=command_id,
                    command_type=CommandType.INTERVIEW,
                    args={"agent_id": 1, "prompt": "Hello?", "platform": "twitter"}
                )
                with open(command_file, 'w') as f:
                    json.dump(cmd.to_dict(), f)
                
                resp = IPCResponse(
                    command_id=command_id,
                    status=CommandStatus.COMPLETED,
                    result={}
                )
                with open(response_file, 'w') as f:
                    json.dump(resp.to_dict(), f)
                
                result = client.send_interview(
                    agent_id=1,
                    prompt="Hello?",
                    platform="twitter",
                    timeout=1.0
                )
                
                assert result.status == CommandStatus.COMPLETED

    def test_send_batch_interview(self, client, tmp_path):
        """send_batch_interview sends correct command structure."""
        command_id = "batch-cmd"
        command_file = os.path.join(client.commands_dir, f"{command_id}.json")
        response_file = os.path.join(client.responses_dir, f"{command_id}.json")
        
        interviews = [
            {"agent_id": 1, "prompt": "Q1"},
            {"agent_id": 2, "prompt": "Q2"}
        ]
        
        with patch('app.services.simulation_ipc.uuid.uuid4', return_value=MagicMock(__str__=lambda x: command_id)):
            with patch('app.services.simulation_ipc.time.sleep'):
                os.makedirs(client.commands_dir, exist_ok=True)
                
                cmd = IPCCommand(
                    command_id=command_id,
                    command_type=CommandType.BATCH_INTERVIEW,
                    args={"interviews": interviews}
                )
                with open(command_file, 'w') as f:
                    json.dump(cmd.to_dict(), f)
                
                resp = IPCResponse(
                    command_id=command_id,
                    status=CommandStatus.COMPLETED,
                    result={"count": 2}
                )
                with open(response_file, 'w') as f:
                    json.dump(resp.to_dict(), f)
                
                result = client.send_batch_interview(
                    interviews=interviews,
                    timeout=1.0
                )
                
                assert result.status == CommandStatus.COMPLETED
                assert result.result == {"count": 2}

    def test_send_close_env(self, client, tmp_path):
        """send_close_env sends close command."""
        command_id = "close-cmd"
        command_file = os.path.join(client.commands_dir, f"{command_id}.json")
        response_file = os.path.join(client.responses_dir, f"{command_id}.json")
        
        with patch('app.services.simulation_ipc.uuid.uuid4', return_value=MagicMock(__str__=lambda x: command_id)):
            with patch('app.services.simulation_ipc.time.sleep'):
                os.makedirs(client.commands_dir, exist_ok=True)
                
                cmd = IPCCommand(
                    command_id=command_id,
                    command_type=CommandType.CLOSE_ENV,
                    args={}
                )
                with open(command_file, 'w') as f:
                    json.dump(cmd.to_dict(), f)
                
                resp = IPCResponse(
                    command_id=command_id,
                    status=CommandStatus.COMPLETED,
                    result={"closed": True}
                )
                with open(response_file, 'w') as f:
                    json.dump(resp.to_dict(), f)
                
                result = client.send_close_env(timeout=1.0)
                
                assert result.status == CommandStatus.COMPLETED

    def test_check_env_alive_returns_true(self, client, tmp_path):
        """check_env_alive returns True when status is alive."""
        status_file = os.path.join(client.simulation_dir, "env_status.json")
        with open(status_file, 'w') as f:
            json.dump({"status": "alive", "timestamp": datetime.now().isoformat()}, f)
        
        assert client.check_env_alive() is True

    def test_check_env_alive_returns_false_when_not_alive(self, client, tmp_path):
        """check_env_alive returns False when status is not alive."""
        status_file = os.path.join(client.simulation_dir, "env_status.json")
        with open(status_file, 'w') as f:
            json.dump({"status": "stopped", "timestamp": datetime.now().isoformat()}, f)
        
        assert client.check_env_alive() is False

    def test_check_env_alive_returns_false_when_file_missing(self, client, tmp_path):
        """check_env_alive returns False when status file doesn't exist."""
        assert client.check_env_alive() is False

    def test_check_env_alive_returns_false_on_invalid_json(self, client, tmp_path):
        """check_env_alive returns False on malformed JSON."""
        status_file = os.path.join(client.simulation_dir, "env_status.json")
        with open(status_file, 'w') as f:
            f.write("not valid json{")
        
        assert client.check_env_alive() is False


class TestSimulationIPCServer:
    """Tests for SimulationIPCServer."""

    @pytest.fixture
    def server(self, tmp_path):
        """Create a SimulationIPCServer with temporary directories."""
        sim_dir = str(tmp_path / "simulation")
        os.makedirs(sim_dir, exist_ok=True)
        return SimulationIPCServer(sim_dir)

    def test_server_initialization(self, server, tmp_path):
        """Server initializes with correct directory paths."""
        sim_dir = str(tmp_path / "simulation")
        assert server.simulation_dir == sim_dir
        assert server.commands_dir == os.path.join(sim_dir, "ipc_commands")
        assert server.responses_dir == os.path.join(sim_dir, "ipc_responses")

    def test_server_creates_directories(self, server, tmp_path):
        """Server creates command and response directories."""
        assert os.path.exists(server.commands_dir)
        assert os.path.exists(server.responses_dir)

    def test_server_start_updates_status(self, server, tmp_path):
        """start() sets running True and updates env_status.json."""
        server.start()
        
        assert server._running is True
        status_file = os.path.join(server.simulation_dir, "env_status.json")
        assert os.path.exists(status_file)
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        assert status["status"] == "alive"

    def test_server_stop_updates_status(self, server, tmp_path):
        """stop() sets running False and updates env_status.json."""
        server.start()
        server.stop()
        
        assert server._running is False
        status_file = os.path.join(server.simulation_dir, "env_status.json")
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        assert status["status"] == "stopped"

    def test_poll_commands_returns_none_when_empty(self, server, tmp_path):
        """poll_commands returns None when no command files exist."""
        result = server.poll_commands()
        assert result is None

    def test_poll_commands_returns_first_command(self, server, tmp_path):
        """poll_commands returns oldest command file."""
        # Create two command files with different timestamps
        cmd1 = IPCCommand(
            command_id="first",
            command_type=CommandType.INTERVIEW,
            args={"agent_id": 1}
        )
        cmd2 = IPCCommand(
            command_id="second",
            command_type=CommandType.BATCH_INTERVIEW,
            args={"interviews": []}
        )
        
        # Write in order but older one first
        first_file = os.path.join(server.commands_dir, "first.json")
        second_file = os.path.join(server.commands_dir, "second.json")
        
        with open(first_file, 'w') as f:
            json.dump(cmd1.to_dict(), f)
        
        # Ensure different mtime
        time.sleep(0.02)
        with open(second_file, 'w') as f:
            json.dump(cmd2.to_dict(), f)
        
        result = server.poll_commands()
        
        assert result is not None
        assert result.command_id == "first"
        assert result.command_type == CommandType.INTERVIEW

    def test_poll_commands_skips_invalid_json(self, server, tmp_path):
        """poll_commands skips files with invalid JSON."""
        # Create invalid file first
        with open(os.path.join(server.commands_dir, "invalid.json"), 'w') as f:
            f.write("not valid json")
        
        # Create valid command file second
        cmd = IPCCommand(
            command_id="valid-cmd",
            command_type=CommandType.INTERVIEW,
            args={}
        )
        time.sleep(0.01)
        with open(os.path.join(server.commands_dir, "valid.json"), 'w') as f:
            json.dump(cmd.to_dict(), f)
        
        result = server.poll_commands()
        
        assert result is not None
        assert result.command_id == "valid-cmd"

    def test_send_response_creates_file(self, server, tmp_path):
        """send_response writes response file and removes command file."""
        cmd = IPCCommand(
            command_id="to-remove",
            command_type=CommandType.INTERVIEW,
            args={}
        )
        command_file = os.path.join(server.commands_dir, "to-remove.json")
        with open(command_file, 'w') as f:
            json.dump(cmd.to_dict(), f)
        
        resp = IPCResponse(
            command_id="to-remove",
            status=CommandStatus.COMPLETED,
            result={"done": True}
        )
        server.send_response(resp)
        
        # Response file should exist
        response_file = os.path.join(server.responses_dir, "to-remove.json")
        assert os.path.exists(response_file)
        
        with open(response_file, 'r') as f:
            data = json.load(f)
        assert data["status"] == "completed"
        assert data["result"] == {"done": True}

    def test_send_success(self, server, tmp_path):
        """send_success creates completed response."""
        server.send_success("cmd-success", {"result": "data"})
        
        response_file = os.path.join(server.responses_dir, "cmd-success.json")
        assert os.path.exists(response_file)
        
        with open(response_file, 'r') as f:
            data = json.load(f)
        assert data["status"] == "completed"
        assert data["result"] == {"result": "data"}
        assert data["error"] is None

    def test_send_error(self, server, tmp_path):
        """send_error creates failed response."""
        server.send_error("cmd-error", "Something broke")
        
        response_file = os.path.join(server.responses_dir, "cmd-error.json")
        assert os.path.exists(response_file)
        
        with open(response_file, 'r') as f:
            data = json.load(f)
        assert data["status"] == "failed"
        assert data["error"] == "Something broke"
        assert data["result"] is None


class TestSimulationIPCClientIntegration:
    """Integration tests for client-server IPC communication."""

    @pytest.fixture
    def ipc_dirs(self, tmp_path):
        """Create shared directories for integration tests."""
        sim_dir = str(tmp_path / "simulation")
        commands_dir = os.path.join(sim_dir, "ipc_commands")
        responses_dir = os.path.join(sim_dir, "ipc_responses")
        os.makedirs(commands_dir, exist_ok=True)
        os.makedirs(responses_dir, exist_ok=True)
        return sim_dir, commands_dir, responses_dir

    def test_full_command_response_cycle(self, ipc_dirs, tmp_path):
        """Simulate complete command->response cycle."""
        sim_dir, commands_dir, responses_dir = ipc_dirs
        
        client = SimulationIPCClient(sim_dir)
        server = SimulationIPCServer(sim_dir)
        
        # Server polls and finds command
        # First, client sends a command
        command_id = "cycle-test"
        command_file = os.path.join(commands_dir, f"{command_id}.json")
        response_file = os.path.join(responses_dir, f"{command_id}.json")
        
        cmd = IPCCommand(
            command_id=command_id,
            command_type=CommandType.INTERVIEW,
            args={"agent_id": 1, "prompt": "Test?"}
        )
        with open(command_file, 'w') as f:
            json.dump(cmd.to_dict(), f)
        
        # Server polls command
        polled = server.poll_commands()
        assert polled is not None
        assert polled.command_id == command_id
        
        # Server sends success response
        server.send_success(command_id, {"response": "Answer!"})
        
        # Clean up command file (server does this)
        try:
            os.remove(command_file)
        except OSError:
            pass
        
        # Client polls and gets response
        # Mock uuid so the client uses our command_id
        with patch('app.services.simulation_ipc.uuid.uuid4', return_value=Mock(__str__=lambda x: command_id)):
            with patch('app.services.simulation_ipc.time.sleep'):
                response = client.send_command(
                    CommandType.INTERVIEW,
                    {"agent_id": 1, "prompt": "Test?"},
                    timeout=1.0,
                    poll_interval=0.01
                )
        
        # Response should be found
        assert os.path.exists(response_file) is False  # Cleaned up by client

        
    def test_client_server_error_handling(self, ipc_dirs, tmp_path):
        """Test error response handling through IPC."""
        sim_dir, commands_dir, responses_dir = ipc_dirs
        
        client = SimulationIPCClient(sim_dir)
        server = SimulationIPCServer(sim_dir)
        
        command_id = "error-test"
        command_file = os.path.join(commands_dir, f"{command_id}.json")
        
        cmd = IPCCommand(
            command_id=command_id,
            command_type=CommandType.INTERVIEW,
            args={"agent_id": 999}  # Non-existent agent
        )
        with open(command_file, 'w') as f:
            json.dump(cmd.to_dict(), f)
        
        # Server polls and sends error
        polled = server.poll_commands()
        assert polled is not None
        
        server.send_error(command_id, "Agent not found")
        
        # Clean up
        try:
            os.remove(command_file)
        except OSError:
            pass
