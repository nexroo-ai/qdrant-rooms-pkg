from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from qdrant_rooms_pkg.configuration import CustomAddonConfig

from .base import ActionResponse, OutputBase, TokensSchema


class ActionInput(BaseModel):
    collection_name: str = Field(..., description="Name of the collection to create")
    vector_size: int = Field(..., description="Size of the vectors to store")
    distance: str = Field("Cosine", description="Distance metric: Cosine, Euclid, or Dot")


class ActionOutput(OutputBase):
    collection_name: str = Field(..., description="Name of the created collection")
    success: bool = Field(..., description="Whether the collection was created successfully")
    message: str = Field(..., description="Status message")


def create_collection(
    config: CustomAddonConfig,
    collection_name: str,
    vector_size: int,
    distance: str = "Cosine"
) -> ActionResponse:
    logger.debug(f"Creating collection: {collection_name} with vector size: {vector_size}, distance: {distance}")

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

        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclid": Distance.EUCLID,
            "Dot": Distance.DOT,
        }

        distance_metric = distance_map.get(distance, Distance.COSINE)

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance_metric)
        )

        logger.info(f"Collection '{collection_name}' created successfully")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            success=True,
            message=f"Collection '{collection_name}' created successfully"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message="Collection created successfully",
            code=200
        )

    except Exception as e:
        logger.error(f"Failed to create collection: {str(e)}")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            success=False,
            message=f"Error: {str(e)}"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message=f"Failed to create collection: {str(e)}",
            code=500
        )
