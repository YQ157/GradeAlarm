#!/usr/bin/env python
# coding: utf-8

# In[14]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import re
import sys
import configparser
import yagmail


# In[15]:


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')  # 此处建议更换为绝对路径，虚拟环境可能不能定位绝对路径
if not config:
    sys.exit("配置文件不存在或无法访问")
try:
    username = config.get('User','username')
    password = config.get('User','password')
    semesterId = config.get('Semester','id')
    emailUser = config.get('Email','user')
    emailPassword = config.get('Email','password')
    if not config.has_section('Grade'):
        config.add_section('Grade')
    if not config.has_option('Grade','count'):
        config.set('Grade','count','0')
    with open('config.ini','w') as configfile:
        config.write(configfile)
    gradeCount = config.get('Grade','count')
except:
    sys.exit("配置错误")
print('账号：',username)
print('密码：',password)
chrome_options = Options()
chrome_options.add_argument("--headless")  # 启用无头模式
chrome_options.add_argument("--disable-gpu")  # 关闭 GPU 加速
chrome_options.add_argument("--no-sandbox")


# In[16]:


driver = webdriver.Chrome(options=chrome_options)
driver.get('https://auth.cumtb.edu.cn/authserver/login?service=https%3A%2F%2Fjwxt.cumtb.edu.cn%2Fstudent%2Fsso%2Flogin')
time.sleep(2)


# In[18]:


username_input = driver.find_element(By.XPATH, '//*[@id="login-normal"]/div/form/div[1]/nz-input-group/input') 
username_input.send_keys(username)

# 定位到密码输入框并填写
password_input = driver.find_element(By.XPATH, '//*[@id="login-normal"]/div/form/div[2]/nz-input-group/input')  
password_input.send_keys(password)

# 定位到登录按钮并点击
wait = WebDriverWait(driver, 5)
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-normal"]/div[2]/form/div[6]/div/button')))
login_button.click()
# login_button = driver.find_element(By.XPATH, '//*[@id="submitBtn"]') 
# login_button.click()

# 等待登录操作完成，可以根据实际情况调整等待时间
time.sleep(5)


# In[19]:


try:
    if driver.session_id:
        welcome_message = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div/div[1]/div/div[2]/div[2]/div/span[2]') 
        print("登录成功！")
except:
    print("登录失败！")
    if driver.session_id:
        driver.quit()  # 关闭浏览器
    sys.exit("登录失败")
print("还是运行了")
driver.get("https://jwxt.cumtb.edu.cn/student/for-std/grade/sheet")
time.sleep(1)
url = driver.current_url
cookies = driver.get_cookies()
driver.quit()


# In[20]:


match = re.search(r"\d+",url)
if match:
    studentID = match.group()
    print(studentID)
else: 
    studentID = -1
    print("发生了某些错误，获取studentID失败")
print(url)


# In[21]:


for cookie in cookies:
    print(f"{cookie['name']}_{cookie['value']}")


# In[22]:


if studentID != -1:
    cookie_jar = {}
    for cookie in cookies:
        cookie_jar[cookie['name']] = cookie['value']
    gradeUrl = f"https://jwxt.cumtb.edu.cn/student/for-std/grade/sheet/get-grade-data/{studentID}?semesterId="
    response = requests.get(gradeUrl,cookies=cookie_jar)
    data = response.json()
    data = data['studentGradeList']
    semester = data['id2semesters']
    semesterId = next((k for k,v in semester.items() if v['name'] == semesterId),None)
    if semesterId:
        count_t = len(data['semesterId2studentGrades'][semesterId])
        if int(gradeCount) < count_t:
            try:
                email_subject = f"已有新科目出成绩，当前{count_t}科，上次{gradeCount}科"
                email_content = '\n'.join([f"{i['course']['nameZh']}:{i['gaGrade']}" for i in data['semesterId2studentGrades'][semesterId]])
            except:
                sys.exit("成绩单生成失败")
            try:
                yag = yagmail.SMTP(user=emailUser,password=emailPassword,host='smtp.qq.com',port=465) # 自行配置 smtp 服务器，此处以 qq 为例
                yag.send(to=emailUser,subject=email_subject,contents=email_content)
            except:
                sys.exit("邮件发送失败")
            gradeCount = count_t
            config.set('Grade','count',str(gradeCount))
            with open('config.ini','w') as configfile:  # 此处建议更换为绝对路径，虚拟环境可能不能定位绝对路径
                config.write(configfile)
            print("成功")


# In[ ]:




