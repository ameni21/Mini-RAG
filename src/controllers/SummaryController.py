
from .BaseController import BaseController
from typing import List


class SummaryController(BaseController):

    def __init__(self, generartion_client, template_parser ):
        super().__init__()       
        self.generation_client = generartion_client
        self.template_parser = template_parser

    
    def create_collection_name(self, project_id: str): 
        return f"collection_{project_id}".strip()
    
    

    def summary_transcript(self, retrieve_document : List[str], limit: int = 10):
        summary, full_prompt = None, None,


        if not retrieve_document or len(retrieve_document) == 0:
            return summary, full_prompt
        
        # Filter out None values from retrieve_document
        #retrieve_document = [doc for doc in retrieve_document if doc]

        # Step 2: Construct LLM prompt for summarization
        system_prompt = self.template_parser.get("summary", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("summary", "documents_prompt", {"chunk_text": text}) 
            for text in retrieve_document
        ])

        footer_prompt = self.template_parser.get("summary", "footer_prompt")

        full_prompt = "\n\n".join([system_prompt, documents_prompts, footer_prompt])

        # Step 3: Generate the summary
        answer  = self.generation_client.generate_text(
            prompt=full_prompt,
        )

        return answer, full_prompt





