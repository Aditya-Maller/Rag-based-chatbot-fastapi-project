from pydantic import BaseModel, Field

class IngestRequest(BaseModel):
    text: str=Field(...,description="The content to store in the knowledge base")

    source_name: str=Field(...,description="Source of the info")

class SearchRequests(BaseModel):
    query: str=Field(...,description="The search query to find relevant documents")