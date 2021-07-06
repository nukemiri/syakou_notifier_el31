from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import datetime
import requests
from sendline import Line
import pickle
import config
import colorama
import os

options = Options()
#ヘッドレスモードで実行
options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
url = config.url
driver.get(url)
login_id = driver.find_element_by_id("studentId")
login_id.send_keys(config.student_id)
password = driver.find_element_by_id("password")
password.send_keys(config.password)
login_btn = driver.find_element_by_id("login")
login_btn.click()

f = open(os.path.join(os.path.dirname(__file__),"emptytimelist.txt"),"rb")
try:
    prelist = pickle.load(f)
except:
    prelist = []

avadates = []
avadatetimes =[]
notify_status = False



for i in range(3):
    time.sleep(3)
    html=driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    datelist = soup.find_all(class_="date")
    for i in range(7):
        emptynum = len(datelist[i+7].find_all(class_="status1"))
        print("空き数:"+str(emptynum))
        # if len(date.find_all(class_="status3"))+len(date.find_all(class_="status4"))>=2: 
        #     print(date.find(class_="view").text.replace("\n","").replace("\t","")+": 済")
        date = datelist[i].find(class_="view").text.replace("\n","").replace("\t","")
        if emptynum==0:
            try:
                print(date +": 満")
            except:
                pass
        else:
            try:
                print(date+": 空")
                count = 1
                emptylist = []
                for i in datelist[i+7].find_all("td"):
                    if "status1" in str(i):
                        emptylist.append(str(count))
                        avadatetimes.append(date +" "+str(count))
                    count += 1
                avadates.append(date +" "+" ".join(emptylist))
            except:
                pass
    next_btn = driver.find_element_by_class_name("float-right")
    next_btn.click()
driver.quit()

for i in avadatetimes:
    if i in prelist:
        pass
    else:
        notify_status = True
        break
if len(avadates)==0:
    print("*********\n空きなし\n*********")
else:
    print("*********\n空きあり\n"+"\n".join(avadates)+"\n*********")
    message = ("技能予約可能\n\n"+"\n".join(avadates)+"\n"+url)
    if notify_status:
        line = Line(config.line_token)

        try:
            result_line = line.send_message(message)
        except Exception as error:
            print('[LINE Notify] Result: Failed')
            print('[LINE Notify] ' + colorama.Fore.RED + 'Error: ' + error.args[0], end = '\n\n')
        else:
            if result_line['status'] != 200:
                # ステータスが 200 以外（失敗）
                print('[LINE Notify] Result: Failed (Code: ' + str(result_line['status']) + ')')
                print('[LINE Notify] ' + colorama.Fore.RED + 'Error: ' + result_line['message'], end = '\n\n')
            else:
                # ステータスが 200（成功）
                print('[LINE Notify] Result: Success (Code: ' + str(result_line['status']) + ')')
                print('[LINE Notify] Message: ' + result_line['message'], end = '\n\n')
f = open(os.path.join(os.path.dirname(__file__),"emptytimelist.txt"),"wb")
pickle.dump(avadatetimes,f)
