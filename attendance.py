from dgut.dgut_xgxtt import dgut_xgxtt
import time
import sys

def sign(username, password, flag):
    # 登录
    mydgut = dgut_xgxtt(username, password)

    # 签到/签退
    response = mydgut.attendance(flag=flag)

    # 如果错误码3开头，进行重新请求三次
    if str(response['code'])[0] == '3':
        for i in range(3):
            time.sleep(5)
            response = mydgut.attendance(flag=1)
            if response['code'] == 1:
                break
    return response


if __name__ == '__main__':

    # 验证账号密码和登录时间
    try:
        username = sys.argv[1]
        password = sys.argv[2]
        attendance_time = int(sys.argv[3])

        # 签到
        response1 = sign(username, password, 1)
        print(response1)
        if response1['code'] != 1:
            print("启动自动考勤失败！")
            exit()
        

        # 考勤时间
        time.sleep(attendance_time - 5)


        # 签退
        response2 = sign(username, password, 2)
        print(response2)
        if response2['code'] != 1:
            print("签到成功了但签退失败！")
            exit()

    except ValueError:
        print("考勤时间（第三个参数）应输入一个整数")

    except IndexError:
        print("请完整输入账号、密码和考勤时间")
    
    except:
        print("未知的错误")

    
    