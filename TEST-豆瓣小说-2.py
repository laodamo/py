# coding=utf-8
##############################
#爬取豆瓣电影数据并处理
#Created on 2018-10-17 19:08
#@author: cch
##############################
import requests
from bs4 import BeautifulSoup
data_all =[]
for i in range(0,400,20):##980
     url = 'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4'+'?start=%d&type=T'%i
     douban_data = requests.get(url)
     soup = BeautifulSoup(douban_data.text,'lxml')
     titles = soup.select('h2 a[title]')##titles = soup.select('h2 a.title')
     prices = soup.select('div.pub')
     stars  = soup.select('div span.rating_nums')
     for title,price,star in zip(titles,prices,stars):
         if star.get_text()=='':
             pri=0
         else:
             pri = float(star.get_text())   
         
         data = {'title':title.get_text().strip().split()[0],
                 'price':price.get_text().strip().split('/')[-1],
                 'star' :pri}
#         print(data)
         data_all.append(data)
len(data_all)
data_all[:5]  #查看前5个元素


#【【【【将整理好的数据存储到c:\Users\yubg\2.txt里
with open(r'c:\Users\treeg\2.txt','w',encoding='utf-8') as f:
    f.write(str(data_all)) 

#将c:\Users\yubg\2.txt读取到f4变量
f3 = open(r'c:\Users\treeg\2.txt','r',encoding='utf-8')
f4 = f3.read()
type(f4)
f4[:159]


#【【【【将f4转化为列表f5
f5 = eval(f4)  #还原到了data_all
type(f5) 
f5[:5]  



#【【【【将f5中的每一个字典元素中的值提取出来做成列表k，k中的每一个元素就是一个小说的[名称，价格，星等级]列表
k=f5
'''for i in f5:
    k.append(list(i.values()))'''
k[:10]#查看前10个元素'''



#【【【【将k列表做成一个数据框df
import pandas as pd
df = pd.DataFrame(columns = ["title", "price", "star"])
p=0
for j in k:
#    print(j)
    df.loc[p]=j
    p+=1
df.tail(20) #查看前5行数据


#【【【【计算出所有爬取下来的小说的平均星等级
df['star'].mean()


#【【【【如何处理price列为全部数字？并计算其均值。
#【【首先：将price列单独出来，按照小数点分成了两列
df0 = df['price'].str.rstrip('元')  #删除price列数据后的单位元
df1 = df0.str.split('.',1,True)#将数据按“.”分割成两列，1表示新增一列
df1.tail(20)   

#【【其次：将小数点后的数据处理成两位数字，并替换原数据
a1 = df1[1].str.slice(0,2)   #抽取数据
a1 = a1.fillna('00')         #替换数据
df1[1]=a1   #将处理好的小数点后的数据替换原来的数据df1[1]
df1.tail(20)

#【【第三：将小数点前的非数字全部去掉，仅保留数字
#from pandas import DataFrame 
#len(df1)
import re
for q in range(0,len(df1),1):
    i=0
    #print(q,len(df1[0][q]))
    '''while (str(df1[0][q])[i].isdigit()) & (i<len(df1[0][q])):
        i+=1
        str1.app str(df1[0][q])[i]
        
    
    if i>=len(df1[0][q]):
        df1[0][q]=0'''
    df1[0][q] = re.sub("\D", "", df1[0][q])
df1.tail()

#【【第四：将处理好的小数点前后两列用“.”合并,并替换df中price列
e=df1[0].map(str.strip)
f=df1[1].map(str.strip)
for x in range(len(df1)):
    df['price'][x]=".".join([e[x],f[x]])
df.tail()

type(df['price'][976])
#df['price'].astype(float)
df2 = pd.to_numeric(df['price'],errors='coerce')#转成数值型
df2.tail()

df['price'] = df2 #将处理好的数据替换df中price列


#【【【计算小说的均价情况
df.describe()  #describe函数对列进行统计,发现price少2项，查找问题
len(df['price'])   #总数不变，说明有2项数据可能为空

#【【【【分析原因：可能在强制转化为数值时出了问题！找原因
L=list(df1[0])         #将列中的数据做成列表 

for i in L:
    for j in list(i):
        if not j.isdigit():     #判断每一个数据是不是数值型
           print(L.index(i),i)  #将不是数值型的数据打印出来
           
#【【发现了异常元素808和810项，用0值替换，首先找到位置
df1[df1[0]=='2017-8-31']#查找数据所在的行列

df['price'][808] = 0
df['price'][810] = 0
 

#重新计算统计描述情况
df.describe()  


#【【【【对小说的星级分组：优[>=9.0],良[>=7.5],中[6.0],差[<6.0]。
bins= [0,7.5,8.5,9,max(df.star)+1]
lab = ["差","中","良","优"] 
dj  = pd.cut(df.star,bins,right=False,labels=lab) 
dj.head()    #仅显示前 5 行数据 Out

df['等级']=dj
df.head()

#【【分组统计
import numpy as np
df_gp = df.groupby(by=['等级'])['star'].agg({'人数':np.size,'平均值':np.mean,'最高分':np.max,'最低分':np.min}) 
df_gp

#【【【【做饼图
#显示中文的问题
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei'] #指定默认字体  
mpl.rcParams['axes.unicode_minus'] = False #解决图像中负号'-'显示为方块的问题  
  
## 【【切片将按顺时针方向排列并绘制.
import matplotlib.pyplot as plt 
labels = ['差', '中','良', '优']  ## 标注 
sizes = list(df_gp['人数'])       ## 大小 
colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral'] ## 颜色 

## 0.1 代表第二个块从圆中分离出来 
explode = (0.1, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs') 

##【【 绘制饼图 
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
         autopct='%1.1f%%', shadow=True, startangle=90) 
plt.axis('equal') 
plt.savefig(r'C:\Users\treeg\pc.png')
plt.show()















    



# -*- coding: utf-8 -*-
'''
Created on Wed Aug 15 21:06:00 2018
@author: yubg
'''
#将爬下来的html保存成txt
#file = douban_data.text #若有编码错误，可以先将file.encode("utf8"),再将file = file.decode("utf8")
#with open(r'c:\Users\yubg\1.txt','w',encoding='utf-8') as f:
#    f.write(file)  
    












