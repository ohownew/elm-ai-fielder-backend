from sqlalchemy import create_engine, text
import re

def parseCompFromFileName(file_name):
    """从文件名中解析企业名"""
    regex = r'[^\-\d\s\.\:\!\?]*(公司|集团)'
    match = re.search(regex, file_name)
    if match:
        return match.group(0)
    else:
        return None

def searchCompany(company_name):
    """根据企业名查询企业信息"""
    host='172.16.124.10'  # 数据库地址
    port=3311  # 端口号
    user='readonly'  # 用户名
    passwd='XEvwijUpHtaxO9h6'  # 密码
    db='db2'
    engine = create_engine(f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}')

    with engine.connect() as conn:
        # 执行查询
        result_proxy = conn.execute(text(
            f"""
            select company_id, company_name, 
                city, district, street, 
                industry_l1_name, industry_l2_name, industry_l3_name, industry_l4_name,
                real_capital
            from db2.company_general_info
            where company_name = '{company_name}'
            limit 1;
            """
        ))
        # 获取字段名
        column_names = result_proxy.keys()
        # 获取查询结果
        results = result_proxy.fetchone()

    return dict(zip(column_names, results))


def searchPark(park_name):
    """根据园区名查询园区信息"""
    ...

def getCompInfo(file_name):
    """获取企业信息，主函数"""
    company_name = parseCompFromFileName(file_name)
    if company_name:
        com = searchCompany(company_name)
        return {
            'name': com['company_name'],
            'location': com['city'] + '|' + com['district'] + '|' + com['street'],
            'industry': com['industry_l1_name'] + '|' + com['industry_l2_name'] + '|' + com['industry_l3_name'] + '|' + com['industry_l4_name'],
            'scale': '实缴|' + com['real_capital']
        }
    else:
        return {
            'name': None,
            'location': None,
            'industry': None,
            'scale': None
        }


if __name__ == '__main__':
    # company_name = parseCompFromFileName('家电-小型-宁波欧普电器有限公司调研20240521.docx')
    # print(company_name)
    # if company_name:
    #     sql_result = searchCompany(company_name)
    #     print(sql_result)

    print(getCompInfo('家电-小型-宁波欧普电器有限公司调研20240521.docx'))