##################################################################################################################
# 淘宝抢购脚本                                                                                                   #
# 使用方法：                                                                                                     #
#     1、先将需要抢购的商品放到购物车中（注意购物车中只能放需要抢购的东西，到时抢购的时候会全部提交）；          #
#     2、修改下本脚本中的BUY_TIME值，设定为需要抢购的时间；                                                      #
#     3、执行此脚本，然后等待浏览器打开弹出登陆界面，手机淘宝扫描登陆；                                          #
#     4、脚本开始执行后，会定时刷新防止超时退出，到了设定时间点会自动尝试提交订单；                              #
#     5、抢购时为了防止一次网络拥堵出问题，设置了尝试机制，会不停尝试提交订单，直到提交成功或达到最大重试次数为止#
#     6、脚本只负责提交订单，之后24小时内需要自行完成付款操作。                                                  #
##################################################################################################################

from selenium import webdriver
from selenium.webdriver.safari.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import time

# ==== 设定抢购时间 （修改此处，指定抢购时间点）====
BUY_TIME = "2020-05-01 20:00:00"

buy_time_object = datetime.datetime.strptime(BUY_TIME, '%Y-%m-%d %H:%M:%S')

now_time = datetime.datetime.now()
if now_time > buy_time_object:
    print("当前已过抢购时间，请确认抢购时间是否填错...")
    exit(0)

print("正在打开Safari浏览器...")
# 让浏览器不要显示当前受自动化测试工具控制的提醒
driver: WebDriver = webdriver.Safari()
driver.maximize_window()
print("Safari浏览器已经打开...")


def __login_operates():
    driver.get("https://www.taobao.com")
    try:
        WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.LINK_TEXT, "亲，请登录")))
        driver.find_element_by_link_text("亲，请登录").click()

        WebDriverWait(driver, 100, 0.0001).until(EC.url_matches("https://login.taobao.com"))
        WebDriverWait(driver, 10, 0.1).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[3]/div/div[1]/div/div[1]/i")))
        driver.find_element_by_xpath("/html/body/div/div[2]/div[3]/div/div[1]/div/div[1]/i").click()
        print("请使用手机淘宝扫描屏幕上的二维码进行登录...")
    except:
        print("登陆超时")
        return


def login():
    print("开始尝试登录...")
    __login_operates()

    WebDriverWait(driver, 100, 0.0001).until(EC.url_matches("https://www.taobao.com"))

    # time.sleep(3)
    now = datetime.datetime.now()
    print('login success:', now.strftime('%Y-%m-%d %H:%M:%S'))


def __refresh_keep_alive():
    # 重新加载购物车页面，定时操作，防止长时间不操作退出登录
    driver.get("https://cart.taobao.com/cart.htm")
    # print("刷新购物车界面，防止登录超时...")
    time.sleep(10)


def keep_login_and_wait():
    driver.get("https://cart.taobao.com/cart.htm")
    # print("当前距离抢购时间点还有较长时间，开始定时刷新防止登录超时...")
    while True:
        currentTime = datetime.datetime.now()
        if (buy_time_object - currentTime).seconds > 120:
            __refresh_keep_alive()
        else:
            print("抢购时间点将近，停止自动刷新，准备进入抢购阶段...")
            break


def buy():
    # 打开购物车
    # WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.ID, "J_SelectAll1")))
    # driver.find_element_by_id("J_SelectAll1").click()
    WebDriverWait(driver, 10, 0.0001).until(EC.url_matches("https://cart.taobao.com/"))
    WebDriverWait(driver, 1000, 0.1).until(EC.presence_of_element_located((By.ID, "J_SelectAll1")))
    driver.find_element_by_id("J_SelectAll1").click()
    submit_succ = False
    retry_submit_times = 0
    while True:
        now = datetime.datetime.now()
        if now >= buy_time_object:
            retry_submit_times = retry_submit_times + 1
            if submit_succ or (retry_submit_times > 6):
                print("订单已经提交成功，无需继续抢购...")
                return
            try:
                # 点击结算按钮
                WebDriverWait(driver, 100, 0.00001).until(EC.presence_of_element_located((By.ID, "J_Go")))
                driver.find_element_by_id("J_Go").click()
                print("已经点击结算按钮...")
                while True:
                    WebDriverWait(driver, 10, 0.00001).until(EC.url_matches("https://buy"))
                    WebDriverWait(driver, 10, 0.00001).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "提交")))
                    driver.find_element_by_partial_link_text('提交').click()
                    # __buy_error_code
                    if 'https://cashierem14.alipay.com/' in driver.current_url:
                        submit_succ = True
                        pass
                    else:
                        WebDriverWait(driver, 10, 0.00001).until(EC.url_matches("__buy_error_code"))
                        driver.back()
            except Exception as e:
                if 'https://cashierem14.alipay.com/' in driver.current_url:
                    print("提交订单成功")
                    return
                print("不好，挂了，提交订单失败了...")
                toCart()
                # time.sleep(5)
        time.sleep(0.000001)


def toCart():
    driver.get("https://cart.taobao.com/")
    WebDriverWait(driver, 10, 0.0001).until(EC.url_matches("https://cart.taobao.com/"))
    WebDriverWait(driver, 10, 0.0001).until(EC.presence_of_element_located((By.ID, "J_SelectAll1")))
    driver.find_element_by_id("J_SelectAll1").click()


login()
keep_login_and_wait()
buy()
if __name__ == '__main__':
    pass
