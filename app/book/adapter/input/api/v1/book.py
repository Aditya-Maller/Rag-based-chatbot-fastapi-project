from fastapi import APIRouter, HTTPException
#connect for api to get data
from app.book.adapter.input.api.v1.request import CreateBookRequest, UpdateBookRequest
#connector for mongo db
from core.db.mongo_db import mongo_instance

book_router=APIRouter()
@book_router.post(
    "",
    response_model=dict,
)
async def create_book(request: CreateBookRequest):
    print("Book API was hit")
    print(f"The data received:{request.book_id}")
    print("Book id:",)
    print(f"Name:{request.name}")
    print(f"Book Title:{request.book_title}")
    print(f"Book Pages:{request.book_pages}")
    print(f"Publication Date:{request.pub_date}")
    print(f"Price:{request.price}")

    book_data=request.model_dump(mode='json')
    result=await mongo_instance.db.books.insert_one(book_data)
    return {
        "status": "success",
        "message": "Book information received!",
        "data": {
            "title": request.book_title,
            "student_assigned": request.name,
            "price": request.price
        }
    }
@book_router.get("")
async def get_all_books():
    books_list=[]
    cursor=mongo_instance.db.books.find({})
    async for document in cursor:
        document["_id"]=str(document["_id"])
        books_list.append(document)
    return books_list
@book_router.get("/{book_id}")
async def get_book_by_id(book_id: int):
    book=await mongo_instance.db.books.find_one({"book_id": book_id})
    if not book:
        raise HTTPException(status_code=404,detail="Book not found")
    book["_id"]=str(book["_id"])
    return book


@book_router.put("/{book_id}")
async def update_book(book_id: int, request: UpdateBookRequest):
    
    update_data = request.model_dump(exclude_unset=True, mode='json')
    if len(update_data) < 1:
        raise HTTPException(status_code=400, detail="Send at least 1 field to update")
    
    result = await mongo_instance.db.books.update_one(
        {"book_id": book_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {
        "status": "success",
        "message": "Book information updated successfully",
        "changes": update_data
    }
@book_router.delete("/{book_id}")
async def delete_book(book_id: int):
    result=await mongo_instance.db.books.delete_one({"book_id":book_id})
    if result.deleted_count==0:
        raise HTTPException(status_code=404,details="Book not found")
    return{
        "status":"success",
        "message":"Book deleted successfully"
    }
