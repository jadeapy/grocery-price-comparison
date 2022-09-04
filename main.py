import datetime
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

browser = webdriver.Chrome(executable_path=r"D:\\chromedriver.exe")
browser.get("https://www.loblaws.ca/")
time.sleep(2)
search_area = browser.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/header/form/div/div[1]/input')

for item_ in ['NEILSON milks', 'MUFFINS', 'lays']:
    search_area.send_keys(item_)
    search_area.submit()
    time.sleep(3)
    data = (browser.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/main/div/div/div/div[3]/div[2]/div[3]/div')).text
    data = data.split('\n')
    temp = data.copy()
    indices = [i for i, x in enumerate(data) if 'STOCK' in x]
    for i in indices:
        temp[i - 1] = temp[i - 1] + ' ' + temp[i]
    for index in sorted(indices, reverse=True):
        del temp[index]
    indices = [i for i, x in enumerate(temp) if 'ADD' in x]
    new_data = [temp[: indices[0] + 1]]
    for i in range(len(indices) - 1):
        start = indices[i] + 1
        end = indices[i + 1] + 1
        new_data.append(temp[start: end])

    raw = pd.DataFrame(new_data)
    sale = raw[raw[1] == 'SALE'].copy()
    sale.loc[sale[6] == 'ADD', 6] = 'IN STOCK'
    sale.loc[sale[6] == 'ADD LOW STOCK', 6] = 'LOW STOCK'
    sale.loc[sale[6] == 'ADD OUT OF STOCK', 6] = 'OUT OF STOCK'
    sale.columns = ['name', 1, 'sale_end_date', 'save', 4, 'avg_price', 'stock_level']
    sale['sale'] = True
    sale['org_price'] = sale[4].str.split('$').str[2]
    sale['sale_price'] = sale[4].str.split('$').str[1]
    sale['sale_end_date'] = sale['sale_end_date'].str.replace('Ends ', '')
    sale = sale.drop([1, 4], axis=1)

    df = raw[raw[1] != 'SALE']
    df = df.drop([4, 5, 6], axis=1)
    df.columns = ['name', 'org_price', 'avg_price', 'stock_level']
    df.loc[df['stock_level'] == 'ADD', 'stock_level'] = 'IN STOCK'
    df.loc[df['stock_level'] == 'ADD LOW STOCK', 'stock_level'] = 'LOW STOCK'
    df.loc[df['stock_level'] == 'ADD OUT OF STOCK', 'stock_level'] = 'OUT OF STOCK'

    df = pd.concat([df, sale])
    df['sale'] = df['sale'].fillna(False)
    today = datetime.datetime.today()
    df['date'] = today.strftime('%Y%m%d')
    df.to_csv(r'C:\Users\jadea\Desktop\Grocery_price_comparison\{}_{}.csv'.format(item_, today.strftime('%Y%m%d')),
              index=False)
    search_area.clear()
    print(df)





