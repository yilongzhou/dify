import logging
from typing import List, Optional
from pymilvus import MilvusException

from llama_index import GPTMilvusIndex, ServiceContext, GPTVectorStoreIndex
from llama_index.data_structs.data_structs_v2 import MilvusIndexDict
from llama_index.data_structs.node_v2 import DocumentRelationship, Node
from llama_index.vector_stores import MilvusVectorStore
from llama_index.vector_stores.types import VectorStoreQueryResult, VectorStoreQuery, VectorStoreQueryMode

from core.embedding.openai_embedding import OpenAIEmbedding
from core.vector_store.base import BaseVectorStoreClient, BaseGPTVectorStoreIndex, EnhanceVectorStore


class MilvusVectorStoreClient(BaseVectorStoreClient):
    def __init__(self, host: str, port: int,
                 user: str = "", password: str = "", use_secure: bool = False):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_secure = use_secure

    def get_index(self, service_context: ServiceContext, config: dict) -> GPTVectorStoreIndex:
        index_struct = MilvusIndexDict()

        collection_name = config.get('collection_name')
        if not collection_name:
            raise Exception("collection_name cannot be None.")

        return GPTMilvusEnhanceIndex(
            service_context=service_context,
            index_struct=index_struct,
            vector_store=MilvusEnhanceVectorStore(
                collection_name=collection_name,
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                use_secure=self._use_secure,
                overwrite=False,
                tokenizer=OpenAIEmbedding().get_text_embedding
            )
        )

    def to_index_config(self, dataset_id: str) -> dict:
        index_id = "vector_" + dataset_id.replace("-", "_")
        return {"collection_name": index_id}


class GPTMilvusEnhanceIndex(GPTMilvusIndex, BaseGPTVectorStoreIndex):
    pass


class MilvusEnhanceVectorStore(MilvusVectorStore, EnhanceVectorStore):
    # Vector field is not supported in current release.

    def delete_node(self, node_id: str):
        try:
            # Begin by querying for the primary keys to delete
            self.collection.delete(f"id in [\"{node_id}\"]")
            logging.debug(f"Successfully deleted embedding with node_id: {node_id}")
        except MilvusException as e:
            logging.debug(f"Unsuccessfully deleted embedding with node_id: {node_id}")
            raise e

    def exists_by_node_id(self, node_id: str) -> bool:
        try:
            rst = self.collection.query(
              expr=f"id in [\"{node_id}\"]",
              offset=0,
              limit=1,
              consistency_level="Strong"
            )

            if len(rst) > 0:
                return True
        except MilvusException as e:
            raise e

        return False
