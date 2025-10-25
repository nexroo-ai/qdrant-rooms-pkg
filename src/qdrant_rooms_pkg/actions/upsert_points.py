
from loguru import logger
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from qdrant_rooms_pkg.configuration import CustomAddonConfig

from .base import ActionResponse, OutputBase, TokensSchema


class ActionInput(BaseModel):
    collection_name: str = Field(..., description="Name of the collection to insert points into")
    points: list = Field(..., description="List of points with id, vector, and optional payload")


class ActionOutput(OutputBase):
    collection_name: str = Field(..., description="Name of the collection")
    points_count: int = Field(..., description="Number of points upserted")
    success: bool = Field(..., description="Whether the upsert was successful")
    message: str = Field(..., description="Status message")


def upsert_points(
    config: CustomAddonConfig,
    collection_name: str,
    points: list
) -> ActionResponse:
    logger.debug(f"Upserting {len(points)} points to collection: {collection_name}")

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

        point_structs = []
        for point in points:
            point_struct = PointStruct(
                id=point.get("id"),
                vector=point.get("vector"),
                payload=point.get("payload", {})
            )
            point_structs.append(point_struct)

        client.upsert(
            collection_name=collection_name,
            points=point_structs
        )

        logger.info(f"Successfully upserted {len(points)} points to collection '{collection_name}'")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            points_count=len(points),
            success=True,
            message=f"Successfully upserted {len(points)} points"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message="Points upserted successfully",
            code=200
        )

    except Exception as e:
        logger.error(f"Failed to upsert points: {str(e)}")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            points_count=0,
            success=False,
            message=f"Error: {str(e)}"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message=f"Failed to upsert points: {str(e)}",
            code=500
        )
