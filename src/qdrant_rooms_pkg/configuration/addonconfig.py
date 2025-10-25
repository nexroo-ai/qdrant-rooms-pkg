from typing import Optional

from pydantic import Field, model_validator

from .baseconfig import BaseAddonConfig, RequiredSecretsBase


class CustomRequiredSecrets(RequiredSecretsBase):
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key environment variable name (optional for local mode)")


class CustomAddonConfig(BaseAddonConfig):
    url: Optional[str] = Field(None, description="Qdrant server URL (e.g., http://localhost:6333)")
    host: Optional[str] = Field(None, description="Qdrant server host (alternative to url)")
    port: Optional[int] = Field(6333, description="Qdrant server port")
    grpc_port: Optional[int] = Field(6334, description="Qdrant gRPC port")
    prefer_grpc: bool = Field(False, description="Prefer gRPC for communication")
    timeout: int = Field(60, description="Request timeout in seconds")

    @classmethod
    def get_required_secrets(cls) -> CustomRequiredSecrets:
        return CustomRequiredSecrets()

    @model_validator(mode='after')
    def validate_qdrant_secrets(self):
        return self
