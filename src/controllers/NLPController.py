from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json

class NLPController(BaseController):

    def __init__(self,vectordb_client, generartion_client, embedding_client, template_parser ):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generartion_client
        self.embeddings_client = embedding_client
        self.template_parser = template_parser

    
    def create_collection_name(self, project_id: str): 
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    
    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)

    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)


        return await json.loads( #convert data to dict
            json.dumps(collection_info, default=lambda x : x.__dict__) # convert data to string
        )
    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                             chunks_ids: List[int],
                             do_reset: bool = False):
        
        #step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        #step2: manage items
        texts = [c.chunk_text for c in chunks]
        metadatas = [c.chunk_metadata for c in chunks]

        vectors = [self.embeddings_client.embedding_text(text=texts,
                                                         document_type= DocumentTypeEnum.DOCUMENT.value)]

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

    async def search_vector_db_collection(self, project: Project, text:str, limit: int = 10):

        #step1: get collection name
        query_vector = None
        collection_name = self.create_collection_name(project_id=project.project_id)

        #step2: get text embedding vector 
        
        vectors = self.embeddings_client.embed_text(text=text,
                                                 document_type=DocumentTypeEnum.QUERY.value)
        
        if not vectors or len(vectors) == 0:
            return False
        
        if isinstance(vectors, list) and len(vectors) > 0 :
            query_vector = vectors[0]

        if not query_vector:
            return False

        #step3 : do semantic search 
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vectors,
            limit=limit
        )

        if not results:
            return False

        return results
    

    async def answer_rag_question(self, project: Project, query: str, limit: int = 10):

        answer, full_prompt, chat_history = None, None, None

        #step1: retrieve relative documents
        retrieve_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )

        if not retrieve_documents or len(retrieve_documents)==0:
            return answer, full_prompt, chat_history 
        
        # step 2: construct LLM prompt
        system_prompt = self.template_parser.get("rag","system_prompt")

        #documents_prompts = []
        #for idx, doc in retrieve_documents:
            #documents_prompts.append(
                #self.template_parser.get("rag","documents_prompt", {
                    #"doc_num": idx + 1,
                    #"chunk_text": doc.text,
                #})
            #)
           
        #the method is faster   
        documents_prompts = "\n".join([
            self.template_parser.get("rag","documents_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
                })
            for idx, doc in enumerate(retrieve_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt",{"query": query})

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
                #self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt =  "\n\n".join([documents_prompts,footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history





