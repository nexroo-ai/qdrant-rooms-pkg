
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
    if_exists: str = Field("error", description="Action if collection exists: 'error', 'skip', or 'recreate'")


class ActionOutput(OutputBase):
    collection_name: str = Field(..., description="Name of the created collection")
    success: bool = Field(..., description="Whether the collection was created successfully")
    message: str = Field(..., description="Status message")


def create_collection(
    config: CustomAddonConfig,
    collection_name: str,
    vector_size: int,
    distance: str = "Cosine",
    if_exists: str = "error"
) -> ActionResponse:
    logger.debug(f"Creating collection: {collection_name} with vector size: {vector_size}, distance: {distance}, if_exists: {if_exists}")

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

        collection_exists = False
        try:
            collections = client.get_collections().collections
            collection_exists = any(c.name == collection_name for c in collections)
        except Exception as e:
            logger.warning(f"Could not check if collection exists: {e}")

        if collection_exists:
            if if_exists == "skip":
                logger.info(f"Collection '{collection_name}' already exists, skipping creation")
                tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
                output = ActionOutput(
                    collection_name=collection_name,
                    success=True,
                    message=f"Collection '{collection_name}' already exists (skipped)"
                )
                return ActionResponse(
                    output=output,
                    tokens=tokens,
                    message="Collection already exists, skipped creation",
                    code=200
                )
            elif if_exists == "recreate":
                logger.info(f"Collection '{collection_name}' already exists, recreating")
                client.delete_collection(collection_name=collection_name)
                logger.info(f"Deleted existing collection '{collection_name}'")
            elif if_exists == "error":
                logger.error(f"Collection '{collection_name}' already exists")
                tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
                output = ActionOutput(
                    collection_name=collection_name,
                    success=False,
                    message=f"Collection '{collection_name}' already exists"
                )
                return ActionResponse(
                    output=output,
                    tokens=tokens,
                    message=f"Collection '{collection_name}' already exists",
                    code=409
                )
            else:
                logger.warning(f"Unknown if_exists value: {if_exists}, defaulting to 'error'")
                tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
                output = ActionOutput(
                    collection_name=collection_name,
                    success=False,
                    message=f"Collection '{collection_name}' already exists"
                )
                return ActionResponse(
                    output=output,
                    tokens=tokens,
                    message=f"Collection '{collection_name}' already exists",
                    code=409
                )

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance_metric)
        )

        action_taken = "recreated" if (collection_exists and if_exists == "recreate") else "created"
        logger.info(f"Collection '{collection_name}' {action_taken} successfully")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            success=True,
            message=f"Collection '{collection_name}' {action_taken} successfully"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message=f"Collection {action_taken} successfully",
            code=200
        )

    except Exception as e:
        logger.error(f"Failed to create collection: {str(e)}")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name or "unknown",
            success=False,
            message=f"Error: {str(e)}"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message=f"Failed to create collection: {str(e)}",
            code=500
        )
