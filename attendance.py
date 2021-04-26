from dgut_requests.dgut import dgutXgxt
import time
import sys
import datetime
import json
import configparser
import chinese_calendar as calendar
import yaml
import os
import click
import requests


def get_schedule(filename: str, flag: int):
    '''
    获取今天的考勤时间表
    返回一个考勤时间列表[[start1, end1], [start2, end2]]，也可能是空列表
    flag => 1->读取星期考勤表 2->读取特殊情况考勤表
    '''
    try:
        # 打开读取文件
        with open(filename, 'r') as fp:
            schedule = json.loads(fp.read())
        # 获取当前时间
        now = datetime.datetime.utcnow()+datetime.timedelta(hours=8)

        if flag == 1:
            schedule_today = schedule.get(now.strftime("%w"))
        elif flag == 2:
            schedule_today = schedule.get(now.strftime('%Y-%m-%d'))

        else:
            return None

        if not schedule_today:
            return None
        schedule_today = list(map(lambda i: list(
            map(lambda j: datetime.datetime.strptime(j, '%H:%M').time(), i)), schedule_today))
        schedule_today.sort()
        return schedule_today

    except FileNotFoundError:
        print(f'没找到文件{filename}')


def get_config(filename: str):
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
                demand['holiday_attendance'] = config.getboolean(
                    'attendance', 'holiday_attendance')
            if config.has_option('attendance', 'workAssignmentId'):
                demand['workAssignmentId'] = config.getint(
                    'attendance', 'workAssignmentId')
    except ValueError:
        print(
            "配置获取错误，系统将使用默认配置（节假日不打卡，考勤岗位ID为系统列表中的第一个）")
    except:
        print(f"读取配置文件{filename}出错")
    finally:
        return demand


def xgxtt_sign(username: str, password: str, flag: int, workAssignmentId: int = None, count=0):
    '''
    登录并考勤签到/签退
    flag = 1 => 签到
    flag = 2 => 签退
    '''
    try:
        if count > 3:
            return {'code': 0}
        mydgut = dgutXgxt(username, password)

        # 测试/签到/签退
        response = mydgut.attendance(
            flag=flag, workAssignmentId=workAssignmentId)
    except:
        response = xgxtt_sign(username, password, flag,
                              workAssignmentId, count+1)
    finally:
        return response


def utc_local(t: datetime.datetime):
    if isinstance(t, datetime.datetime):
        return t+datetime.timedelta(hours=8)
    return False


@click.command()
@click.option('-U', '--username', required=True, help="中央认证账号用户名", type=str)
@click.option('-P', '--password', required=True, help="中央认证账号密码", type=str)
def run(username, password):
    try:
        # 1、读取配置文件
        demand = get_config(filename="./config.ini")

        # 2、读取特殊情况考勤表
        special = get_schedule(filename='./special.json', flag=2)

        # 3、获取当前时间，并判断是否为休息日
        run_time = utc_local(datetime.datetime.utcnow())
        print(f"程序启动 >> {run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if calendar.is_holiday(run_time) and not demand['holiday_attendance'] and not special:
            raise Exception("今天是休息日")

        # 4、获取考勤时间，判断是否需要考勤
        schedule = special if isinstance(special, list) else get_schedule(
            filename='./schedule.json', flag=1)

        if not schedule:
            raise Exception("今天没有考勤安排")

        # 5、启动考勤程序
        for item in schedule:
            start_time = item[0]
            end_time = item[1]

            print("-"*20)
            print(
                f"正在进行{start_time.strftime('%H:%M')}至{end_time.strftime('%H:%M')}的考勤...")

            # 如果已经错过该考勤时间，则进入下一个考勤时间
            if utc_local(datetime.datetime.utcnow()).time() > start_time:
                print("已经错过了该考勤时间")
                continue

            # 如果考勤无法正常签退，则不进行考勤（程序只能运行6小时）
            if run_time.hour + 5.9 < end_time.hour:
                raise Exception("计算得到该程序运行总时长将超过6小时，程序自动终止运行")

            while True:
                if utc_local(datetime.datetime.utcnow()).time() >= start_time:
                    break
                time.sleep(10)

            # 6、签到
            response = xgxtt_sign(username, password, 1,
                                  workAssignmentId=demand['workAssignmentId'])
            if response.get('info'):
                if response.get('info').get('time'):
                    response['info']['time'] = utc_local(
                        response['info']['time'])
            print(response)
            if response['code'] == 0:
                u = dgutXgxt(username, password)
                print(u.attendance(1, demand['workAssignmentId']))

            while True:
                if utc_local(datetime.datetime.utcnow()).time() >= end_time:
                    break
                time.sleep(15)

            # 7、签退
            response = xgxtt_sign(username, password, 2,
                                  workAssignmentId=demand['workAssignmentId'])
            if response['code'] == 0:
                u = dgutXgxt(username, password)
                print(u.attendance(2, demand['workAssignmentId']))
            if response.get('info'):
                if response.get('info').get('time'):
                    response['info']['time'] = utc_local(
                        response['info']['time'])
            print(response)

    except IndexError:
        print("请完整输入账号和密码")
    except requests.exceptions.ConnectTimeout:
        print('服务器连接超时')
    except requests.exceptions.ReadTimeout:
        print('在指定时间内未响应')
    except requests.exceptions.ConnectionError:
        print('与服务器连接失败，可能是找不到服务器或网络环境差')
    except Exception as e:
        if not e:
            print("程序结束：可能是未知的错误")
        else:
            print(e)
    except:
        print("程序出现未知错误")


if __name__ == '__main__':
    run()
