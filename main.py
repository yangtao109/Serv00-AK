import os
import re
import json
import time
import string
import random
import ddddocr
import inspect
import asyncio
import requests
from telegram import Bot
from loguru import logger
from datetime import datetime
from urllib.parse import quote
from requests.exceptions import JSONDecodeError
os.makedirs("static", exist_ok=True)
cache = {}
global input_token, input_chatid
config_file = 'static/config.json'
def get_input_prompt():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.') + str(datetime.now().microsecond // 1000).zfill(3)
    frame = inspect.stack()[1]
    module_name = inspect.getmodule(frame[0]).__name__
    module_info = f'{module_name}:<module>'
    caller_line = frame.lineno
    return f'\033[32m{current_time}\033[0m | \033[1;94mINPUT\033[0m    | \033[36m{module_info}:{caller_line}\033[0m - '
async def send_message(message):
    global input_token, input_chatid
    bot = Bot(token=input_token)
    try:
        await bot.send_message(chat_id=input_chatid, text=message)
    except Exception as e:
        logger.error(f"发送失败: {e}")
def get_user_name():
    url = "https://www.ivtool.com/random-name-generater/uinames/api/index.php?region=united%20states&gender=male&amount=5&="
    resp = requests.get(url, verify=False)
    if resp.status_code != 200:
        print(resp.status_code, resp.text)
        raise Exception("获取名字出错")
    data = resp.json()
    return data
def generate_random_username():
    length = random.randint(7, 10)
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
def start_userconfig():
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if config: return config['token'], config['chatid']
        except (json.JSONDecodeError, IOError):
            pass
        input_token = input(f"{get_input_prompt()}\033[1;94m请输入Telegram Bot Token [默认使用 @Serv00Reg_Bot]:\033[0m")
        if input_token == "": input_token = '7594103635:AAEoQKB_ApJgDbfoVJm-gwW6e0VVS_a5Dl4'
        input_chatid = get_valid_input("\033[1;94m请输入Telegram Chat ID:\033[0m", lambda x: x.isdigit() and int(x) > 0, "无效的ChatID,请输入一个正整数.")
    with open(config_file, 'w') as f:
        json.dump({'token': input_token.strip(), 'chatid': input_chatid.strip()}, f)
    return input_token, input_chatid
def get_valid_input(prompt, validation_func, error_msg):
    while True:
        user_input = input(f"{get_input_prompt()}{prompt}")
        if validation_func(user_input):
            return user_input
        logger.error(f"\033[1;93m{error_msg}\033[0m")
def start_task(input_email: str):
    id_retry = 1
    while True:
        try:
            User_Agent = ''.join(random.choices(string.digits, k=24))
            Cookie = "csrftoken={}"
            url1 = "https://www.serv00.com/offer/create_new_account"
            headers = {f"User-Agent": User_Agent}
            captcha_url = "https://www.serv00.com/captcha/image/{}/"
            header2 = {"Cookie": Cookie, "User-Agent": User_Agent}
            url3 = "https://www.serv00.com/offer/create_new_account.json"
            header3 = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": "https://www.serv00.com/offer/create_new_account",
                "Cookie": Cookie,
                "User-Agent": User_Agent
            }
            email = input_email
            usernames = get_user_name()
            _ = usernames.pop()
            first_name = _["name"]
            last_name = _["surname"]
            username = generate_random_username().lower()
            print(""), logger.info(f"{email} {first_name} {last_name} {username}")
            with requests.Session() as session:
                logger.info(f"获取网页信息 - 尝试次数: \033[1;94m{id_retry}\033[0m.")
                resp = session.get(url=url1, headers=headers, verify=False)
                headers = resp.headers
                content = resp.text
                csrftoken = re.findall(r"csrftoken=(\w+);", headers.get("set-cookie"))[0]
                header2["Cookie"] = header2["Cookie"].format(csrftoken)
                header3["Cookie"] = header3["Cookie"].format(csrftoken)
                captcha_0 = re.findall(r'id=\"id_captcha_0\" name=\"captcha_0\" value=\"(\w+)\">', content)[0]
                captcha_retry = 1
                while True:
                    time.sleep(random.uniform(0.5, 1.2))
                    logger.info("获取验证码")
                    resp = session.get(url=captcha_url.format(captcha_0), headers=dict(header2, **{"Cookie": header2["Cookie"].format(csrftoken)}), verify=False)
                    content = resp.content
                    with open("static/image.jpg", "wb") as f:
                        f.write(content)
                    captcha_1 = ddddocr.DdddOcr(show_ad=False).classification(content).upper()
                    if bool(re.match(r'^[a-zA-Z0-9]{4}$', captcha_1)):
                        logger.info(f"识别验证码成功: \033[1;92m{captcha_1}\033[0m")
                    else:
                        logger.warning("\033[7m验证码识别失败,正在重试...\033[0m")
                        captcha_retry += 1
                        if captcha_retry > 200: # 此处修改重试次数，默认200次.
                            logger.error("验证码识别失败次数过多,退出重试.")
                            return
                        continue
                    data = f"csrfmiddlewaretoken={csrftoken}&first_name={first_name}&last_name={last_name}&username={username}&email={quote(email)}&captcha_0={captcha_0}&captcha_1={captcha_1}&question=free&tos=on"
                    time.sleep(random.uniform(0.5, 1.2))
                    logger.info("请求信息")
                    resp = session.post(url=url3, headers=dict(header3, **{"Cookie": header3["Cookie"].format(csrftoken)}), data=data, verify=False)
                    logger.info(f'请求状态码: \033[1;93m{resp.status_code}\033[0m')
                    try:
                        content = resp.json()
                        if resp.status_code == 200 and len(content.keys()) == 2:
                            logger.success(f"\033[1;92m🎉 账户 {username} 已成功创建!\033[0m")
                            asyncio.run(send_message(f"Success!\nEmail: {input_email}\nUserName: {username}"))
                            return
                        else:
                            first_key = next(key for key in content if key not in ['__captcha_key', '__captcha_image_src'])
                            first_content = re.search(r"\['(.+?)'\]", str(content[first_key])).group(1)
                            logger.info(f"\033[36m{first_key.capitalize()}: {first_content}\033[0m")
                            if first_content == "An account has already been registered to this e-mail address.":
                                logger.warning(f"\033[1;92m该邮箱已存在,或账户 {username} 已成功创建🎉!")
                                asyncio.run(send_message(f"Success!\nEmail: {input_email}\nUserName: {username}"))
                                return
                    except JSONDecodeError:
                        logger.error("\033[7m获取信息错误,正在重试...\033[0m")
                        time.sleep(random.uniform(0.5, 1.2))
                        continue
                    if content.get("captcha") and content["captcha"][0] == "Invalid CAPTCHA":
                        captcha_0 = content["__captcha_key"]
                        logger.warning("\033[7m验证码错误,正在重新获取...\033[0m")
                        time.sleep(random.uniform(0.5, 1.2))
                        continue
                    if content.get("username") and content["username"][0] == "Maintenance time. Try again later.":
                        id_retry += 1
                        logger.error("\033[7m系统维护中,正在重试...\033[0m")
                        time.sleep(random.uniform(0.5, 1.2))
                        break
                    if content.get("email") and content["email"][0] == "Enter a valid email address.":
                        logger.error("\033[7m无效的邮箱,请重新输入.\033[0m")
                        asyncio.run(send_message(f"{input_email} 无效的邮箱,请重新输入."))
                        time.sleep(random.uniform(0.5, 1.2))
                        return
                    else:
                        asyncio.run(send_message(f"Success!\nEmail: {input_email}\nUserName: {username}"))
                        return
        except Exception as e:
            logger.error(f"\033[7m发生异常:{e},正在重新开始任务...\033[0m")
            time.sleep(random.uniform(0.5, 1.2))
        if input_email in cache:
            del cache[input_email]
if __name__ == "__main__":
    First_Run = True
    while True:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                input_token, input_chatid = config['token'], config['chatid']
                break
        except (FileNotFoundError, json.JSONDecodeError):
            if First_Run: logger.error("\033[1;92m初始化运行未检测到配置文件.\033[0m"); First_Run = False
            input_token, input_chatid = start_userconfig()
os.system("cls" if os.name == "nt" else "clear")
response = requests.get('https://ping0.cc/geo', verify=False)
print(f"=============================\n\033[96m{response.text[:200]}\033[0m=============================")
logger.info("\033[91m输入邮箱开始自动任务,退出快捷键Ctrl+C.\033[0m")
while True:
    input_email = get_valid_input("\033[1;94m请输入邮箱:\033[0m", lambda x: '@' in x, "无效的邮箱,请重新输入.")
    if '@' not in input_email:
        logger.error("\033[1;93m无效的邮箱,请重新输入.\033[0m")
        continue
    start_task(input_email)
