from dgut_requests.dgut import dgutIllness
import time
import click


def try_report(u: dgutIllness, count: int = 0):
    try:
        if count > 10:
            return None
        response = u.report()
    except:
        time.sleep(30)
        response = try_report(u, count+1)
    finally:
        return response


@click.command()
@click.option('-U', '--username', required=True, help="中央认证账号用户名", type=str)
@click.option('-P', '--password', required=True, help="中央认证账号密码", type=str)
def main(username, password):
    u = dgutIllness(username, password)
    count = 1
    while True:
        response = try_report(u, 0)
        if response['code'] == 400 or not response['messsage'] == '提交异常' or count > 100:
            break
        count += 1
        time.sleep(10)
    print(response)


if __name__ == '__main__':
    main()
