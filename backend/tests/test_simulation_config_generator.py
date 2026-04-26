"""
Tests for SimulationConfigGenerator - config generation dataclasses and utilities.
"""
import pytest
import json
from datetime import datetime

from app.services.simulation_config_generator import (
    SimulationConfigGenerator,
    SimulationParameters,
    AgentActivityConfig,
    TimeSimulationConfig,
    EventConfig,
    PlatformConfig,
    CHINA_TIMEZONE_CONFIG,
)


class TestAgentActivityConfig:
    """Tests for AgentActivityConfig dataclass."""

    def test_agent_activity_config_default_values(self):
        """AgentActivityConfig has sensible defaults for all fields."""
        config = AgentActivityConfig(
            agent_id=1,
            entity_uuid="test-uuid-123",
            entity_name="TestAgent",
            entity_type="Person",
        )

        assert config.agent_id == 1
        assert config.entity_uuid == "test-uuid-123"
        assert config.entity_name == "TestAgent"
        assert config.entity_type == "Person"
        assert config.activity_level == 0.5
        assert config.posts_per_hour == 1.0
        assert config.comments_per_hour == 2.0
        assert config.active_hours == list(range(8, 23))
        assert config.response_delay_min == 5
        assert config.response_delay_max == 60
        assert config.sentiment_bias == 0.0
        assert config.stance == "neutral"
        assert config.influence_weight == 1.0

    def test_agent_activity_config_custom_values(self):
        """AgentActivityConfig accepts custom values for all fields."""
        config = AgentActivityConfig(
            agent_id=42,
            entity_uuid="custom-uuid",
            entity_name="CustomAgent",
            entity_type="Organization",
            activity_level=0.8,
            posts_per_hour=5.0,
            comments_per_hour=10.0,
            active_hours=[9, 10, 11, 14, 15, 19, 20],
            response_delay_min=1,
            response_delay_max=30,
            sentiment_bias=0.7,
            stance="supportive",
            influence_weight=2.5,
        )

        assert config.activity_level == 0.8
        assert config.posts_per_hour == 5.0
        assert config.comments_per_hour == 10.0
        assert config.active_hours == [9, 10, 11, 14, 15, 19, 20]
        assert config.response_delay_min == 1
        assert config.response_delay_max == 30
        assert config.sentiment_bias == 0.7
        assert config.stance == "supportive"
        assert config.influence_weight == 2.5


class TestTimeSimulationConfig:
    """Tests for TimeSimulationConfig dataclass."""

    def test_time_simulation_config_default_values(self):
        """TimeSimulationConfig has sensible defaults."""
        config = TimeSimulationConfig()

        assert config.total_simulation_hours == 72
        assert config.minutes_per_round == 60
        assert config.agents_per_hour_min == 5
        assert config.agents_per_hour_max == 20
        assert config.peak_hours == [19, 20, 21, 22]
        assert config.peak_activity_multiplier == 1.5
        assert config.off_peak_hours == [0, 1, 2, 3, 4, 5]
        assert config.off_peak_activity_multiplier == 0.05
        assert config.morning_hours == [6, 7, 8]
        assert config.morning_activity_multiplier == 0.4
        assert config.work_hours == [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        assert config.work_activity_multiplier == 0.7

    def test_time_simulation_config_custom_hours(self):
        """TimeSimulationConfig accepts custom hour ranges."""
        config = TimeSimulationConfig(
            total_simulation_hours=24,
            minutes_per_round=30,
            peak_hours=[18, 19, 20, 21, 22, 23],
            peak_activity_multiplier=2.0,
        )

        assert config.total_simulation_hours == 24
        assert config.minutes_per_round == 30
        assert config.peak_hours == [18, 19, 20, 21, 22, 23]
        assert config.peak_activity_multiplier == 2.0


class TestEventConfig:
    """Tests for EventConfig dataclass."""

    def test_event_config_default_values(self):
        """EventConfig has empty defaults."""
        config = EventConfig()

        assert config.initial_posts == []
        assert config.scheduled_events == []
        assert config.hot_topics == []
        assert config.narrative_direction == ""

    def test_event_config_with_events(self):
        """EventConfig accepts event data."""
        config = EventConfig(
            initial_posts=[{"content": "Breaking news", "agent_id": 1}],
            scheduled_events=[{"time": "12:00", "content": "Lunch topic"}],
            hot_topics=["AI", "Machine Learning"],
            narrative_direction="positive",
        )

        assert len(config.initial_posts) == 1
        assert config.hot_topics == ["AI", "Machine Learning"]
        assert config.narrative_direction == "positive"


class TestPlatformConfig:
    """Tests for PlatformConfig dataclass."""

    def test_platform_config_default_values(self):
        """PlatformConfig has sensible defaults."""
        config = PlatformConfig(platform="twitter")

        assert config.platform == "twitter"
        assert config.recency_weight == 0.4
        assert config.popularity_weight == 0.3
        assert config.relevance_weight == 0.3
        assert config.viral_threshold == 10
        assert config.echo_chamber_strength == 0.5

    def test_platform_config_reddit(self):
        """PlatformConfig works for reddit platform."""
        config = PlatformConfig(
            platform="reddit",
            recency_weight=0.5,
            popularity_weight=0.4,
            relevance_weight=0.1,
            viral_threshold=20,
            echo_chamber_strength=0.7,
        )

        assert config.platform == "reddit"
        assert config.recency_weight == 0.5
        assert config.viral_threshold == 20


class TestSimulationParameters:
    """Tests for SimulationParameters dataclass."""

    def test_simulation_parameters_to_dict(self):
        """SimulationParameters.to_dict() returns all fields."""
        params = SimulationParameters(
            simulation_id="sim_test_001",
            project_id="proj_1",
            graph_id="graph_1",
            simulation_requirement="Test simulation",
        )

        result = params.to_dict()

        assert result["simulation_id"] == "sim_test_001"
        assert result["project_id"] == "proj_1"
        assert result["graph_id"] == "graph_1"
        assert result["simulation_requirement"] == "Test simulation"
        assert "time_config" in result
        assert "agent_configs" in result
        assert "event_config" in result
        assert "twitter_config" in result
        assert "reddit_config" in result
        assert "llm_model" in result
        assert "llm_base_url" in result
        assert "generated_at" in result
        assert "generation_reasoning" in result

    def test_simulation_parameters_to_dict_includes_agent_configs(self):
        """SimulationParameters.to_dict() includes agent_configs as list."""
        params = SimulationParameters(
            simulation_id="sim_with_agents",
            project_id="proj_1",
            graph_id="graph_1",
            simulation_requirement="Test with agents",
        )
        params.agent_configs = [
            AgentActivityConfig(
                agent_id=1,
                entity_uuid="uuid1",
                entity_name="Agent1",
                entity_type="Person",
            ),
            AgentActivityConfig(
                agent_id=2,
                entity_uuid="uuid2",
                entity_name="Agent2",
                entity_type="Person",
            ),
        ]

        result = params.to_dict()

        assert len(result["agent_configs"]) == 2
        assert result["agent_configs"][0]["entity_name"] == "Agent1"
        assert result["agent_configs"][1]["entity_name"] == "Agent2"

    def test_simulation_parameters_to_dict_with_platform_config(self):
        """SimulationParameters.to_dict() handles platform configs."""
        params = SimulationParameters(
            simulation_id="sim_platform",
            project_id="proj_1",
            graph_id="graph_1",
            simulation_requirement="Platform test",
        )
        params.twitter_config = PlatformConfig(platform="twitter")
        params.reddit_config = PlatformConfig(platform="reddit")

        result = params.to_dict()

        assert result["twitter_config"] is not None
        assert result["twitter_config"]["platform"] == "twitter"
        assert result["reddit_config"] is not None
        assert result["reddit_config"]["platform"] == "reddit"

    def test_simulation_parameters_to_dict_with_none_platform(self):
        """SimulationParameters.to_dict() handles None platform configs."""
        params = SimulationParameters(
            simulation_id="sim_no_twitter",
            project_id="proj_1",
            graph_id="graph_1",
            simulation_requirement="No platform test",
        )
        params.twitter_config = None
        params.reddit_config = None

        result = params.to_dict()

        assert result["twitter_config"] is None
        assert result["reddit_config"] is None

    def test_simulation_parameters_to_json(self):
        """SimulationParameters.to_json() returns valid JSON string."""
        params = SimulationParameters(
            simulation_id="sim_json_001",
            project_id="proj_1",
            graph_id="graph_1",
            simulation_requirement="Test",
        )

        json_str = params.to_json()
        parsed = json.loads(json_str)

        assert parsed["simulation_id"] == "sim_json_001"
        assert parsed["project_id"] == "proj_1"

    def test_simulation_parameters_generated_at_is_iso_format(self):
        """SimulationParameters.generated_at is in ISO format."""
        params = SimulationParameters(
            simulation_id="sim_time",
            project_id="proj_1",
            graph_id="graph_1",
            simulation_requirement="Time test",
        )

        # Should not raise - verifies it's a valid ISO timestamp
        datetime.fromisoformat(params.generated_at)


class TestChinaTimezoneConfig:
    """Tests for CHINA_TIMEZONE_CONFIG constant."""

    def test_china_timezone_has_all_periods(self):
        """CHINA_TIMEZONE_CONFIG defines all expected time periods."""
        assert "dead_hours" in CHINA_TIMEZONE_CONFIG
        assert "morning_hours" in CHINA_TIMEZONE_CONFIG
        assert "work_hours" in CHINA_TIMEZONE_CONFIG
        assert "peak_hours" in CHINA_TIMEZONE_CONFIG
        assert "night_hours" in CHINA_TIMEZONE_CONFIG
        assert "activity_multipliers" in CHINA_TIMEZONE_CONFIG

    def test_china_timezone_activity_multipliers(self):
        """CHINA_TIMEZONE_CONFIG.activity_multipliers has expected keys."""
        multipliers = CHINA_TIMEZONE_CONFIG["activity_multipliers"]

        assert "dead" in multipliers
        assert "morning" in multipliers
        assert "work" in multipliers
        assert "peak" in multipliers
        assert "night" in multipliers

    def test_china_timezone_dead_hours(self):
        """dead_hours covers nighttime hours (0-5)."""
        assert CHINA_TIMEZONE_CONFIG["dead_hours"] == [0, 1, 2, 3, 4, 5]

    def test_china_timezone_peak_hours(self):
        """peak_hours covers evening hours (19-22)."""
        assert CHINA_TIMEZONE_CONFIG["peak_hours"] == [19, 20, 21, 22]


class TestSimulationConfigGenerator:
    """Tests for SimulationConfigGenerator class constants and init."""

    def test_generator_class_constants(self):
        """SimulationConfigGenerator has expected class constants."""
        assert SimulationConfigGenerator.MAX_CONTEXT_LENGTH == 50000
        assert SimulationConfigGenerator.AGENTS_PER_BATCH == 15
        assert SimulationConfigGenerator.TIME_CONFIG_CONTEXT_LENGTH == 10000
        assert SimulationConfigGenerator.EVENT_CONFIG_CONTEXT_LENGTH == 8000
        assert SimulationConfigGenerator.ENTITY_SUMMARY_LENGTH == 300
        assert SimulationConfigGenerator.AGENT_SUMMARY_LENGTH == 300
        assert SimulationConfigGenerator.ENTITIES_PER_TYPE_DISPLAY == 20

    def test_generator_init_raises_without_api_key(self, monkeypatch):
        """SimulationConfigGenerator.__init__ raises ValueError when no API key is configured."""
        # Mock Config to have empty LLM_API_KEY so the fallback also fails
        monkeypatch.setattr("app.services.simulation_config_generator.Config.LLM_API_KEY", "")

        with pytest.raises(ValueError, match="LLM_API_KEY"):
            SimulationConfigGenerator(api_key=None, base_url="http://test")
