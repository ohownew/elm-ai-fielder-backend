import requests
import json
from docx import Document
from typing import IO

MODEL = "gpt-4o-mini"

def read_docx(file):
    doc = Document(file)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

####### GPT #######
def gpt_json_mode(messages: list):
    url = 'https://api.openai.com/v1/chat/completions'
    api_key = "" # your api key
    # Define the proxy
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "http://127.0.0.1:10809",
    }
    # headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # 参数验证
    if not isinstance(messages, list) or len(messages) == 0:
        raise ValueError("messages should be a non-empty list of strings")
    
    data = {
        "model": MODEL,
        "response_format": {"type": "json_object" },
        "messages": messages,
    }
    return requests.post(url, proxies=proxies, headers=headers, json=data)


prompt = """
# Character
You are a helpful assistant designed to output JSON.

## Skills
你是一个城市规划领域专家，你现在正在进行某个地区企业的调研，目的是了解企业需求痛点。需求类型主要分5类：
1. 产业空间需求。比如：分离品牌营销与制造，产业空间设置含营销等环节的办公类总部空间; 土地增容，解决土地审批难的问题，满足扩大生产需求; 需要扩产。已上报200亩土地的需求，希望继续在周巷，以方便集中管理。建设物流＋仓储＋生产一体化的智能厂区等......
2. 产业服务需求。比如：专业服务：品牌建设、商标维护，需要100w左右的资金; 科技创新：需要科技创新技术支持企业环保、绿色转型；需要关于申报国家单项冠军的辅导与支持; 希望提供企业出海的相应情报以及知识产权的保护、外观专利等.....
3. 生活服务及配套需求。比如：北部住房紧张，房价过高，一般就业人口、工人难以负担; 教育优惠政策、引进优秀师资; 需要居住优惠以及更多的人才公寓; 良好的工作环境、整体的发展环境、居住环境和好的交通条件; 需要高端的接待场所，如高档餐厅等......
4. 人才需求。比如：需要研发+营销相关的人才；从职业技能角度进行人才认定。按照企业人头数进行支持；需要有代表性、创造力的人才。研发人员外地为主等......
5. 其他需求。

请根据后面给出的某家企业的一次调研访谈记录中，归纳总结出这5类需求痛点，提炼精简，合并相似内容，并以json输出，格式参考：
{
    "产业空间需求": ["xxxx", "xxxx", ...],
    "产业服务需求": ["xxxx, "xxxx", ...],
    "生活服务及配套需求": ["xxxx", "xxxx", ...],
    "人才需求": ["xxxx", "xxxx", ...],
    "其他需求": ["xxxx", "xxxx", ...],
}

## Constraints
- 不存在相关需求痛点就留空[]，遵照记录内容，不要编造内容之外的需求;
- 注意区分需求和现状属性，比如：企业简介, 主营业务, 主要产品, 当前战略, 拥有的荣誉、知识产权等不属于需求，请忽略
"""


def parseOneFile(file: str | IO[bytes] | None = None) -> dict:
    # test
    messages = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": read_docx(file),
        }
    ]

    res = gpt_json_mode(messages)
    sector_res = json.loads(res.json()['choices'][0]['message']['content']) # 返回的结果
    for k,v in sector_res.items():
        sector_res[k] = [f'【{i+1}】{v[i]};' for i in range(len(v))]
    sector_res.update(res.json()['usage']) # 花费的token

    return sector_res


if __name__ == '__main__':
    # test
    test_file = r"\\172.10.10.6\研发中心数据小组\09_知产\06_内部竞赛\2024周年庆AI竞赛\总规部\业务场景资料\现场调研助手\调研信息结构化\调研纪要\家电-龙头-月立集团有限公司记录20240528.docx"

    print(parseOneFile(test_file))
    