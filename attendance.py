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

def get_config(filename):
    try:
        demand = {
            'holiday_attendance': False,
            'workAssignmentId': None,
        }

        # 获取config.ini配置文件信息
        config = configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        attendance_demand = config.items('attendance')
        for item in attendance_demand:
            demand[item[0]] = item[1]
        
        if isinstance(demand['holiday_attendance'], str):
            demand['holiday_attendance'] = bool(demand['holiday_attendance'])
        
        if isinstance(demand['workAssignmentId'], str):
            demand['workAssignmentId'] = int(demand['workAssignmentId'])
    except configparser.NoSectionError:
        print("缺少配置文件config.ini或缺少session [attendance]")
        demand = {
            'holiday_attendance': False,
            'workAssignmentId': None,
        }
    finally:
        return demand


def xgxtt_sign(username: str, password: str, flag: int, workAssignmentId=None):
    '''
    登录并考勤签到/签退
    flag = 0 => 测试
    flag = 1 => 签到
    flag = 2 => 签退
    '''
    mydgut = DgutXgxtt(username, password)

    # 测试/签到/签退
    response = mydgut.attendance(flag=flag)

    # 如果错误码3开头，进行重新请求三次
    if str(response['code'])[0] == '3':
        for i in range(3):
            time.sleep(5)
            response = mydgut.attendance(flag=flag)
            if response['code'] == 1:
                break
    return response

def utc_local(t: datetime.datetime):
    if isinstance(t, datetime.datetime):
        return t+datetime.timedelta(hours=8)
    return False

if __name__ == '__main__':

    
    try:
        # 读取配置文件
        demand = get_config(filename="./config.ini")

        # 获取当前时间及是否为休息日
        run_time = utc_local(datetime.datetime.utcnow())
        if not run_time:
            raise Exception("调用时间转换函数utc_local发生错误")
        print(f"程序启动...\n当前时间 => {run_time.year}-{run_time.month}-{run_time.day} {run_time.hour}:{run_time.minute}:{run_time.second}")

        if not demand['holiday_attendance'] and calendar.is_holiday(run_time):
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


        # 启动考勤程序
        for atten in schedule:
            start = atten[0].split(":")
            end = atten[1].split(":")
            start_time = datetime.datetime(year=run_time.year, month=run_time.month, day=run_time.day, hour=int(start[0]), minute=int(start[1]))
            end_time = datetime.datetime(year=run_time.year, month=run_time.month, day=run_time.day, hour=int(end[0]), minute=int(end[1]))

            print("-"*20)
            print(f"{start_time.hour}:{start_time.minute}-{end_time.hour}:{end_time.minute}...")


            # 如果已经不在这段考勤时间（设定是必须要在考勤签到时间的10分钟之前运行到这里才能通过）
            if utc_local(datetime.datetime.utcnow()+datetime.timedelta(minutes=10)) > start_time:
                print("已经错过了该考勤时间")
                continue
            
            # 如果考勤无法正常签退，则不进行考勤（程序只能运行6小时）
            if (run_time+datetime.timedelta(hours=5.9)) < end_time:
                raise Exception("计算得到该程序运行总时长将超过6小时，程序自动终止运行")
            
            # 在考勤开始的8分钟前运行测试，得到进行签到至少需要花费多少时间，并以此时间提前进行签到
            test = []
            for i in range(3):
                now1 = datetime.datetime.utcnow()
                response = xgxtt_sign(username, password, 0, workAssignmentId=demand['workAssignmentId'])
                now2 = datetime.datetime.utcnow()
                if response['code'] == 1:
                    test.append(now2-now1)
                time.sleep(60)
            if not len(test):
                raise Exception("请求超时")
            test_min = min(test)
            test_max = max(test)
            print(f"test_min:{test_min}")
            print(f"test_max:{test_max}")
            while True:
                if utc_local(datetime.datetime.utcnow()+test_min) >= start_time:
                    break
            time1 = datetime.datetime.utrnow()
            print(f"签到开始:{utc_local(datetime.datetime.utcnow())}")
            # 签到
            response = xgxtt_sign(username, password, 1, workAssignmentId=demand['workAssignmentId'])
            response['info']['time'] = utc_local(response['info']['time'])
            print(f"签到结束:{utc_local(datetime.datetime.utcnow())}")
            print(response)
            if response['code'] != 1:
                raise Exception("启动自动考勤失败！")


            while True:
                if utc_local(datetime.datetime.utcnow()+test_max) >= end_time:
                    break
            print(f"签退开始:{utc_local(datetime.datetime.utcnow())}")
            # 签退
            response = xgxtt_sign(username, password, 2, workAssignmentId=demand['workAssignmentId'])
            response['info']['time'] = utc_local(response['info']['time'])
            print(f"签退结束:{utc_local(datetime.datetime.utcnow())}")
            print(response)
            if response['code'] != 1:
                raise Exception("签到成功了但签退失败！")

    except IndexError:
        print("请完整输入账号和密码")
    
    except ValueError as e:
        print(e)

    except Exception as e:
        if not e:
            print("程序结束：可能是未知的错误")
        else:
            print(e)

    except:
        print("程序出现未知错误")

    
    
