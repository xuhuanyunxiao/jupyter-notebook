
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

# In[53]:


engine = specific_func.get_engine('cbirc')


# # 七月及以前数据

# In[54]:


ip_port = '47.93.183.157:10000'

headers={'content-type':'application/json'}
url_cor = "http://%s/judge_correlation_i"%ip_port
url_tend = "http://%s/tendency_analysis_i"%ip_port
url_warn = "http://%s/early_warning_i"%ip_port

file_list_1 = ['raw/人寿 7月.xlsx', 'raw/同业  七月.xlsx']


# In[ ]:


# for filename in file_list_1:
#     print(filename, '  ----------------')
#     data = pd.read_excel(filename)
#     data_null = data[data['八大分险类型'].isnull() | data['文章倾向性'].isnull()]
#     data_full = data[data['八大分险类型'].notnull() & data['文章倾向性'].notnull()]
#     print('总量：', data.shape)
#     print('缺失值数量：', data_null.shape)
#     print('无缺失值数量：', data_full.shape)

#     id_list = tuple(data_null['id'].tolist())

#     chunksize = 2000
#     sql_count = "select count(t1.id)                         from db_docinfo_backup t1                             where t1.id in {0}".format(id_list[:5])
#     count = pd.read_sql_query(sql_count, engine)
#     loop = int(list(count.values)[0] / chunksize) + 1

#     sql_cbirc = "select t1.id, t1.title,t2.text as content                         from db_docinfo_backup t1, db_docinfo_text_backup t2                             where t1.urlhash = t2.urlhash                                 and t1.id in {0}".format(id_list)

#     combine_data = pd.DataFrame()
#     i = 0
#     for tmp_data in pd.read_sql_query(sql_cbirc, engine, chunksize = chunksize):
#         i += 1        
#         print('--  一、共 %s次循环，第 %s 次获取数据，开始...'%(loop, i))
#         print(tmp_data.shape)

#         data = {"types":3, "record":tmp_data.iloc[:,[0, 1, 2]].to_dict(orient = 'records')}

#         # 相关性模型
#         result = requests.post(url_cor, data = json.dumps(data),
#                                headers=headers, allow_redirects=True)
#         json_data = json.loads(result.text)
#         cor_elapsed_time = json_data['elapsed_time']
#         print('cor elapsed_time: ', cor_elapsed_time, '    tmp_data: ',tmp_data.shape)
#         cor_list = [[j['cor'], j['id']] for j in json_data['docs']]
#         cor_list = pd.DataFrame(cor_list, columns = ['八大分险类型', 'id'])

#         # 倾向性模型
#         result = requests.post(url_tend, data = json.dumps(data),
#                                headers=headers, allow_redirects=True)
#         json_data = json.loads(result.text)
#         tend_elapsed_time = json_data['elapsed_time'] 
#         print('tend elapsed_time: ', tend_elapsed_time, '    tmp_data: ',tmp_data.shape)
#         tendency_list = [[j['tendency'], j['id']] for j in json_data['docs']]
#         tendency_list = pd.DataFrame(tendency_list, columns = ['文章倾向性', 'id'])

#         cor_tend = pd.merge(cor_list, tendency_list, on = 'id', how = 'inner')
#         combine_data = pd.concat([combine_data, cor_tend], axis = 0)

#     print('combine_data: ', combine_data.shape)    
#     print('data_null: ', data_null.shape) 
#     data_null.update(combine_data)
#     data_null_still = data_null[data_null['八大分险类型'].isnull() | data_null['文章倾向性'].isnull()]
#     print('data_null_still: ', data_null_still.shape) 

#     update_data = pd.concat([data_null, data_full], axis = 0)
#     print('update_data: ', update_data.shape) 

#     writer = pd.ExcelWriter('result/{0}'.format(filename),
#                             engine='xlsxwriter',
#                             options={'strings_to_urls': False})

#     update_data.to_excel(writer, sheet_name='Sheet1', index = False)
#     writer.save()


# # 七月之后数据

# In[ ]:


file_list_2 = ['raw/人寿  8-10月.xlsx', 'raw/同业  8-10月.xlsx']


# In[ ]:


for filename in file_list_2:
    print(filename, '  ----------------')
    data = pd.read_excel(filename)
    data_null = data[data['八大分险类型'].isnull() | data['文章倾向性'].isnull()]
    data_full = data[data['八大分险类型'].notnull() & data['文章倾向性'].notnull()]
    print('总量：', data.shape)
    print('缺失值数量：', data_null.shape)
    print('无缺失值数量：', data_full.shape)

    id_list = tuple(data_null['id'].tolist())

    chunksize = 2000
    sql_count = "select count(t1.id)                         from db_docinfo_trade t1                             where t1.id in {0}".format(id_list[:5])
    count = pd.read_sql_query(sql_count, engine)
    loop = int(list(count.values)[0] / chunksize) + 1

    sql_cbirc = "select t1.id, t1.title,t2.text as content                         from db_docinfo_trade t1, db_docinfo_text t2                             where t1.urlhash = t2.urlhash                                 and t1.id in {0}".format(id_list)

    combine_data = pd.DataFrame()
    i = 0
    for tmp_data in pd.read_sql_query(sql_cbirc, engine, chunksize = chunksize):
        i += 1        
        print('--  一、共 %s次循环，第 %s 次获取数据，开始...'%(loop, i))
        print(tmp_data.shape)

        data = {"types":3, "record":tmp_data.iloc[:,[0, 1, 2]].to_dict(orient = 'records')}

        # 相关性模型
        result = requests.post(url_cor, data = json.dumps(data),
                               headers=headers, allow_redirects=True)
        json_data = json.loads(result.text)
        cor_elapsed_time = json_data['elapsed_time']
        print('cor elapsed_time: ', cor_elapsed_time, '    tmp_data: ',tmp_data.shape)
        cor_list = [[j['cor'], j['id']] for j in json_data['docs']]
        cor_list = pd.DataFrame(cor_list, columns = ['八大分险类型', 'id'])

        # 倾向性模型
        result = requests.post(url_tend, data = json.dumps(data),
                               headers=headers, allow_redirects=True)
        json_data = json.loads(result.text)
        tend_elapsed_time = json_data['elapsed_time'] 
        print('tend elapsed_time: ', tend_elapsed_time, '    tmp_data: ',tmp_data.shape)
        tendency_list = [[j['tendency'], j['id']] for j in json_data['docs']]
        tendency_list = pd.DataFrame(tendency_list, columns = ['文章倾向性', 'id'])

        cor_tend = pd.merge(cor_list, tendency_list, on = 'id', how = 'onner')
        combine_data = pd.concat([combine_data, cor_tend], axis = 0)

    print('combine_data: ', combine_data.shape)    
    print('data_null: ', data_null.shape) 
    data_null.update(combine_data)
    data_null_still = data_null[data_null['八大分险类型'].isnull() | data_null['文章倾向性'].isnull()]
    print('data_null_still: ', data_null_still.shape) 

    update_data = pd.concat([data_null, data_full], axis = 0)
    print('update_data: ', update_data.shape) 

    writer = pd.ExcelWriter('result/{0}'.format(filename),
                            engine='xlsxwriter',
                            options={'strings_to_urls': False})

    update_data.to_excel(writer, sheet_name='Sheet1', index = False)
    writer.save()

