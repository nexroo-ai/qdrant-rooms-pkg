from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from qdrant_rooms_pkg.configuration import CustomAddonConfig

from .base import ActionResponse, OutputBase, TokensSchema


class ActionInput(BaseModel):
    collection_name: str = Field(..., description="Name of the collection to search in")
    query_vector: list = Field(..., description="Query vector to search for similar points")
    limit: int = Field(5, description="Maximum number of results to return")
    score_threshold: Optional[float] = Field(None, description="Minimum score threshold for results")


class ActionOutput(OutputBase):
    collection_name: str = Field(..., description="Name of the collection searched")
    results: list = Field(..., description="List of search results with id, score, and payload")
    results_count: int = Field(..., description="Number of results returned")
    success: bool = Field(..., description="Whether the search was successful")
    message: str = Field(..., description="Status message")


def search_points(
    config: CustomAddonConfig,
    collection_name: str,
    query_vector: list,
    limit: int = 5,
    score_threshold: float = None
) -> ActionResponse:
    logger.debug(f"Searching collection: {collection_name} with limit: {limit}")

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

        search_params = {
            "collection_name": collection_name,
            "query_vector": query_vector,
            "limit": limit
        }

        if score_threshold is not None:
            search_params["score_threshold"] = score_threshold

        search_results = client.search(**search_params)

        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })

        logger.info(f"Found {len(results)} results in collection '{collection_name}'")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            results=results,
            results_count=len(results),
            success=True,
            message=f"Found {len(results)} results"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message="Search completed successfully",
            code=200
        )

    except Exception as e:
        logger.error(f"Failed to search points: {str(e)}")

        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        output = ActionOutput(
            collection_name=collection_name,
            results=[],
            results_count=0,
            success=False,
            message=f"Error: {str(e)}"
        )

        return ActionResponse(
            output=output,
            tokens=tokens,
            message=f"Failed to search points: {str(e)}",
            code=500
        )
