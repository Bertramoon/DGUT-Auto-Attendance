>**莞工学生助理自动考勤**
>>Created on February 14, 2021 by Bertram for students of Dongguan University of Technology



# 目录
- [1. 项目概述](#1-项目概述)
    - [1.1. 功能展示](#11-功能展示)
    - [1.2. 使用技术](#12-使用技术)
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
    - [4.4. 待补充](#44-待补充)
- [5. 参考资料](#5-参考资料)


# 1. 项目概述
>[返回目录](#目录)
# 1.1. 功能展示

东莞理工学院学工系统自动考勤

![功能展示](https://raw.githubusercontent.com/BertraMoon/Auto_Attendance/main/img/功能展示.png "")

# 1.2. 使用技术
- Python3.7
- Github Actions
- 网络爬虫（主要是requests和解析库的使用）
- 配置文件的基础认识


# 2. 部署
>[返回目录](#目录)
## 2.1. fork仓库

![fork仓库](h "")
## 2.2. 设置Secrets

点击 Settings => Secrets => New repository secret，添加所需要的repository secret

![点击Secrets](h "")


|需要添加的repository secret|含义|例|
:-:|:-:|:-:
|USERNAME|DGUT中央认证系统账号|20184141xxxx|
|PASSWORD|密码|123456|

<br>

**添加USERNAME**

![添加USERNAME](h "")

<br>

**添加PASSWORD**

![添加PASSWORD](h "")


## 2.3. 设置考勤时间

>**设置考勤时间不需要编辑python代码，仅需要编辑schedule.json文件**  
>&emsp;&emsp;在schedule.json文件中，"0"-"6"表示星期日-星期六（每周的第一天是星期日），其映射的列表表示考勤时间  
>&emsp;&emsp;考勤时间列表的每一个元素亦是一个列表，代表一次考勤的开始时间和结束时间，下面这个例子能让你更加清楚如何制定自己的考勤时间表  
>>Tips:
不要更改schedule.json的文件结构，否则程序无法正常运行

<br>

**chedule.json**

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


## 2.4. * 配置config.ini

config.ini一般不需要进行配置。该文件下有两个参数：
- holiday_attendance：
bool类型，设置休息日及法定节假日是否考勤，True则考勤，False则不考勤，默认为False
- workAssignmentId：
int类型，设置考勤职位的ID，当你有2个职位的时候可能会用到该参数

<br>



## 2.5. 开启Actions定时任务
**点击Actions**  
![点击Actions](h "")

**点击Enable workflow启动工作流**  
![点击Enable workflow](h "")


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
    ├─Dgut
    │      DgutLogin.py
    │      DgutXgxtt.py
    │      __init__.py
    │      错误类型的说明.png
    │
    └─img

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
- img:
存放README.md所需的图片资源

# 4. 常见问题
>[返回目录](#目录)
## 4.1. 设置8:30-12:00考勤，但实际考勤时间是8:30-11:59？
>由于网络会有波动，同时系统在访问量比较大的时候运行很慢，因此在程序层面设置了提前一分钟结束考勤。因此，实际情况会提前几十秒结束了考勤

<br>

## 4.2. 设置8:30-12:00考勤，但工作流提前几十分钟就开始启动？
>Github Actions经常性不会准时开启定时任务，通常延迟几分钟到几十分钟才运行，因此程序设置了7:30和13:30的定时任务（因为GitHub Actions限制每个程序只能运行6个小时，因此分两次运行），在程序上设置时间监控进行考勤

<br>

## 4.3. 设置8:30-12:00考勤，但运行结果是0:30签到，3:59/4:00签退？
>Github Actions的时间是UTC时间，比北京时间慢8小时。因此8:30-12:00转换后就是0:30-4:00

<br>

## 4.4. 待补充



<br><br>
- 有需求或技术方面的问题请联系作者Email：3233406405@qq.com

# 5. 参考资料
>[返回目录](#目录)
- [莞工自动打卡&nbsp;&nbsp;Auto_Daily_Attendance-rebuild-](https://github.com/RanegadeHRH/Auto_Daily_Attendance-rebuild-/tree/ForWorkflow "莞工每日疫情打卡 - github仓库")

- [YAML语言教程](http://www.ruanyifeng.com/blog/2016/07/yaml.html "YAML 语言教程 - 阮一峰的网络日志")

- [GitHub Actions 入门教程](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html "GitHub Actions 入门教程 - 阮一峰的网络日志")

- [chinesecalendar · PyPI](https://pypi.org/project/chinesecalendar/)
