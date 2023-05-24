import logging
import time
from typing import List, cast

import pinecone
from llama_index import GPTPineconeIndex, ServiceContext, GPTVectorStoreIndex
from llama_index.data_structs.data_structs_v2 import PineconeIndexDict
from llama_index.data_structs.node_v2 import DocumentRelationship, Node
from llama_index.vector_stores import PineconeVectorStore
from llama_index.vector_stores.pinecone import generate_sparse_vectors, get_node_info_from_metadata
from llama_index.vector_stores.types import VectorStoreQueryResult, VectorStoreQuery, VectorStoreQueryMode
from pinecone import NotFoundException

from core.embedding.openai_embedding import OpenAIEmbedding
from core.vector_store.base import BaseVectorStoreClient, BaseGPTVectorStoreIndex, EnhanceVectorStore


class PineconeVectorStoreClient(BaseVectorStoreClient):
    def __init__(self, api_key: str, environment: str):
        self._client = self.init_from_config(api_key, environment)

    @classmethod
    def init_from_config(cls, api_key: str, environment: str):
        pinecone.init(
            api_key=api_key,
            environment=environment
        )
        return pinecone

    def get_index(self, service_context: ServiceContext, config: dict) -> GPTVectorStoreIndex:
        index_struct = PineconeIndexDict()

        if self._client is None:
            raise Exception("Vector client is not initialized.")

        index_name = config.get('index_name')
        if not index_name:
            raise Exception("index_name cannot be None.")

        try:
            self._client.describe_index(index_name)
        except NotFoundException:
            # pinecone index not found
            self._client.create_index(index_name, dimension=1536, metric="cosine", pod_type="p2")

            waiting_iterations = 120
            while waiting_iterations > 0:
                try:
                    index_info = self._client.describe_index(index_name)
                except:
                    logging.exception("Failed to query index status.")
                    break

                if index_info.status['ready']:
                    # index is ready
                    break

                time.sleep(1)
                waiting_iterations -= 1

        return GPTPineconeEnhanceIndex(
            service_context=service_context,
            index_struct=index_struct,
            vector_store=PineconeEnhanceVectorStore(
                pinecone_index=self._client.Index(index_name),
                tokenizer=OpenAIEmbedding().get_text_embedding
            )
        )

    def to_index_config(self, dataset_id: str) -> dict:
        index_id = "vector-" + dataset_id
        return {"index_name": index_id}


class GPTPineconeEnhanceIndex(GPTPineconeIndex, BaseGPTVectorStoreIndex):
    pass


class PineconeEnhanceVectorStore(PineconeVectorStore, EnhanceVectorStore):
    def query(self, query: VectorStoreQuery) -> VectorStoreQueryResult:
        """Query index for top k most similar nodes.

        Args:
            query_embedding (List[float]): query embedding
            similarity_top_k (int): top k most similar nodes

        """
        sparse_vector = None
        if query.mode in (VectorStoreQueryMode.SPARSE, VectorStoreQueryMode.HYBRID):
            if query.query_str is None:
                raise ValueError(
                    "query_str must be specified if mode is SPARSE or HYBRID."
                )
            sparse_vector = generate_sparse_vectors([query.query_str], self._tokenizer)[
                0
            ]
            if query.alpha is not None:
                sparse_vector = {
                    "indices": sparse_vector["indices"],
                    "values": [v * (1 - query.alpha) for v in sparse_vector["values"]],
                }

        query_embedding = None
        if query.mode in (VectorStoreQueryMode.DEFAULT, VectorStoreQueryMode.HYBRID):
            query_embedding = cast(List[float], query.query_embedding)
            if query.alpha is not None:
                query_embedding = [v * query.alpha for v in query_embedding]

        response = self._pinecone_index.query(
            vector=query_embedding,
            sparse_vector=sparse_vector,
            top_k=query.similarity_top_k,
            include_values=True,
            include_metadata=True,
            namespace=self._namespace,
            filter=self._metadata_filters,
            **self._pinecone_kwargs,
        )

        top_k_nodes = []
        top_k_ids = []
        top_k_scores = []
        for match in response.matches:
            text = match.metadata["text"]
            extra_info = get_node_info_from_metadata(match.metadata, "extra_info")
            node_info = get_node_info_from_metadata(match.metadata, "node_info")
            doc_id = match.metadata["doc_id"]
            id = match.metadata["id"]
            embedding = match.values

            node = Node(
                text=text,
                extra_info=extra_info,
                node_info=node_info,
                embedding=embedding,
                doc_id=id,
                relationships={DocumentRelationship.SOURCE: doc_id},
            )
            top_k_ids.append(match.id)
            top_k_nodes.append(node)
            top_k_scores.append(match.score)

        return VectorStoreQueryResult(
            nodes=top_k_nodes, similarities=top_k_scores, ids=top_k_ids
        )

    def delete_node(self, node_id: str):
        self._pinecone_index.delete([node_id])

    def exists_by_node_id(self, node_id: str) -> bool:
        query_response = self._pinecone_index.query(
            id=node_id
        )

        return len(query_response.matches) > 0
