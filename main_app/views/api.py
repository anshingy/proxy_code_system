#coding=utf-8
"""
警告！在请求中请勿以username 及password作为http请求的参数名！
"""
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse #用来进行命名空间的反调用
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse,HttpResponseRedirect #HttpResponseRedirect是用于进行url进行跳转
from main_app.models import *
from django.contrib.auth.models import User
import json
from .time_deal import *
import django.utils.timezone as timezone

def dump_and_response(data): #checked
    return HttpResponse(json.dumps(data), content_type="application/json")


"""
可通过TOKEN或username找代理账号
返回一个列表，第一个是User对象，第二个是Others_info对象。
"""
def get_proxy_account(TOKEN=None,username=None):
    if TOKEN != None:
        try:
            user_others_info = Others_info.objects.get(TOKEN=TOKEN)
            return [user_others_info.user,user_others_info]
        except:
            return False
    elif username != None:
        try:
            user_object = User.objects.get_by_natural_key(username=username)
            user_others_info = Others_info.objects.get(user=user_object)
            return [user_object,user_others_info]
        except:
            return False


"""
以下是管理员API
"""
def admin_code_check(admin_code): #checked
    try:
        Admin_code.objects.get(code = admin_code)
        return True
    except:
        return False

"""
代理账户开户API
url:http://127.0.0.1:8000/api/admin_proxy_account_add_api/?admin_code=testtest&proxy_username=Kong4&proxy_password=testtest&proxy_ad=测试广告&proxy_balance=88
参数:
admin_code = 管理员代码
proxy_username = 代理账户名
proxy_password = 代理密码
proxy_ad = 代理广告（不写就是为空字符串)
proxy_balance = 代理账户金额（不写默认为0)
返回值： (全部json格式）
"Fail,account already existed" 账户已存在，创建失败
"Success" 创建成功
"Error, admin code wrong"  管理员代码错误
"Error,bad request method POST" 错误的请求模式
"""

def admin_proxy_account_add_API(request): #已测试1
    if request.method == "POST":
        return dump_and_response("Error,bad request method POST")
    admin_code = request.GET['admin_code']
    if not admin_code_check(admin_code):
        return dump_and_response("Error, admin code wrong")
    proxy_username = request.GET['proxy_username']
    proxy_password = request.GET['proxy_password']
    try:
        proxy_ad = request.GET['proxy_ad']
    except:
        proxy_ad = ''
    try:
        proxy_balance = request.GET['proxy_balance']
    except:
        proxy_balance = 0
    user_object = authenticate(username = proxy_username,password = proxy_password)
    if user_object is None:
        user_object = User.objects.create_user(username=proxy_username,password=proxy_password)
        user_others_info = Others_info.objects.create(user=user_object,ad=proxy_ad,balance=proxy_balance)
        user_object.save()
        user_others_info.save()
        return dump_and_response("Success")
    else:
        return dump_and_response("Fail,account already existed")


"""
代理账户充值
url:http://127.0.0.1:8000/api/admin_proxy_account_topup/?admin_code=testtest&proxy_username=Kong2&money=30

参数：
admin_code 管理员代码
proxy_username 代理账号
money 添加金额

返回值:
["Success", "90"] 成功，第二个参数是目前的金额
"Error, admin code wrong"  管理员代码错误
"Error,bad request method POST" 错误的请求模式
"Proxy account not existed" 代理账号不存在
"""

def admin_proxy_account_topup(request): #已测试1
    if request.method == "POST":
        return dump_and_response("Error,bad request method POST")
    admin_code = request.GET['admin_code']
    if not admin_code_check(admin_code):
        return dump_and_response("Error, admin code wrong")
    proxy_username = request.GET['proxy_username']
    money = request.GET['money']
    user = get_proxy_account(username=proxy_username)
    if user:
        user_balance = user[1].balance
        user_balance = int(user_balance) +int(money)
        user[1].balance = user_balance
        user[1].save()
        return dump_and_response(["Success",user[1].balance])
    else:
        return dump_and_response("Proxy account not existed")

"""
代理账户金额修改
注意！此API功能用于清零，如果操作不当可能造成严重后果。且输入值必须大于等于0

url:http://127.0.0.1:8000/api/admin_proxy_account_balance_setup/?admin_code=testtest&proxy_username=Kong2&money=30

参数：
admin_code 管理员代码
proxy_username 代理账号
money 设置金钱

返回值:
["Success", "90"] 成功，第二个参数是目前的金额
"Error, admin code wrong"  管理员代码错误
"Error,bad request method POST" 错误的请求模式
"Proxy account not existed" 代理账号不存在
"Error, money type wrong" money参数不是一个数字
"Error, money less than 0" money参数小于0
"""

def admin_proxy_account_balance_setup(request): #已测试1
    if request.method == "POST":
        return dump_and_response("Error, bad request method POST")
    admin_code = request.GET['admin_code']
    if not admin_code_check(admin_code):
        return dump_and_response("Error, admin code wrong")
    proxy_username = request.GET['proxy_username']
    money = request.GET['money']
    try:
        money = int(money)
    except ValueError:
        return dump_and_response("Error, money type wrong")
    if money < 0:
        return dump_and_response("Error, money less than 0")
    user = get_proxy_account(username=proxy_username)
    if user:
        user[1].balance = money
        user[1].save()
        return dump_and_response(["Success",user[1].balance])
    else:
        return dump_and_response("Proxy account not existed")

"""
代理金额查询 (管理员及代理可用，不需要管理员代码）
url:http://127.0.0.1:8000/api/proxy_account_balance_check/?proxy_username=Kong5

参数：
proxy_username 代理账号
返回值：
"30" 正确返回则返回目前余额(字符串）
"Error,bad request method POST" 错误的请求模式
"Proxy account not existed" 代理账号不存在

"""
def proxy_account_balance_check(request): #已测试1
    if request.method == "POST":
        return dump_and_response("Error, bad request method POST")
    proxy_username = request.GET['proxy_username']
    user = get_proxy_account(username=proxy_username)
    if user:
        return dump_and_response(str(user[1].balance))
    else:
        return dump_and_response("Proxy account not existed")

"""
管理员用——修改代理账号密码
url:http://127.0.0.1:8000/api/admin_proxy_account_change_password/?proxy_username=Kong&admin_code=tedttest&proxy_new_password=MyNewPassword
参数：
admin_code 管理员代码
proxy_username 代理账号
proxy_new_password 新密码
返回值：
"success" 代表修改成功
"Error,admin code wrong!" 管理员密链错误
"Error, account is Not exsited" 如果账户不存在则返回此警告
"Error,bad request method POST" 错误的请求模式
"""

def admin_proxy_account_change_password(request): #测试1
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    admin_code = request.GET["admin_code"]
    if not admin_code_check(admin_code):
        return dump_and_response("Error,admin code wrong!")
    username = request.GET["proxy_username"]
    new_password = request.GET["proxy_new_password"]
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        return dump_and_response("success")
    except User.DoesNotExist:
        return dump_and_response("Error, account is Not exsited")


"""
管理员设置软件
url:http://127.0.0.1:8000/api/admin_set_software/?admin_code=testtest&software_id=1&software_name=%E6%B5%8B%E8%AF%95%E8%BD%AF%E4%BB%B6&software_each_time=720&software_cost=10

参数：
admin_code 管理员密链
software_id 软件id（必须是唯一！）
software_name 软件名字
software_version_number 软件版本号（选填，不填写就默认为V1.0)
software_each_time 套餐时间
software_cost 套餐价格

返回值：
"success" 成功创建
"software_id already excited" 软件ID已经存在，请换一个ID
"Error,admin code wrong!" 管理员密链错误
"Error,bad request method POST" 错误的请求模式
"""
def admin_set_software(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    admin_code = request.GET["admin_code"]
    if not admin_code_check(admin_code):
        return dump_and_response("Error,admin code wrong!")
    software_id = request.GET['software_id']
    software_name = request.GET['software_name']
    try:
        software_version_number = request.GET['software_version_number']
    except:
        software_version_number = "V1.0"
    software_each_time = request.GET['software_each_time']
    software_cost = request.GET['software_cost']
    try:
        test = Software.objects.get(software_id=software_id)
        return dump_and_response("software_id already excited")
    except Software.DoesNotExist:
        software = Software.objects.create(software_id=int(software_id),software_name=software_name,
                                           software_version_number=software_version_number,
                                           software_each_time=int(software_each_time),software_cost=int(software_cost))
        software.save()
        return dump_and_response("success")

"""
获取所有软件信息
url:http://127.0.0.1:8000/api/get_all_software/

参数:
无
返回值：
[[1, "\u6d4b\u8bd5\u8f6f\u4ef6", "V1.1", 720, 10, false], [2, "\u6d4b\u8bd5\u8f6f\u4ef62", "V1.0", 720, 10, false], [3, "\u6d4b\u8bd5\u8f6f\u4ef63", "V1.2", 720, 10, false], [4, "\u6d4b\u8bd5\u8f6f\u4ef64", "BetaV0.3", 720, 1, true]]
[[软件id,软件名,软件版本号,套餐时间,套餐价格,是否试用],[软件id,软件名,软件版本号,套餐时间,套餐价格,是否试用]]



"""
def get_all_software(request):
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    all_software = Software.objects.all()
    all_software_list = []
    for i in all_software:
        a = [i.software_id,i.software_name,i.software_version_number,i.software_each_time,i.software_cost,i.software_try]
        all_software_list.append(a)

    return dump_and_response(all_software_list)




"""
管理员更新软件版本号
url: http://127.0.0.1:8000/api/admin_update_software_version/?admin_code=testtest&software_id=1&software_version_number=V1.1

参数：
admin_code 管理员密链
software_id 软件ID
software_version_number 新版本号
返回值：
"success" 成功修改
"software_id do not excited" 软件不存在或软件ID错误
"Error,admin code wrong!" 管理员密链错误
"Error,bad request method POST" 错误的请求模式
"""

def admin_update_software_version(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    admin_code = request.GET["admin_code"]
    if not admin_code_check(admin_code):
        return dump_and_response("Error,admin code wrong!")
    software_id = request.GET['software_id']
    software_version_number = request.GET['software_version_number']
    try:
        software = Software.objects.get(software_id=software_id)
    except Software.DoesNotExist:
        return dump_and_response("software_id do not excited")
    software.software_version_number = str(software_version_number)
    software.save()
    return dump_and_response("success")

"""
管理员更新软件套餐价格
url:http://127.0.0.1:8000/api/admin_update_software_cost/?admin_code=testtest&software_id=1&software_each_time=721&software_cost=5

参数：
admin_code 管理员密链
software_id 软件ID
software_each_time 套餐时间
software_cost 套餐价格
返回值：
"success" 设置成功
"software_id do not excited" 软件不存在或软件ID错误
"Error,admin code wrong!" 管理员密链错误
"Error,bad request method POST" 错误的请求模式
"""

def admin_update_software_cost(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    admin_code = request.GET["admin_code"]
    if not admin_code_check(admin_code):
        return dump_and_response("Error,admin code wrong!")
    software_id = request.GET['software_id']
    try:
        software = Software.objects.get(software_id=software_id)
    except Software.DoesNotExist:
        return dump_and_response("software_id do not excited")
    software_each_time = request.GET['software_each_time']
    software_cost = request.GET['software_cost']
    software.software_each_time = software_each_time
    software.software_cost = software_cost
    return dump_and_response("success")






"""
以下为代理可用API
"""

"""
代理登陆
代理登陆后会返回一个TOKEN(密链）,代理的其他操作API都需要此密链，
每次调用一次登陆函数就会重新定义并返回一次密链，所以具有时效性
url:http://127.0.0.1:8000/api/proxy_account_login/?proxy_username=d&proxy_password=XXXXX

参数：
proxy_username 用户名
proxy_password 密码

返回值：
XXXXXXXXXXXX 如果成功，将返回15位数的特定密链（这里被称为token)
"Error, account is Not exsited or password is fail" 如果账号密码或账户不存在都返回此警告
"Error,bad request method POST" 错误的请求模式

"""

def proxy_account_login(request): #已测试1
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    username = request.GET["proxy_username"]
    password = request.GET["proxy_password"]
    user = authenticate(username=username,password=password)
    if user != None:
        if user.is_active:
            try:
                user_others_info = Others_info.objects.get(user=user)
                user_others_info.TOKEN = get_TOKEN(15)
                user_others_info.save()
                return dump_and_response(user_others_info.TOKEN)
            except Others_info.DoesNotExist:
                return dump_and_response("Error, account is Not exsited or password is fail")
        else:
            return dump_and_response("Error, account is Not exsited or password is fail")
    else:
        return dump_and_response("Error, account is Not exsited or password is fail")


"""
代理修改代理账户密码
参数：
proxy_username 用户名
proxy_password 密码
proxy_new_password 新的密码

返回值：
"success" 代表修改成功
"Error, account is Not exsited or password is fail" 如果账号密码或账户不存在都返回此警告
"Error,bad request method POST" 错误的请求模式
"""

def proxy_account_change_password(request): #已测试1
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    username = request.GET["proxy_username"]
    password = request.GET["proxy_password"]
    user = authenticate(username=username,password=password)
    if user != None:
        if user.is_active:
            new_password = request.GET["proxy_new_password"]
            user.set_password(new_password)
            user.save()
            return dump_and_response("success")
        else:
            return dump_and_response("Error, account is Not exsited or password is fail")
    else:
        return dump_and_response("Error, account is Not exsited or password is fail")


"""
代理设置广告
url: http://127.0.0.1:8000/api/proxy_account_ad_change/?token=d6t7rd8l0j0z4p1&ad=testtest
参数：
token 代理客户login函数成功后返回的密链，每个账号都有一个独立的密链，并且每次登陆后都会返回一个新的密链
ad 需要设置的广告（15字以内）
返回值：
"success" 修改成功
"Error, account is Not exsited or token is fail" 如果token错误或账户不存在都返回此警告
"Error,bad request method POST" 错误的请求模式
"""
def proxy_account_ad_change(request): #已测试1
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    token = request.GET['token']
    ad = request.GET['ad']
    user = get_proxy_account(TOKEN=token)
    if not user:
        return dump_and_response("Error, account is Not exsited or token is fail")
    user[1].ad = ad
    user[1].save()
    return dump_and_response("success")



"""
请求代理全部信息
url:http://127.0.0.1:8000/api/proxy_info_get/?proxy_username=Kong5

参数：
proxy_username 用户名

返回值:
["name","ad","balance"] 成功返回会有以下几个数值，第一名字，第二广告，第三余额。
"Error, account is Not exsited" 如果账户不存在返回此警告
"Error,bad request method POST" 错误的请求模式
"""
def proxy_info_get(request):
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    username = request.GET['proxy_username']
    user = get_proxy_account(username=username)
    if not user:
        return dump_and_response("Error, account is Not exsited")
    ad = user[1].ad
    balance = user[1].balance
    return dump_and_response([str(username),str(ad),str(balance)])

"""
代理提卡
url:http://127.0.0.1:8000/api/proxy_get_software_code/?token=w5M3r4U6P7t8dU0&HowMuch=3&software_id=1

参数：
token 代理账户密链
software_id 软件ID
HowMuch 提多少张

返回值：
["n7o7I7M3I4", "r6X7D6O5g1", "c0Z4b3s6F7"] 如果成功，将返回一个列表
"Error, HowMuch lower than 0" 提卡数量小于或等于0
"Error, account is Not exsited or token is fail" 如果token错误或账户不存在都返回此警告
"Error,bad request method POST" 错误的请求模式
"software_id do not excited" 软件不存在或软件ID错误
["Balance not enough!","100"] 如果余额不足以提卡，就会返回第一个是提示，第二个是目前的余额
"""

def proxy_get_software_code(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    token = request.GET['token']
    user = get_proxy_account(TOKEN=token)
    if not user:
        return dump_and_response("Error, account is Not exsited or token is fail")
    howmuch = int(request.GET['HowMuch'])
    if howmuch <= 0:
        return dump_and_response("Error, HowMuch lower than 0")
    software_id = request.GET['software_id']
    try:
        software = Software.objects.get(software_id=software_id)
    except Software.DoesNotExist:
        return dump_and_response("software_id do not excited")
    count = int(user[1].balance) - (int(software.software_cost)*howmuch)
    if count < 0:
        return dump_and_response(["Balance not enough!",user[1].balance])
    code_list = []
    for i in range(howmuch):
        user[1].balance -= int(software.software_cost)
        user[1].save()
        code = get_Code(10)
        code_object = Time_code.objects.create(software=software,
                                        time=software.software_each_time,
                                        code=code,
                                        cost=software.software_cost,
                                        proxy_man=user[0],
                                        )
        code_object.save()
        code_list.append(code)

    return dump_and_response(code_list)


"""
创建授权（续费授权）
url:http://127.0.0.1:8000/api/authorization_make/?software_code=R4I0Z9r0h5&customer_QQ=123123&bot_QQ=123123

参数：
software_code 软件卡密
customer_QQ  客户QQ，用于保存修改机器人
bot_QQ 机器人QQ

返回值:
["success","2018-05-06 15:01:35"] 如果成功，第二个值会为到期时间
"Code Fail" 卡密错误
"Error,bad request method POST" 错误的请求模式
"Code already used" 卡密已经被使用过了
"""
def authorization_make(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    software_code = request.GET['software_code']
    try:
        code_object = Time_code.objects.get(code=software_code)
    except:
        return dump_and_response("Code Fail")
    if code_object.used == True:
        return dump_and_response("Code already used")
    customer_QQ = int(request.GET['customer_QQ'])
    software = code_object.software
    time_long = code_object.time
    try:
        authorization = Authorization.objects.get(software=software,customer_QQ=customer_QQ)
        if authorization.deadline_time < timezone.now():
            authorization.deadline_time = datetime.datetime.now()
            authorization.save()
        authorization.deadline_time = authorization.deadline_time + datetime.timedelta(hours=time_long)
        authorization.save()
        code_object.used = True
        code_object.save()
        return dump_and_response(["success",convert_timezone(authorization.deadline_time).strftime("%Y-%m-%d %H:%M:%S")])
    except Authorization.DoesNotExist: #如果授权不存在，新创立
        authorization = Authorization.objects.create(software=software,
                                                     customer_QQ=customer_QQ,
                                                     proxy_man=code_object.proxy_man,
                                                     bot_QQ=int(request.GET['bot_QQ']),
                                                     )
        authorization.save()
        authorization.deadline_time = authorization.deadline_time + datetime.timedelta(hours=time_long)
        authorization.save()
        code_object.used = True
        code_object.save()
        return dump_and_response(["success", convert_timezone(authorization.deadline_time).strftime("%Y-%m-%d %H:%M:%S")])

"""
授权查询
url:http://127.0.0.1:8000/api/authorization_check/?software_id=1&bot_QQ=123123

参数：
software_id 软件id
bot_QQ 机器人QQ

返回值：
["success","2018-05-06 15:01:35","测试广告"] 如果成功，第二个值会为到期时间，第三个是代理商的广告
"Fail" 已过期或不存在
"Error,bad request method POST" 错误的请求模式
"""
def authorization_check(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    software_id = request.GET['software_id']
    bot_QQ = request.GET['bot_QQ']
    try:
        authorization = Authorization.objects.get(software_id=software_id,bot_QQ=bot_QQ)
    except Authorization.DoesNotExist:
        return dump_and_response("Fail")
    if authorization.deadline_time < timezone.now():
        return dump_and_response('Fail')
    else:
        proxy_man_others_info = Others_info.objects.get(user=authorization.proxy_man)
        return dump_and_response(["success",convert_timezone(authorization.deadline_time).strftime("%Y-%m-%d %H:%M:%S"),proxy_man_others_info.ad])

"""
更换授权机器人QQ
url:http://127.0.0.1:8000/api/authorization_change/?software_id=1&new_bot_QQ=1414&customer_QQ=123123

参数：
software_id 软件id
new_bot_QQ 新机器人QQ
customer_QQ 客户QQ 

返回值：
["success","1414"] 如果修改成功，第二个返回目前的机器人QQ
"Error,bad request method POST" 错误的请求模式
"Fail" 授权不存在或过期
"""
def authorization_change(request): #已测试
    if request.method is "POST":
        return dump_and_response("Error, bad request method POST")
    software_id = request.GET['software_id']
    new_bot_QQ = request.GET['new_bot_QQ']
    customer_QQ = request.GET['customer_QQ']
    try:
        authorization = Authorization.objects.get(software_id=software_id,customer_QQ=customer_QQ)
    except Authorization.DoesNotExist:
        return dump_and_response("Fail")
    if authorization.deadline_time < timezone.now():
        return dump_and_response('Fail')
    authorization.bot_QQ = new_bot_QQ
    authorization.save()
    return dump_and_response(["success",authorization.bot_QQ])

