import math
import re
import requests
import mysql.connector
from sqlalchemy import create_engine
import pymysql
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from sklearn import linear_model

# this program will get the information of the first 30 pages or the first 100 car ads on bama.ir about peugeot 206's and put them in a table in mysql db called carpredict
# then it will get the file carstopredict.csv as an input of car data we want to predict their prices of and the data already collected.
# using linear regression in sklearn,it will predict their prices
# carstopredict.csv is a csv file with 3 columns.
# the lable of the first column is "model" and in each cell of this column we should only write "206" because this program only woorks with peugeot 206
# the lable of the first column is "year" and in each cell we write the year our car was made
# the lable of the first column is "milage" and in each cell we write how many kilometers the car has traveled
# the result will be given in another csv file
#my example for carstopredict.csv will be sent for the answer of the project in the zip file along with the code

cnx = mysql.connector.connect(user='root', password='p1661374',
                              host='127.0.0.1',
                              database='test')
cursor=cnx.cursor()
cursor.execute("DROP TABLE IF EXISTS carpredict;")
sql ='''CREATE TABLE carpredict(
   model CHAR(20) NOT NULL,
   year char(40),
   milage char(40),
   price char(40)
);'''
cursor.execute(sql)
cnx.close()

carcount=0
pagecount=1
#while will get between 100 and 120 car information from cars that have all four criteria said in their ad(model,year,milage and price) or 30 pages of the site
while(carcount<=100 and pagecount<=30):
    url='https://bama.ir/car/peugeot/206-ir/all-trims?page='+str(pagecount)
    r=requests.get(url)
    soup=BeautifulSoup(r.text,'html.parser')
    val=soup.find_all('div',attrs={'class' : "listdata"})
    for v in val:
        cnx = mysql.connector.connect(user='root', password='p1661374',host='127.0.0.1',database='test')
        cost='N'
        list=re.split(r'\n+',v.text)
        # we are doing the ML prediction on pegout 206's
        name='206'
        for l in list:
            if l.find('کارکرد')!=-1:
                usagestr=(re.sub(r'کارکرد','',l)).strip()
                if usagestr.find('صفر')!=-1:
                    usage='0'
                else:
                    usage=usagestr
                    usage = (re.sub(r',', '', usage)).strip()
                break
        for l in list:
            if l.find('13') != -1:
                if l.find('206') == -1 and l.find('،') != -1:
                    year=(re.sub(r'،', '', l)).strip()
                    break
        for l in list:
            if l.find('توافقی')!=-1:
                break
            if l.find('در توضیحات')!=-1:
                break
            if l.find('تومان')!=-1:
                #this ifs are because sometimes it writes the number of days/hours since posted int the same element in list as price
                if re.search(r'^\d\s',l)!=None:
                    if re.search(r'\d',l)!=None:
                        coststr=(re.sub(r'^\d\s',' ',l)).strip()
                        coststr=(re.sub(r',','',coststr)).strip()
                        cost=(re.sub(r'تومان','',coststr)).strip()
                elif re.search(r'\s\d$',l)!=None:
                    if re.search(r'\d', l) != None:
                        coststr=(re.sub(r'\s\d$',' ',l)).strip()
                        coststr=(re.sub(r',','',coststr)).strip()
                        cost=(re.sub(r'تومان','',coststr)).strip()
                elif re.search(r'\d', l) != None:
                    cost=(re.sub(r'تومان','',l)).strip()
                    cost=(re.sub(r',','',cost)).strip()
                break
            if l.find('ماهانه')!=-1:
                break
            if l.find('پیش')!=-1:
                break
        if cost!='N':
            cursor = cnx.cursor()
            cursor.execute('insert into carpredict values(\'%s\',\'%s\',\'%s\',\'%s\')' % (name,year, usage, cost))
            carcount=carcount+1
        cnx.commit()
        cnx.close()
    pagecount=pagecount+1
















db_connection_str = 'mysql+pymysql://root:p1661374@127.0.0.1/test'
db_connection = create_engine(db_connection_str)

df = pd.read_sql('SELECT * FROM carpredict', con=db_connection)
print(df)
prediction=[]
df2=pd.read_csv("carstopredict.csv")
reg=linear_model.LinearRegression()
reg.fit(df[['model','year','milage']],df.price)
prediction=reg.predict(df2[['model','year','milage']])
df2['price predicted'] = prediction
root = tk.Tk()
canvas1 = tk.Canvas(root, width=300, height=300, bg='lightsteelblue2', relief='raised')
canvas1.pack()
def exportCSV():
    global df2
    export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    df2.to_csv(export_file_path, index=None, header=True)
saveAsButton_CSV = tk.Button(text='Export CSV', command=exportCSV, bg='green', fg='white',
                             font=('helvetica', 12, 'bold'))
canvas1.create_window(150, 150, window=saveAsButton_CSV)
root.mainloop()