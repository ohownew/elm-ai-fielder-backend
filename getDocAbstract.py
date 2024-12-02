import asyncio
from typing import IO
import requests
from docx import Document
import time
from tqdm import tqdm
# from fastapi import WebSocket
from httpx import AsyncClient
from tqdm.asyncio import tqdm_asyncio

MODEL = 'qwen-plus'
SPEED = 5

class DocAbstract:
    def __init__(self, docFile: str | IO[bytes], docName: str):
        self.docFile = docFile
        self.docName = docName.split('.doc')[0]
        self.docParsed = DocAbstract.parse_doc(docFile)
        # self.docParsed_forHTTP = {".".join([str(each) for each in key]): value for key, value in self.docParsed.items()}
        self.docList = [{
            "head_id": ".".join([str(i) for i in k]), 
            "head": v["head"], 
            "content": v["content"] if "content" in v.keys() else None
            } for k, v in self.docParsed.items()
        ]
        
    @staticmethod
    def parse_doc(docFile):
        doc = Document(docFile)
        # 加载 Word 文档
        docParsed = {}
        head_flag = [0,0,0]
        current_level = 0

        # 遍历文档中的所有段落
        for para in doc.paragraphs:
            # 检查段落的样式是否是标题样式
            if para.style.name == 'Heading 1':
                # 获取标题文本和级别
                text = para.text
                head_flag[0] += 1
                head_flag[1] = 0
                head_flag[2] = 0
                docParsed[tuple(head_flag[:1])] = {'head': text}
                current_level = 1
            elif para.style.name == 'Heading 2':
                # 获取标题文本和级别
                text = para.text
                head_flag[1] += 1
                head_flag[2] = 0
                docParsed[tuple(head_flag[:2])] = {'head': text}
                current_level = 2
            elif para.style.name == 'Heading 3':
                # 获取标题文本和级别
                text = para.text
                head_flag[2] += 1
                docParsed[tuple(head_flag[:3])] = {'head': text}       
                current_level = 3

            else: # 非前三级标题，将其内容添加到当前序号对应的content中
                if current_level == 0:
                    continue

                current_no = tuple(head_flag[:current_level])
                try:
                    if 'content' in docParsed[current_no].keys():

                            docParsed[current_no]['content'] = docParsed[current_no]['content'] + para.text
                    else:
                        docParsed[current_no]['content'] = para.text
                except Exception as e:
                        print(e, current_no, current_level)
                    
        return docParsed


    @staticmethod
    def summarise_by_ai(
        input, 
        output_words=50,
        prompt="将user输入的内容进行总结提炼，能罗列要点则罗列，不能则压缩"
    ):
        """
        AI提炼要点

        Params:
        - input: 用户输入内容
        - output_words: 输出字数，AI无法严格控制，只是一个估计值
        - prompt: 提示词
        """
        url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        api_key = "" # 添加自己的api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # "X-DashScope-SSE": "enable"
        }
        proxies = {
            "http": "http://127.0.0.1:10809",
            "https": "http://127.0.0.1:10809",
        }

        data = {
            "model": MODEL,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": f"{prompt}。要求：{output_words}个汉字以内"
                    },
                    {
                        "role": "user",
                        "content": input
                    }
                ],
            },
            "parameters": {
                "result_format": "message",
            },
        }

        try:
            res = requests.post(url, proxies=proxies, headers=headers, json=data)
            if res.status_code == 200:
                return res.json()['output']['choices'][0]['message']['content']
            else:
                return 'bad'
        except:
            return 'bad'
    

    def batch_summarise(self): # , websocket: WebSocket = None):
        pbar = tqdm(total=len(self.docParsed), desc="Summarising")
        bad_no = []
        for k, v in self.docParsed.items():
            if 'content' in v.keys():
                if len(v['content']) > 50:
                    res = DocAbstract.summarise_by_ai(v['content'])
                    if res == 'bad':
                        bad_no.append(k)
                    else:
                        self.docParsed[k]['abstract'] = res
                else:
                    v['abstract'] = v['content']
                pbar.update(1)
                # if websocket:
                #     progress = (pbar.n / pbar.total) * 100
                #     asyncio.run(websocket.send_text(f"Progress: {progress:.2f}%"))
            else:
                continue
        pbar.close()

        if len(bad_no)>0:
            print(bad_no)
        
        self.docParsed_forHTTP = {".".join([str(each) for each in key]): value for key, value in self.docParsed.items()}
        # self.get_abstract_md()


    def get_abstract_md(self):
        timestamp = int(time.time())  # 秒时间戳
        self.md_name = f'{timestamp}_{self.docName}_abs'
        with open(f'./markdown/{self.md_name}.md', 'w', encoding='utf-8') as file:
            for k, v in self.docParsed.items():
                head_level = len(k)
                if head_level == 1:
                    jinhao = '## '
                    head = jinhao + str(k[0]) + ' ' + v['head']
                elif head_level == 2:
                    jinhao = '### '
                    head = jinhao + str(k[0]) + '.' + str(k[1]) + ' ' + v['head']
                elif head_level == 3:
                    jinhao = '#### '
                    head = jinhao + str(k[0]) + '.' + str(k[1]) + '.' + str(k[2]) + ' ' + v['head']

                file.write(f"{head}\n")
                if 'abstract' in v.keys():
                    abstract = v['abstract']
                    file.write(f"{abstract}\n")


    @staticmethod
    async def async_summarise_by_ai(
        client,
        input, 
        output_words=50,
        prompt="将user输入的内容进行总结提炼，能罗列要点则罗列，不能则压缩"
    ):
        """
        AI提炼要点

        Params:
        - input: 用户输入内容
        - output_words: 输出字数，AI无法严格控制，只是一个估计值
        - prompt: 提示词
        """
        if len(input) <= 50:
            return input
        url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        data = {
            "model": MODEL,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": f"{prompt}。要求：{output_words}个汉字以内"
                    },
                    {
                        "role": "user",
                        "content": input
                    }
                ],
            },
            "parameters": {
                "result_format": "message",
            },
        }
        try:
            res = await client.post(url, json=data)
            if res.status_code == 200:
                return res.json()['output']['choices'][0]['message']['content']
            else:
                return 'bad'
        except Exception as e:
            print(e)
            return 'bad'
    

    async def async_summarise(self, client, k, v, semaphore):
        # 使用信号量获取锁
        async with semaphore:
            abstract = await DocAbstract.async_summarise_by_ai(client, v['content'])
            self.docParsed[k]['abstract'] = abstract


    async def async_batch_summarise(self): # , websocket: WebSocket = None):
        api_key = "" # 添加自己的api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # "X-DashScope-SSE": "enable"
        }
        proxies = {
            "http://": "http://127.0.0.1:10809",
            "https://": "http://127.0.0.1:10809",
        }
        async with AsyncClient(headers=headers, proxies=proxies) as client:
            tasks = []
            # 创建信号量
            semaphore = asyncio.Semaphore(SPEED)
            for k, v in self.docParsed.items():
                if 'content' in v.keys():
                    tasks.append(self.async_summarise(client, k, v, semaphore))
                else:
                    continue
            await tqdm_asyncio.gather(*tasks, total=len(tasks), desc="AI提炼摘要中...", colour='green')
        self.docParsed_forHTTP = {".".join([str(each) for each in key]): value for key, value in self.docParsed.items()}


if __name__ == '__main__':
    # doc = DocAbstract("./test/摘要测试.docx", "摘要测试.docx")
    from io import BytesIO
    res = requests.get("https://p26-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/972ab4784d7b4e40a90056f0a5a79a73.docx~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1758530865&x-signature=6A283f52ioDoOUC0lY4IO1w2cDc%3D")
    doc = DocAbstract(BytesIO(res.content), "摘要测试.docx")
    # asyncio.run(doc.async_batch_summarise())
    # doc.get_abstract_md()
    # for k, v in doc.docParsed.items():
    #     print(k,": ", v)
    for each in doc.docList:
        print(each)
    # doc.get_abstract_md()

    # doc = DocAbstract("./test/摘要测试.docx", "摘要测试.docx")
    # print(doc.docParsed_forHTTP)
#     res = DocAbstract.summarise_by_ai(
#         input = """
# 积极盘活“城中村”、工业园区宿舍等存量住房，提升特色住房（村居自建房）居住环境品质和供给质效，支持工厂企业对集体宿舍进行改造提升，满足新时代产业工人的安居需求。优化
# 政府职能，加强房地产市场和住房租赁市场监管，坚决遏制投机炒房，坚决打击住房租赁违法违规行为，维护市场秩序，防范和化解市场风险。"""
#     )
#     print(res)
    




