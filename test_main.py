# test_main.py
from fastapi.testclient import TestClient
from main import app
import unittest
from unittest.mock import Mock, patch
# from fastapi.responses import JSONResponse
from fastapi import UploadFile

# 创建一个测试客户端
client = TestClient(app)

class TestMain(unittest.TestCase):
    # 测试没有上传文件时的情况
    def test_get_doc_abstract_no_upload_file(self):
        response = client.post("/abstract")
        assert response.status_code == 422  # 因为没有上传文件，应该返回422状态码
        # print(response.json())
        assert response.json() == {"message": "No upload file sent"}

    # 测试上传文件时的情况
    @patch('getDocAbstract.DocAbstract')
    def test_get_doc_abstract_with_upload_file(self, MockDocAbstract):
        # 创建一个模拟的UploadFile对象
        mock_file = Mock(spec=UploadFile)
        mock_file.name = "test.docx"
        
        # 模拟DocAbstract的行为
        mock_doc_abstract = MockDocAbstract.return_value
        mock_doc_abstract.docParsed = "Parsed content"
        
        # 发起请求
        response = client.post("/abstract", files={"file": mock_file})
        
        # 验证返回结果
        assert response.status_code == 200
        assert response.json() == "Parsed content"

        # 确认DocAbstract被正确实例化并调用了docParsed方法
        MockDocAbstract.assert_called_once_with(mock_file)
        mock_doc_abstract.docParsed.assert_called_once()

# 运行测试
if __name__ == "__main__":
    unittest.main()