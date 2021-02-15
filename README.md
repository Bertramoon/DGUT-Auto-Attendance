>**莞工学生助理自动考勤**
>>Created on February 14, 2021 by Bertram for students of Dongguan University of Technology



# 目录
- [1. 实现功能](#1-实现功能)
- [2. 配置](#2-配置)
    - [2.1. fork仓库](#21-fork仓库)
    - [2.2. 设置Secrets](#22-设置secrets)
    - [2.3. 设置考勤时间](#23-设置考勤时间)
- [3. 开启定时任务](#3-开启定时任务)
    - [3.1. 点击Actions](#31-点击actions)
    - [3.2. 点击Enable workflow启动工作流](#32-点击enable-workflow启动工作流)
- [4. 项目结构](#4-项目结构)
- [5. 常见问题](#5-常见问题)
- [6. 参考资料](#6-参考资料)


# 1. 实现功能

东莞理工学院学工系统自动考勤

![实现功能](h "")


# 2. 配置

## 2.1. fork仓库

![fork仓库](h "")
## 2.2. 设置Secrets

>点击 Settings => Secrets => New repository secret，添加所需要的repository secret

![点击Secrets](h "")


|需要添加的repository secret|含义|例|
:-:|:-:|:-:
|USERNAME|DGUT中央认证系统账号|20184141xxxx|
|PASSWORD|密码|123456|


>添加USERNAME

![添加USERNAME](h "")



>添加PASSWORD

![添加PASSWORD](h "")

## 2.3. 设置考勤时间

>**设置考勤时间不需要编辑python代码，仅需要编辑schedule.json文件**  
>&emsp;&emsp;在schedule.json文件中，"0"-"6"表示星期日-星期六（每周的第一天是星期日），其映射的列表表示考勤时间  
>&emsp;&emsp;考勤时间列表的每一个元素亦是一个列表，代表一次考勤的开始时间和结束时间，下面这个例子能让你更加清楚如何制定自己的考勤时间表  
>>Tips:
不要更改schedule.json的文件结构，否则程序无法正常运行

<br>

**<center>schedule.json</center>**

```
{
    "0": [

    ],
    "1": [
        ["8:30", "10:10"],
        ["14:30", "17:30"]
    ],
    "2": [
        ["8:30", "12:00"]
    ],
    "3": [
        ["14:30", "17:30"]
    ],
    "4": [
        ["8:30", "10:10"]
    ],
    "5": [
        ["14:30", "17:00"]
    ],
    "6": [
        
    ]
}
``` 
<br>



**上面这段json代码的意思是：**
|星期|考勤时间|
:-:|:-:|
|星期日|-|
|星期一|8:30-10:10<br>14:30-17:30|
|星期二|8:30-12:00|
|星期三|14:30-17:30|
|星期四|8:30-10:10|
|星期五|14:30-17:30|
|星期六|-|




# 3. 开启定时任务
## 3.1. 点击Actions  
![点击Actions](h "")

## 3.2. 点击Enable workflow启动工作流  
![点击Enable workflow](h "")


# 4. 项目结构

    auto_attendance
    │  attendance.py
    │  README.md
    │  requirements.txt
    │  schedule.json
    │
    ├─.github
    │  └─workflows
    │          main.yml
    │
    └─dgut
            dgut_login.py
            dgut_xgxtt.py
            __init__.py
            错误类型的说明.png

- attendance.py:
主程序
- README.md:
项目说明
- requests.txt:
运行程序所需的python第三方库及使用版本
- schedule.json:
考勤时间配置文件
- .github/workflows/main.yml:
YAML文件，创建github action的工作流workflows
- dgut:
作者编写的用于莞工账号模拟登录和相关系统进行爬虫操作的库

# 5. 常见问题

>待补充


- 有技术方面的问题请联系作者email：3233406405@qq.com

# 6. 参考资料
- [莞工自动打卡&nbsp;&nbsp;Auto_Daily_Attendance-rebuild-](https://github.com/RanegadeHRH/Auto_Daily_Attendance-rebuild-/tree/ForWorkflow "莞工每日疫情打卡 - github仓库")

- [YAML语言教程](http://www.ruanyifeng.com/blog/2016/07/yaml.html "YAML 语言教程 - 阮一峰的网络日志")

- [GitHub Actions 入门教程](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html "GitHub Actions 入门教程 - 阮一峰的网络日志")

>[返回目录](#目录)
