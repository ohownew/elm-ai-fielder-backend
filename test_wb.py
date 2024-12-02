from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Progress Monitor</title>
    </head>
    <body>
        <h1>Progress Monitor</h1>
        <div id="progress">0%</div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onopen = function(e) {
                console.log("Connection opened!");
            };
            ws.onmessage = function(event) {
                var progressElement = document.getElementById('progress');
                progressElement.innerText = event.data;
            };
            ws.onclose = function(e) {
                console.error('WebSocket closed unexpectedly');
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # 模拟一个循环任务
    for i in range(1, 101):
        await asyncio.sleep(0.1)  # 每次循环等待0.1秒
        await websocket.send_text(f"{i}%")  # 发送当前进度

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_wb:app", host="0.0.0.0", port=8002, reload=True)