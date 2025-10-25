import pytest
from pydantic import ValidationError

from qdrant_rooms_pkg.configuration.addonconfig import CustomAddonConfig
from qdrant_rooms_pkg.configuration.baseconfig import BaseAddonConfig


class TestBaseAddonConfig:
    def test_base_config_creation(self):
        config = BaseAddonConfig(
            id="test_addon_id",
            type="test_type",
            name="test_addon",
            description="Test addon description",
            secrets={"key1": "value1"}
        )

        assert config.id == "test_addon_id"
        assert config.type == "test_type"
        assert config.name == "test_addon"
        assert config.description == "Test addon description"
        assert config.secrets == {"key1": "value1"}
        assert config.enabled is True

    def test_base_config_defaults(self):
        config = BaseAddonConfig(
            id="test_id",
            type="test_type",
            name="test",
            description="Test description"
        )

        assert config.enabled is True
        assert config.secrets == {}
        assert config.config == {}


class TestCustomAddonConfig:
    def test_custom_config_creation_with_url(self):
        config = CustomAddonConfig(
            id="test_qdrant_addon_id",
            type="storage",
            name="test_qdrant_addon",
            description="Test Qdrant addon",
            url="http://localhost:6333",
            secrets={}
        )

        assert config.id == "test_qdrant_addon_id"
        assert config.name == "test_qdrant_addon"
        assert config.type == "storage"
        assert config.url == "http://localhost:6333"
        assert config.port == 6333
        assert config.prefer_grpc is False
        assert config.timeout == 60

    def test_custom_config_creation_with_host(self):
        config = CustomAddonConfig(
            id="test_qdrant_addon_id",
            type="storage",
            name="test_qdrant_addon",
            description="Test Qdrant addon",
            host="localhost",
            port=6333,
            secrets={}
        )

        assert config.host == "localhost"
        assert config.port == 6333
        assert config.url is None

    def test_custom_config_with_grpc(self):
        config = CustomAddonConfig(
            id="test_qdrant_addon_id",
            type="storage",
            name="test_qdrant_addon",
            description="Test Qdrant addon",
            host="localhost",
            prefer_grpc=True,
            grpc_port=6334,
            secrets={}
        )

        assert config.prefer_grpc is True
        assert config.grpc_port == 6334

    def test_custom_config_with_api_key(self):
        config = CustomAddonConfig(
            id="test_qdrant_addon_id",
            type="storage",
            name="test_qdrant_addon",
            description="Test Qdrant addon",
            url="https://example.cloud.qdrant.io:6333",
            secrets={"qdrant_api_key": "test_key"}
        )

        assert config.secrets == {"qdrant_api_key": "test_key"}

    def test_custom_config_defaults(self):
        config = CustomAddonConfig(
            id="test_qdrant_addon_id",
            type="storage",
            name="test_qdrant_addon",
            secrets={}
        )

        assert config.port == 6333
        assert config.grpc_port == 6334
        assert config.prefer_grpc is False
        assert config.timeout == 60
