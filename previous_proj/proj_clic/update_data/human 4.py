
# coding: utf-8

# - 中国人寿及其同业数据，补充八分类和倾向性结果
# > - 七月及以前数据：db_docinfo_backup、db_docinfo_text_backup
# > - 七月之后数据：db_docinfo_trade、db_docinfo_text

# # 基本设置

# In[1]:


import numpy as np
import pandas as pd
import os
import datetime

import requests,json
from sklearn.externals import joblib

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
# get_ipython().magic('matplotlib inline')

import warnings
warnings.filterwarnings('ignore')


# In[2]:


from toolkits.setup.date_time import get_day_list
from toolkits.setup import specific_func
specific_func.set_ch_pd()


# # 连接数据库

# In[3]:


engine = specific_func.get_engine('cbirc')


# In[4]:


label_dic={'监管':1,'行业':2,'产品销售':3,'资本市场':4,'公司内部管理':5,'消费服务':6,'其他相关报道':7,'噪音':8}
class_name_dict = {v: k for k, v in label_dic.items()}
class_name_dict


# # 七月及以前数据

# In[5]:


ip_port = '47.93.183.157:10000'

headers={'content-type':'application/json'}
url_cor = "http://%s/judge_correlation_i"%ip_port
url_tend = "http://%s/tendency_analysis_i"%ip_port
url_warn = "http://%s/early_warning_i"%ip_port

for filename in ['raw/同业  8-10月.xlsx', ]:
    print(filename, '  ----------------')
    data = pd.read_excel(filename)
    data_null = data[data['八大分险类型'].isnull() | data['文章倾向性'].isnull()]
    data_full = data[data['八大分险类型'].notnull() & data['文章倾向性'].notnull()]
    print('总量：', data.shape)
    print('缺失值数量：', data_null.shape)
    print('无缺失值数量：', data_full.shape)

    id_list = tuple(data_null['id'].unique().tolist())
    print('id_list: ', len(id_list))

    sql_count = "select count(t1.id)                         from db_docinfo t1                             where t1.id in {0}".format(id_list)
    count = pd.read_sql_query(sql_count, engine)
    print('count: ', list(count.values)[0])

    sql_title = "select t1.id, t1.title                         from db_docinfo t1                             where t1.id in {0}".format(id_list)

    sql_content = "select t1.id, t2.text as content                         from db_docinfo t1, db_docinfo_text t2                             where t1.urlhash = t2.urlhash                                 and t1.id in {0}".format(id_list)

    title_id = pd.read_sql_query(sql_title, engine)
    content_id = pd.read_sql_query(sql_content, engine)
    title_content = pd.merge(title_id, content_id, on = 'id', how = 'left')
    print('title_content: ', title_content.shape)
        
    chunksize = 100
    loop = int(len(id_list) / chunksize) + 1
    title_content_com = pd.DataFrame()
    for i in range(loop):
        print('id_list_sel: ', 0 + i * chunksize, chunksize + i * chunksize)        
        data = {"types":3, "record":title_content.iloc[0 + i * chunksize:chunksize + i * chunksize,
                                                       [0, 1, 2]].to_dict(orient = 'records')}

        # 相关性模型
        result = requests.post(url_cor, data = json.dumps(data),
                               headers=headers, allow_redirects=True)
        json_data = json.loads(result.text)
        cor_elapsed_time = json_data['elapsed_time']
        print('cor elapsed_time: ', cor_elapsed_time)
        cor_list = [[j['cor'], j['id']] for j in json_data['docs']]
        cor_list = pd.DataFrame(cor_list, columns = ['八大分险类型', 'id'])

        # 倾向性模型
        try :
            result = requests.post(url_tend, data = json.dumps(data),
                                   headers=headers, allow_redirects=True)
            json_data = json.loads(result.text)
            tend_elapsed_time = json_data['elapsed_time'] 
            print('tend elapsed_time: ', tend_elapsed_time)
            tendency_list = [[j['tendency'], j['id']] for j in json_data['docs']]            
        except Exception as e:
            print('error: ', e)
            tendency_list = []
            for index in range(len(data['record'])):
#                 print(index, '.................')
                data_sel = {"types":3, "record":[data['record'][index]]}
#                 print('data_sel: ', data_sel)
                try :
                    result = requests.post(url_tend, data = json.dumps(data_sel),
                                           headers=headers, allow_redirects=True)
                    json_data = json.loads(result.text) 
                    tendency_list.append([json_data['docs'][0]['tendency'], json_data['docs'][0]['id']])
                except Exception as e1:
                    print('error again...    ', e1)
                    print(data['record'][index])
                    tendency_list.append([0, data['record'][index]['id']])            

        tendency_list = pd.DataFrame(tendency_list, columns = ['文章倾向性', 'id'])

        cor_tend = pd.merge(cor_list, tendency_list, on = 'id', how = 'inner')
        title_content_com = pd.concat([title_content_com, cor_tend], axis = 0)                
        print('    %s  title_id: '%i, title_id.shape)
        print('    %s  content_id: '%i, content_id.shape)
        print('    %s  title_content: '%i, title_content.shape)
        print('    %s  title_content_com: '%i, title_content_com.shape)
    
    title_content_com.index = range(title_content_com.shape[0])
    data_null = data_null.drop(['八大分险类型', '文章倾向性'], axis = 1)
    print('data_null: ', data_null.shape) 
    data_null = pd.merge(data_null, title_content_com, on = 'id', how = 'left')
    print('combined_data: ', data_null.shape)    
    data_null_still = data_null[data_null['八大分险类型'].isnull() | data_null['文章倾向性'].isnull()]
    print('data_null_still: ', data_null_still.shape) 
    data_null['八大分险类型'] = data_null['八大分险类型'].apply(lambda x: class_name_dict[x])
    data_null['文章倾向性'] = data_null['文章倾向性'].apply(lambda x: '非负' if x == 0 else '负面')
    
    update_data = pd.concat([data_null, data_full], axis = 0)
    print('update_data: ', update_data.shape) 
    
    writer = pd.ExcelWriter('result/{0}'.format(filename.split('/')[1]),
                            engine='xlsxwriter',
                            options={'strings_to_urls': False})

    update_data.to_excel(writer, sheet_name='Sheet1', index = False)
    writer.save()    

