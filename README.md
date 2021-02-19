>**莞工勤工俭学自动考勤助手**
>>Created on February 14, 2021 by Bertram for students of Dongguan University of Technology



# 目录
- [1. 项目概述](#1-项目概述)
    - [1.1. 简介](#11-简介)
    - [1.2. 功能展示](#12-功能展示)
    - [1.3. 使用技术](#13-使用技术)
- [2. 部署](#2-部署)
    - [2.1. fork仓库](#21-fork仓库)
    - [2.2. 设置Secrets](#22-设置secrets)
    - [2.3. 设置考勤时间](#23-设置考勤时间)
    - [2.4. * 配置config.ini](#24--配置config.ini)
    - [2.5. 开启Actions定时任务](#25-开启Actions定时任务)
- [3. 项目结构](#3-项目结构)
- [4. 常见问题](#4-常见问题)
    - [4.1. 设置8:30-12:00考勤，但实际考勤时间是8:30-11:59？](#41-设置830-1200考勤但实际考勤时间是830-1159)
    - [4.2. 设置8:30-12:00考勤，但工作流提前几十分钟就开始启动？](#42-设置830-1200考勤但工作流提前几十分钟就开始启动)
    - [4.3. 设置8:30-12:00考勤，但运行结果是0:30签到，3:59/4:00签退？](#43-设置830-1200考勤但运行结果是030签到359400签退)
    - [4.4. 使用这个程序会泄露我的个人账号/密码吗？](#44-使用这个程序会泄露我的个人账号密码吗)
- [5. 参考资料](#5-参考资料)


# 1. 项目概述
>[返回目录](#目录)
# 1.1. 简介
&emsp;&emsp;Auto_Attendance实现莞工学工系统勤工俭学岗位自动打卡的功能，适用于各学生助理、助理班主任等勤工俭学职位的日常考勤打卡。可以避免忘记打卡和打了卡但忘记签退等因“忘记”而引发的情况。  
&emsp;&emsp;因为云服务器的不稳定情况，Github Actions设置的定时任务往往会有几分钟到几十分钟不等的延迟；加上GitHub Actions本身的保护机制，单个程序最大运行时间是360分钟。因此，为保证其稳定性，程序定时每天7:30和13:30启动，然后在python程序中设置简单的循环进行监控，在需要签到和签退的时刻运行签到和签退操作。除了可以设置个人的考勤时间外，还能设置是否在休息日（包括法定节假日）是否考勤。


# 1.2. 功能展示
![功能展示](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Function%20display.png "")

# 1.3. 使用技术
- Python3.7
- Github Actions
- 网络爬虫（主要是requests和解析库的使用）
- 配置文件的基本认识


# 2. 部署
>[返回目录](#目录)
## 2.1. fork仓库

![fork仓库](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Fork%20repository.png "")

<br>

## 2.2. 设置Secrets
![点击Settings](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Click%20Settings.png "")

<br>

![添加secrets](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Click%20Secrets.png "")

<br>

|需要添加的repository secret|含义|例|
:-:|:-:|:-:
|USERNAME|DGUT中央认证系统账号|20184141xxxx|
|PASSWORD|密码|123456|

<br>

**添加USERNAME**

![添加USERNAME](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Add%20username.png "")

<br>

**添加PASSWORD**

![添加PASSWORD](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Add%20password.png "")

<br>

**添加成功**

![添加secret成功](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Set%20secrets%20success.png "")


## 2.3. 设置考勤时间

>**设置考勤时间不需要编辑python代码，仅需要编辑schedule.json文件**  
>&emsp;&emsp;在schedule.json文件中，"0"-"6"表示星期日-星期六（每周的第一天是星期日），其映射的列表表示考勤时间  
>&emsp;&emsp;考勤时间列表的每一个元素亦是一个列表，代表一次考勤的开始时间和结束时间，下面这个例子能让你更加清楚如何制定自己的考勤时间表  
>>Tips:
不要更改schedule.json的文件结构；时间要严格按照"时:分"的格式，不要精确到秒。否则将造成程序无法正常运行

<br>

**schedule.json**

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

<br>

*按照自己的需求设置即可，下面我们来对schedule.json进行在线编辑*

<br>

**点击schedule.json**
![点击schedule.json](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Click%20schedule.png "")

<br>

**编辑schedule.json**
![编辑schedule.json](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Edit%20schedule.png "")

<br>

**提交修改，成功设置考勤时间**
![提交修改](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Set%20schedule.png "")

<br>

## 2.4. * 配置config.ini

config.ini一般不需要进行配置。该文件下有两个参数：
- holiday_attendance：
bool类型，设置休息日及法定节假日是否考勤，True则考勤，False则不考勤，默认为False
- workAssignmentId：
int类型，设置考勤职位的ID，当你有2个职位的时候可能会用到该参数

<br>

>文件配置可参考[2.3. 设置考勤时间](#23-设置考勤时间)

<br>



## 2.5. 开启Actions定时任务
**点击Actions，启动工作流**  
![点击Actions开启工作流](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Start%20action.png "")
![手动开启该定时任务](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Manual%20start.png "")

<br>

**启动成功！**  
![点击Enable workflow](https://raw.githubusercontent.com/BertraMoon/project-img/master/Auto_Attendance/Action%20success.png "")


# 3. 项目结构
>[返回目录](#目录)

    auto_attendance
    │  attendance.py    
    │  config.ini
    │  README.md
    │  requirements.txt
    │  schedule.json
    │
    ├─.github
    │  └─workflows
    │          main.yml
    │
    └─Dgut
            DgutLogin.py
            DgutXgxtt.py
            __init__.py
            错误类型的说明.png

- attendance.py:
主程序
- config.ini:
关于休息日是否考勤、考勤职位ID等信息的配置文件
- README.md:
项目说明
- requirements.txt:
运行程序所需的python第三方库及使用版本
- schedule.json:
考勤时间配置文件
- .github/workflows/main.yml:
YAML文件，创建github action的工作流workflows
- Dgut:
作者编写的用于莞工账号模拟登录和相关系统进行爬虫操作的库


# 4. 常见问题
>[返回目录](#目录)
## 4.1. 设置8:30-12:00考勤，但实际考勤时间是8:30-11:59？
>由于网络会有波动，同时系统在访问量比较大的时候运行很慢，因此在程序层面设置了提前一分钟结束考勤。因此，实际情况会提前几十秒结束考勤

<br>

## 4.2. 设置8:30-12:00考勤，但工作流提前几十分钟就开始启动？
>Github Actions经常性不会准时开启定时任务，通常延迟几分钟到几十分钟才运行，因此程序设置了7:30和13:30的定时任务（因为GitHub Actions限制每个程序只能运行6个小时，因此分两次运行），在程序上设置时间监控进行考勤

<br>

## 4.3. 设置8:30-12:00考勤，但运行结果是0:30签到，3:59/4:00签退？
>Github Actions的时间是UTC时间，比北京时间慢8小时。因此8:30-12:00转换后就是0:30-4:00

<br>

## 4.4. 使用这个程序会泄露我的个人账号/密码吗？
>账号和密码是使用Github Actions Secrets保存，安全性由Github及其安全算法来保障。不能说万无一失，只能说安全性还是有保障的。如果你有一台一直在运行的电脑，直接本地运行会更具安全性，但相应地也失去便捷性


<br>
- 有需求或技术方面的问题请联系作者Email：3233406405@qq.com

# 5. 参考资料
>[返回目录](#目录)
- [莞工自动打卡&nbsp;&nbsp;Auto_Daily_Attendance-rebuild-](https://github.com/RanegadeHRH/Auto_Daily_Attendance-rebuild-/tree/ForWorkflow "莞工每日疫情打卡 - github仓库")

- [YAML语言教程](http://www.ruanyifeng.com/blog/2016/07/yaml.html "YAML 语言教程 - 阮一峰的网络日志")

- [GitHub Actions 入门教程](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html "GitHub Actions 入门教程 - 阮一峰的网络日志")

- [chinesecalendar · PyPI](https://pypi.org/project/chinesecalendar/)
