from Dgut.DgutXgxtt import DgutXgxtt
import time
import sys
import datetime
import json
import configparser
import chinese_calendar as calendar



def get_schedule(filename='./schedule.json'):
    '''
    获取今天的考勤时间表
    返回一个考勤时间列表[[start1, end1], [start2, end2]]
    '''
    try:
        fp = open(filename, 'r')
        schedule = json.loads(fp.read())
        
        # 获取今天的时间表
        now = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
        week = now.strftime("%w")
        
        schedule_today = schedule.get(week)
        if schedule_today == None:
            return None
        schedule_today.sort(key=lambda elem: int(elem[0].split(':')[0]))
        return schedule_today

    except FileNotFoundError:
        print(f'没找到文件{filename}')


def xgxtt_sign(username, password, flag, workAssignmentId=None):
    '''
    登录并考勤签到/签退
    flag = 1 => 签到
    flag = 2 => 签退
    '''
    mydgut = DgutXgxtt(username, password)

    # 签到/签退
    response = mydgut.attendance(flag=flag)

    # 如果错误码3开头，进行重新请求三次
    if str(response['code'])[0] == '3':
        for i in range(3):
            time.sleep(5)
            response = mydgut.attendance(flag=flag)
            if response['code'] == 1:
                break
    return response



if __name__ == '__main__':

    
    try:
        demand = {
            'holiday_attendance': False,
            'workAssignmentId': None,
        }

        # 获取config.ini配置文件信息
        config = configparser.ConfigParser()
        config.read("./config.ini", encoding='utf-8')
        attendance_demand = config.items('attendance')
        for item in attendance_demand:
            demand[item[0]] = item[1]
        
        if isinstance(demand['holiday_attendance'], str):
            demand['holiday_attendance'] = bool(demand['holiday_attendance'])
        
        if isinstance(demand['workAssignmentId'], str):
            demand['workAssignmentId'] = int(demand['workAssignmentId'])


        # 获取当前时间及是否为休息日
        run_time = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
        print(f"程序启动...\n当前时间 => {run_time.year}-{run_time.month}-{run_time.day} {run_time.hour}:{run_time.minute}:{run_time.second}")

        if calendar.is_holiday(run_time):
            raise Exception("今天是休息日")

        # 获取考勤时间，判断是否需要考勤
        schedule = get_schedule(filename='./schedule.json')
        if len(schedule):
            print("今天的考勤时间:", end='')
            for item in schedule:
                print(f" <{item[0]}-{item[1]}>", end='')
            print()
        else:
            raise Exception("今天没有考勤安排")


        # 获取账号密码，验证账号密码格式
        username = sys.argv[1]
        password = sys.argv[2]

        for atten in schedule:
            start = atten[0].split(":")
            end = atten[1].split(":")
            print("-"*20)
            print(f"{start[0]}:{start[1]}-{end[0]}:{end[1]}...")
            now = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
            if now.hour > int(start[0]) or (now.hour == int(start[0]) and now.minute > int(start[1])):
                continue
            
            if int(end[0])-run_time.hour > 6 or (int(end[0])-run_time.hour == 6 and int(end[1]) > run_time.minute):
                raise Exception("计算得到该程序运行总时长将超过6小时，程序自动终止运行")

            while True:
                now = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
                if now.hour == int(start[0]) and now.minute == int(start[1]):
                    break
            
            # 签到
            response1 = xgxtt_sign(username, password, 1, workAssignmentId=demand['workAssignmentId'])
            print(response1)
            if response1['code'] != 1:
                print("启动自动考勤失败！")
                exit()
            while True:
                now = datetime.datetime.utcnow()+datetime.timedelta(hours=8)
                if now.hour == int(end[0]) and now.minute+1 == int(end[1]):
                    break
                
            # 签退
            response2 = xgxtt_sign(username, password, 2, workAssignmentId=demand['workAssignmentId'])
            print(response2)
            if response2['code'] != 1:
                print("签到成功了但签退失败！")
                exit()

    except IndexError:
        print("请完整输入账号和密码")
    
    except ValueError as e:
        print(e)
    
    except configparser.NoSectionError:
        print("缺少配置文件config.ini或缺少session [attendance]")

    except Exception as e:
        print(e)

    except:
        print("程序结束：可能是未知的错误")

    
    
