from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json

class NLPController(BaseController):

    def __init__(self,vectordb_client, generartion_client, embedding_client ):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generartion_client
        self.embeddings_client = embedding_client

    
    def create_collection_name(self, project_id: str): 
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)


        return json.loads( #convert data to dict
            json.dumps(collection_info, default=lambda x : x.__dict__) # convert data to string
        )
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunks_ids: List[int],
                             do_reset: bool = False):
        
        #step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        #step2: manage items
        texts = [c.chunk_text for c in chunks]
        metadatas = [c.chunk_metadata for c in chunks]

        vectors = [
            self.embeddings_client.embed_text(text=text,
                                              document_type=DocumentTypeEnum.DOCUMENT.value )
            for text in texts
        ]

        #step3: creating collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name = collection_name,
            embedding_size = self.embeddings_client.embedding_size,
            do_reset = do_reset,
        )
        

        #step4: insert into  vrctor DB
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadatas,
            vectors= vectors,
            record_ids=chunks_ids,
        )

        return True

    def search_vector_db_collection(self, project: Project, text:str, limit: int = 10):

        #step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        #step2: get text embedding vector 
        
        vector = self.embeddings_client.embed_text(text=text,
                                                 document_type=DocumentTypeEnum.QUERY.value)
        
        if not vector or len(vector) == 0:
            return False

        #step3 : do semantic search 
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False

        return json.loads(
            json.dumps(results, default=lambda x: x.__dict__)
        )





