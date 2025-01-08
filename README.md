# 介绍
通过selenium模拟浏览器操作获取cookie，构造http请求获取成绩
# 步骤
1. 将py文件中smtp服务器设置为自己使用的邮箱的smtp服务器，`config.ini`的路径设置为绝对路径
2. 将`config.ini`中的各项信息设置好
3. 运行测试
4. 挂到云服务器的crontab中定期执行(例如设置为15mins)，即可在新科目出成绩第一时间收到邮件
