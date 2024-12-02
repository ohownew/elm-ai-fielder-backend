from typing import Union
from fastapi import (
    FastAPI, 
    UploadFile, 
    WebSocket, 
    HTTPException
)
from fastapi.middleware.cors import CORSMiddleware
from parseFile import parseOneFile
from getComInfo import getCompInfo
from getDocAbstract import DocAbstract


app = FastAPI(root_path='/dev-api')

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/uploadOneFile", tags=["企业园区调研文件解析"])
def upload_one_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    elif file.size > 10*1024*1024: # 10MB
        return {"message": "File too big"}
    else:
        result = {}
        result.update(parseOneFile(file.file))
        result.update(getCompInfo(file.filename))
        result['filename'] = file.filename
        result['filesize'] = f"{round(file.size/1024,2)}KB"
        return result


@app.post("/abstract",  tags=["文章标题摘要提炼"])
async def get_doc_abstract(file: UploadFile | None = None): # , background_tasks: BackgroundTasks):
    if not file:
        return HTTPException(status_code=422, detail="No upload file sent") # {"message": "No upload file sent"}
    else:
        doc = DocAbstract(file.file, file.filename)
        # background_tasks.add_task(doc.batch_summarise)
        # background_tasks.add_task(doc.get_abstract_md)
        await doc.async_batch_summarise()
        return {
            "message": "Get abstract success",
            "filename": file.filename.split(".doc")[0],
            "result": doc.docParsed_forHTTP
        }


@app.websocket("/abstractProcess")
async def get_abstract_process(websocket: WebSocket):
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")



@app.get("/items/{item_id}", tags=["测试get"])
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)