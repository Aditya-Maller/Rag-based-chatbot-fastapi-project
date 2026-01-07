from fastapi import APIRouter, HTTPException
from huggingface_hub import InferenceClient
from core.db.mongo_db import mongo_instance 
from app.rag.adapter.input.api.v1.request import IngestRequest 
from core.llm.generation import gemini_generator
from core.config import config

rag_router = APIRouter()

HF_TOKEN=config.HF_TOKEN
MODEL_ID=config.MODEL_ID
SIMILARITY_THRESHOLD=0.5

client=InferenceClient(token=HF_TOKEN)

@rag_router.post("/ingest")
async def ingest_document(request: IngestRequest):
    if not mongo_instance.client:
        raise HTTPException(status_code=500, detail="Database down")

    try:
        #get embedding
        resp=client.feature_extraction(request.text, model=MODEL_ID)
        vector=resp.tolist() if hasattr(resp, "tolist") else resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    doc_data={
        "text": request.text,
        "source": request.source_name,
        "vector": vector 
    }
    
    try:
        await mongo_instance.db.rag_documents.insert_one(doc_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@rag_router.get("/search")
async def search_documents(query: str):
    if not mongo_instance.client:
        raise HTTPException(status_code=500, detail="Database down")

    try:
        resp = client.feature_extraction(query, model=MODEL_ID)
        query_vector = resp.tolist() if hasattr(resp, "tolist") else resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector fail: {str(e)}")

    # cosine similarity pipeline
    pipeline = [
        {
            "$addFields": {
                "score": {
                    "$let": {
                        "vars": {
                            "query": query_vector,
                            "doc": "$vector"
                        },
                        "in": {
                            "$divide": [
                                # dot product
                                { "$reduce": {
                                    "input": { "$zip": { "inputs": ["$$query", "$$doc"] } },
                                    "initialValue": 0,
                                    "in": { "$add": ["$$value", { "$multiply": [{ "$arrayElemAt": ["$$this", 0] }, { "$arrayElemAt": ["$$this", 1] }] }] }
                                }},
                                # magnitude
                                { "$multiply": [
                                    { "$sqrt": { "$reduce": { "input": "$$query", "initialValue": 0, "in": { "$add": ["$$value", { "$pow": ["$$this", 2] }] } } } },
                                    { "$sqrt": { "$reduce": { "input": "$$doc", "initialValue": 0, "in": { "$add": ["$$value", { "$pow": ["$$this", 2] }] } } } }
                                ]}
                            ]
                        }
                    }
                }
            }
        },
        { "$sort": { "score": -1 } },
        { "$limit": 3 },
        { "$project": { "_id": 0, "text": 1, "source": 1, "score": 1 } }
    ]

    cursor = mongo_instance.db.rag_documents.aggregate(pipeline)
    matches = await cursor.to_list(length=3)

    valid = [d for d in matches if d['score'] >= SIMILARITY_THRESHOLD]
    
    if not valid:
        return {"query": query, "answer": "No related info found in the database.", "sources": []}

    context = [d['text'] for d in valid]
    
    # generate answer
    ans = gemini_generator.generate_answer(context, query)

    return {
        "query": query,
        "answer": ans,
        "sources": [d['source'] for d in valid]
    }