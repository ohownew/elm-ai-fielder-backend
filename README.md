# AI信息抽取工具elm-ai-fielder的后端

本项目的前端参考：[elm-ai-fielder-frontend](https://github.com/ohownew/elm-ai-fielder-frontend)

## 项目介绍
本项目旨在为企业园区调研提供高效的信息抽取工具。业务部门在对客户企业开展调研时，通常以Word文档或音频形式记录访谈内容，后期需要整理其中的关键信息为表格形式以便于分析。以往是人工整理，效率较低，而直接使用豆包、通义等AI问答助手做信息抽取，效果不稳定且无法批量处理。本项目基于AI大模型，开发了一款用于非结构化文本抽取信息的工具，能够精准按照预先设定的字段，提取调研文档中包含的关键信息，并输出为Excel表格。

## 技术选型
- **大模型**：采用GPT-4o和通义Plus的API接口，确保信息抽取的准确性和稳定性。
- **后端框架**：使用Python的FastAPI框架，实现快速开发和部署。
- **异步请求**：采用异步请求提升批量处理速度，提高系统性能。

## 技术细节
1. **信息抽取**：
   - 使用GPT-4o和通义Plus的API接口，通过JSON输出模式，严格按照需求字段输出。
   - 抽取的信息包括但不限于企业名称、位置、行业、规模、产业空间需求、产业服务需求、生活服务及配套需求、人才需求等。

2. **批量处理**：
   - 采用异步请求处理多个文件，提升批量处理速度。
   - 使用FastAPI的WebSocket实现前端与后端的实时通信，展示处理进度。

3. **文件处理**：
   - 支持上传Word文档，解析文档内容并提取关键信息。
   - 将提取的信息输出为结构化的Excel表格，便于后续分析和使用。

## 目录结构
```
elm-ai-fielder-backend/
├── getComInfo.py          # 从文件名中解析企业信息
├── parseFile.py           # 解析Word文档并提取关键信息
├── getDocAbstract.py      # 提取文档摘要
├── main.py                # FastAPI应用入口
└── README.md              # 项目说明文档
```

## 安装与运行
1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **配置API密钥**：
   - 在`parseFile.py`和`getDocAbstract.py`中配置GPT-4o和通义Plus的API密钥。

3. **启动应用**：
   ```bash
   uvicorn main:app --reload
   ```

4. **访问API**：
   - 访问`http://localhost:8001/docs`查看API文档。

## API接口
### 1. 上传单个文件并提取关键信息
- **路径**：`/uploadOneFile`
- **方法**：POST
- **参数**：
  - `file`：上传的Word文档
- **返回**：
  ```json
  {
    "message": "Get abstract success",
    "filename": "文件名",
    "result": {
      "产业空间需求": ["需求1", "需求2"],
      "产业服务需求": ["需求1", "需求2"],
      "生活服务及配套需求": ["需求1", "需求2"],
      "人才需求": ["需求1", "需求2"],
      "其他需求": ["需求1", "需求2"],
      "name": "企业名称",
      "location": "位置",
      "industry": "行业",
      "scale": "规模"
    }
  }
  ```

### 2. 提取文档摘要
- **路径**：`/abstract`
- **方法**：POST
- **参数**：
  - `file`：上传的Word文档
- **返回**：
  ```json
  {
    "message": "Get abstract success",
    "filename": "文件名",
    "result": {
      "1.0": {"head": "标题1", "content": "内容1", "abstract": "摘要1"},
      "1.1": {"head": "标题1.1", "content": "内容1.1", "abstract": "摘要1.1"},
      ...
    }
  }
  ```

### 3. 实时通信接口（还未实现）
- **路径**：`/abstractProcess`
- **方法**：WebSocket
- **功能**：前端与后端的实时通信，展示处理进度。

## 示例
### 1. 上传单个文件并提取关键信息
```bash
curl -X POST "http://localhost:8001/uploadOneFile" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@调研纪要.docx"
```

### 2. 提取文档摘要
```bash
curl -X POST "http://localhost:8001/abstract" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@调研纪要.docx"
```