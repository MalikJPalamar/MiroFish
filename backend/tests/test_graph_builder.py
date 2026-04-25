"""
Tests for GraphBuilderService - GraphRAG seed extraction.
"""
import pytest
import os
from unittest.mock import patch, MagicMock

from app.services.graph_builder import GraphBuilderService, GraphInfo
from app.services.simulation_manager import (
    SimulationManager,
    SimulationState,
    SimulationStatus,
    PlatformType,
)


class TestGraphInfo:
    """Tests for GraphInfo dataclass."""

    def test_graph_info_to_dict_returns_all_fields(self):
        """GraphInfo.to_dict() returns all required fields."""
        info = GraphInfo(
            graph_id="test_graph_123",
            node_count=42,
            edge_count=17,
            entity_types=["Person", "Organization"],
        )
        result = info.to_dict()

        assert result["graph_id"] == "test_graph_123"
        assert result["node_count"] == 42
        assert result["edge_count"] == 17
        assert result["entity_types"] == ["Person", "Organization"]

    def test_graph_info_to_dict_contains_expected_keys(self):
        """GraphInfo.to_dict() contains exactly the expected keys."""
        info = GraphInfo(
            graph_id="g1",
            node_count=0,
            edge_count=0,
            entity_types=[],
        )
        result = info.to_dict()
        expected_keys = {"graph_id", "node_count", "edge_count", "entity_types"}
        assert set(result.keys()) == expected_keys

    def test_graph_info_empty_entity_types(self):
        """GraphInfo handles empty entity_types list."""
        info = GraphInfo(
            graph_id="empty_test",
            node_count=0,
            edge_count=0,
            entity_types=[],
        )
        result = info.to_dict()
        assert result["entity_types"] == []


class TestSimulationManager:
    """Tests for SimulationManager - simulation lifecycle."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a SimulationManager with temporary storage dir."""
        with patch.object(
            SimulationManager, "SIMULATION_DATA_DIR",
            str(tmp_path / "simulations")
        ):
            mgr = SimulationManager()
            mgr.SIMULATION_DATA_DIR = str(tmp_path / "simulations")
            yield mgr

    def test_create_simulation_returns_simulation_state(self, manager):
        """create_simulation returns a SimulationState with valid fields."""
        state = manager.create_simulation(
            project_id="proj_abc",
            graph_id="graph_xyz",
            enable_twitter=True,
            enable_reddit=False,
        )

        assert isinstance(state, SimulationState)
        assert state.project_id == "proj_abc"
        assert state.graph_id == "graph_xyz"
        assert state.enable_twitter is True
        assert state.enable_reddit is False
        assert state.status == SimulationStatus.CREATED

    def test_create_simulation_generates_unique_id(self, manager):
        """create_simulation generates a unique simulation_id."""
        state1 = manager.create_simulation(project_id="p1", graph_id="g1")
        state2 = manager.create_simulation(project_id="p1", graph_id="g1")

        assert state1.simulation_id != state2.simulation_id
        assert state1.simulation_id.startswith("sim_")
        assert len(state1.simulation_id) == 16  # "sim_" + 12 hex chars

    def test_create_simulation_saves_state_to_disk(self, manager, tmp_path):
        """create_simulation persists state so it survives manager re-creation."""
        state = manager.create_simulation(project_id="persist_test", graph_id="g1")

        # Re-create manager (simulating restart)
        new_mgr = SimulationManager()
        new_mgr.SIMULATION_DATA_DIR = str(tmp_path / "simulations")
        loaded = new_mgr.get_simulation(state.simulation_id)

        assert loaded is not None
        assert loaded.simulation_id == state.simulation_id
        assert loaded.project_id == "persist_test"

    def test_get_simulation_returns_none_for_nonexistent(self, manager):
        """get_simulation returns None when simulation does not exist."""
        result = manager.get_simulation("sim_does_not_exist_12345")
        assert result is None

    def test_list_simulations_returns_empty_when_none_exist(self, manager):
        """list_simulations returns empty list when no simulations exist."""
        result = manager.list_simulations()
        assert result == []

    def test_list_simulations_returns_project_filtered_results(self, manager):
        """list_simulations filters by project_id when provided."""
        manager.create_simulation(project_id="proj_filter_a", graph_id="g1")
        manager.create_simulation(project_id="proj_filter_a", graph_id="g1")
        manager.create_simulation(project_id="proj_filter_b", graph_id="g1")

        results = manager.list_simulations(project_id="proj_filter_a")
        assert len(results) == 2
        assert all(s.project_id == "proj_filter_a" for s in results)


class TestSimulationState:
    """Tests for SimulationState dataclass."""

    def test_simulation_state_to_dict_contains_all_fields(self):
        """to_dict() returns all fields including timestamps."""
        state = SimulationState(
            simulation_id="sim_test_001",
            project_id="proj_1",
            graph_id="graph_1",
        )
        result = state.to_dict()

        assert result["simulation_id"] == "sim_test_001"
        assert result["project_id"] == "proj_1"
        assert result["graph_id"] == "graph_1"
        assert "created_at" in result
        assert "updated_at" in result

    def test_simulation_state_to_simple_dict_excludes_runtime_fields(self):
        """to_simple_dict() excludes runtime fields like current_round."""
        state = SimulationState(
            simulation_id="sim_test_002",
            project_id="proj_1",
            graph_id="graph_1",
            current_round=5,
            twitter_status="running",
            reddit_status="running",
        )
        result = state.to_simple_dict()

        assert "current_round" not in result
        assert "twitter_status" not in result
        assert "reddit_status" not in result
        assert result["simulation_id"] == "sim_test_002"

    def test_simulation_state_default_values(self):
        """SimulationState sets sensible defaults."""
        state = SimulationState(
            simulation_id="sim_defaults",
            project_id="proj_1",
            graph_id="graph_1",
        )

        assert state.enable_twitter is True
        assert state.enable_reddit is True
        assert state.status == SimulationStatus.CREATED
        assert state.entities_count == 0
        assert state.profiles_count == 0
        assert state.config_generated is False
        assert state.error is None


class TestSimulationStatus:
    """Tests for SimulationStatus enum."""

    def test_all_status_values_exist(self):
        """All expected status values are defined."""
        expected = {
            "created", "preparing", "ready", "running",
            "paused", "stopped", "completed", "failed"
        }
        actual = {s.value for s in SimulationStatus}
        assert actual == expected

    def test_status_is_string_enum(self):
        """SimulationStatus values can be used as strings."""
        assert SimulationStatus.CREATED == "created"
        assert SimulationStatus.RUNNING == "running"
        assert SimulationStatus.COMPLETED == "completed"
