from dgut_requests.dgut import dgutXgxt
import time
from datetime import datetime, timedelta
import json
import configparser
import chinese_calendar as calendar
import click
import schedule
from retry import retry

beijing_subtract_local_timedelta = datetime.utcnow() + timedelta(hours=8) - datetime.now()
def get_schedule(filename: str, flag: int):
    '''
    获取今天的考勤时间表
    返回一个考勤时间列表[[start1, end1], [start2, end2]]，也可能是空列表
    flag => 1->读取星期考勤表 2->读取特殊情况考勤表
    '''
    try:
        # 打开读取文件
        with open(filename, 'r') as f:
            data = json.load(f)
        # 获取北京时间（东八区）
        now = get_beijing_datetime()
        
        if flag == 1:
            plan_today = data.get(now.strftime("%w"))
        elif flag == 2:
            plan_today = data.get(now.strftime('%Y-%m-%d'))
        else:
            return None

        beijing_now = get_beijing_datetime().strftime("%Y-%m-%d ")
        plan = [[datetime.strptime(beijing_now+t, "%Y-%m-%d %H:%M") for t in item] for item in plan_today] if plan_today else list()
        plan.sort()
        return plan


    except FileNotFoundError:
        print(f'没找到文件{filename}')


def get_config(filename: str):
    """获取配置信息

    Args:
        filename (str): 文件路径

    Returns:
        dict: 配置信息
    """
    try:
        demand = {
            'holiday_attendance': False,
            'workAssignmentId': None,
        }

        # 获取config.ini配置文件信息
        config = configparser.ConfigParser()
        config.read(filename, encoding='utf-8')
        if config.has_section('attendance'):
            if config.has_option('attendance', 'holiday_attendance'):
                demand['holiday_attendance'] = config.getboolean('attendance', 'holiday_attendance')
            if config.has_option('attendance', 'workAssignmentId'):
                demand['workAssignmentId'] = config.getint('attendance', 'workAssignmentId')
    except ValueError:
        print("配置获取错误，系统将使用默认配置（节假日不打卡，考勤岗位ID为系统列表中的第一个）")
    except:
        print(f"读取配置文件{filename}出错，系统将使用默认配置")
    finally:
        return demand


def get_beijing_datetime():
    """获取当前北京时间

    Returns:
        datetime: 当前北京时间
    """
    return datetime.utcnow() + timedelta(hours=8)


def local2beijing(local_time: datetime):
    """将本地时间转为北京时间

    Args:
        local_time (datetime): 要转化的本地时间

    Returns:
        datetime: 转化之后的北京时间
    """
    return local_time + beijing_subtract_local_timedelta

def beijing2local(beijing_time: datetime):
    """将北京时间转为本地时间

    Args:
        beijing_time (datetime): 要转化的北京时间

    Returns:
        datetime: 转化之后的本地时间
    """
    return beijing_time - beijing_subtract_local_timedelta




def sign_in_out(u: dgutXgxt, flag: int, workAssignmentId: int=None):
    """签到/签退

    Args:
        u (dgutXgxt): 学工系统类
        flag (int): 签到=>1，签退=>2
        workAssignmentId (int, optional): 考勤职位的id. Defaults to None.
    """
    u.attendance_retry = retry(tries=20, delay=10, backoff=2, max_delay=30)(u.attendance)
    res = u.attendance_retry(flag=flag, workAssignmentId=workAssignmentId)
    print(f"[考勤结果] {get_beijing_datetime().strftime('%Y-%m-%d %H:%M:%S')} - {res}")


@click.command()
@click.option('-U', '--username', required=True, help="中央认证账号用户名", type=str)
@click.option('-P', '--password', required=True, help="中央认证账号密码", type=str)
def run(username, password):
    # 1、读取配置文件
    demand = get_config(filename="./config.ini")

    # 2、读取特殊情况考勤表
    special = get_schedule(filename='special.json', flag=2)

    # 3、获取当前时间，并判断是否为休息日
    run_time = get_beijing_datetime()
    print(f"[程序启动] 当前北京时间{run_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if calendar.is_holiday(run_time) and not demand['holiday_attendance'] and not special:
        exit("[程序结束] 今天是休息日")

    # 4、获取考勤时间，判断是否需要考勤
    plan = special if special else get_schedule(filename='schedule.json', flag=1)


    if not plan:
        exit("[程序结束] 今天没有考勤安排")

    # 5、设置账号信息
    u = dgutXgxt(username, password)
    

    # 6、启动考勤程序
    for item in plan:
        start_time = item[0]
        end_time = item[1]

        # 签退时间早于签到时间
        if end_time <= start_time:
            print(f"[加入考勤计划失败] {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')} - 签退时间不应该早于签到时间，因此该组考勤安排不加入本次考勤计划中")
            continue

        # 如果已经错过该考勤时间，则进入下一个考勤时间
        if get_beijing_datetime() >= start_time:
            print(f"[加入考勤计划失败] {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')} - 已经错过了该考勤时间，因此该组考勤安排不加入本次考勤计划中")
            continue

        # 如果考勤无法正常签退，则不进行考勤（程序只能运行6小时）
        if end_time - run_time >= timedelta(hours=5.9):
            print(f"[加入考勤计划失败] {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')} - 计算得在本程序执行（6小时）时间内无法完成考勤，因此该组考勤安排不加入本次考勤计划中")
            continue

        schedule.every().day.at(beijing2local(start_time).strftime("%H:%M")).do(sign_in_out, u=u, flag=1, workAssignmentId=demand['workAssignmentId'])
        schedule.every().day.at(beijing2local(end_time).strftime("%H:%M")).do(sign_in_out, u=u, flag=2, workAssignmentId=demand['workAssignmentId'])
        print(f"[加入考勤计划成功] {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')} - 已加入考勤队列")


    while True:
        schedule.run_pending()
        if not schedule.jobs:
            exit("[程序结束] 往后无考勤安排，程序退出")
        time.sleep(10)



if __name__ == '__main__':
    run()
