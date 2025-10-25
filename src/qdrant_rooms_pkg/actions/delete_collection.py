from loguru import logger
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from qdrant_rooms_pkg.configuration import CustomAddonConfig

from .base import ActionResponse, OutputBase, TokensSchema


class ActionInput(BaseModel):
    collection_name: str = Field(..., description="Name of the collection to delete")


class ActionOutput(OutputBase):
    collection_name: str = Field(..., description="Name of the deleted collection")
    success: bool = Field(..., description="Whether the collection was deleted successfully")
    message: str = Field(..., description="Status message")


def delete_collection(
    config: CustomAddonConfig,
    collection_name: str
) -> ActionResponse:
    logger.debug(f"Deleting collection: {collection_name}")

    try:
        client_params = {}

        if config.url:
            client_params["url"] = config.url
        elif config.host:
            client_params["host"] = config.host
            client_params["port"] = config.port

        if config.prefer_grpc and config.grpc_port:
            client_params["grpc_port"] = config.grpc_port
            client_params["prefer_grpc"] = True

        if "qdrant_api_key" in config.secrets and config.secrets["qdrant_api_key"]:
            client_params["api_key"] = config.secrets["qdrant_api_key"]

        client_params["timeout"] = config.timeout

        client = QdrantClient(**client_params)

        client.delete_collection(collection_name=collection_name)

        logger.info(f"Collection '{collection_name}' deleted successfully")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            success=True,
            message=f"Collection '{collection_name}' deleted successfully"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message="Collection deleted successfully",
            code=200
        )

    except Exception as e:
        logger.error(f"Failed to delete collection: {str(e)}")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            success=False,
            message=f"Error: {str(e)}"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message=f"Failed to delete collection: {str(e)}",
            code=500
        )
