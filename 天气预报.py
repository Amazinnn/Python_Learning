import re
from bs4 import BeautifulSoup
import requests

# 常用城市名到城市编号的映射字典
CITY_CODE_MAP = {
    "北京": "54511",    # 北京
    "上海": "58362",    # 上海
    "广州": "59287",    # 广州
    "深圳": "59493",    # 深圳
    "杭州": "58457",    # 杭州
    "南京": "58238",    # 南京
    "成都": "56294",    # 成都
    "武汉": "57494",    # 武汉
    "西安": "57036",    # 西安
    "天津": "54527",    # 天津
    "重庆": "57516",    # 重庆
    "沈阳": "54342",    # 沈阳
    "大连": "54662",    # 大连
    "青岛": "54857",    # 青岛
    "厦门": "59134",    # 厦门
    "苏州": "58354",    # 苏州
    "宁波": "58562",    # 宁波
    "郑州": "57083",    # 郑州
    "长沙": "57687",    # 长沙
    "合肥": "58321",    # 合肥
    "福州": "58847",    # 福州
    "昆明": "56778",    # 昆明
    "贵阳": "57816",    # 贵阳
    "石家庄": "53698",   # 石家庄
    "哈尔滨": "50953",   # 哈尔滨
    "长春": "54161",    # 长春
    "济南": "54823",    # 济南
    "太原": "53772",    # 太原
    "南昌": "58606",    # 南昌
    "南宁": "59431",    # 南宁
    "海口": "59758",    # 海口
    "兰州": "52889",    # 兰州
    "西宁": "52866",    # 西宁
    "银川": "53614",    # 银川
    "乌鲁木齐": "51463", # 乌鲁木齐
    "拉萨": "55591",    # 拉萨
    "呼和浩特": "53463", # 呼和浩特
}

print("Welcome to use this weather forecast programme!")
while True:
    # 获取用户输入的城市名
    city_name = input("Please enter the city name in Chinese: ")

    # 检查城市是否在映射表中
    if city_name not in CITY_CODE_MAP:
        print(f"Sorry,we do not have the information of '{city_name}'.")
        print(f"Cities whose information are available：")
        for key, value in CITY_CODE_MAP.items():
            print(f"{key}: {value}")
    else:
        # 获取城市编号
        city_code = CITY_CODE_MAP[city_name]

        # 构造目标URL - weather.cma.cn 城市页面的URL格式通常是这样的
        # 注意：实际URL格式可能需要根据网站结构调整
        url = f"https://weather.cma.cn/web/weather/{city_code}.html"

        print(f"Searching for {city_name}'s weather information...")

        response = requests.get(url)

        if response.status_code == 200 and response.url == url :
            print("Your query is working.")
            print(f"URL of targeted city: {response.url}")

            soup = BeautifulSoup(response.content, "lxml")

            # 尝试查找今天的天气
            weather_today = soup.find("div", {"class": "pull-left day actived"})
            if weather_today:
                print("\nToday's weather Information:")
                try:
                    date_match = re.findall(r"[0-9]{2}/[0-9]{2}", weather_today.text)
                    if date_match:
                        print("Date:", date_match[0])
                    else:
                        print("Date missing.")
                except:
                    print("Date:Fail to analyze.")

                high_temp = weather_today.find('div', {'class': 'high'})
                if high_temp:
                    print("Highest temperature:", re.sub(r'\s+', '', high_temp.text))
                else:
                    print("Highest temperature is not available.")

                low_temp = weather_today.find('div', {'class': 'low'})
                if low_temp:
                    print("Lowest temperature::", re.sub(r'\s+', '', low_temp.text))
                else:
                    print("Lowest temperature is not available.")
            else:
                print("Information of today's weather is not available.")

            # 尝试查找未来天气
            print("\nFuture weather information:")
            weather_future = soup.find_all("div", {"class": "pull-left day"})

            if weather_future:
                for item in weather_future:
                    try:
                        date_match = re.findall(r"[0-9]{2}/[0-9]{2}", item.text)
                        date = date_match[0] if date_match else "Date missing."
                    except:
                        date = "Date missing."

                    high_temp = item.find('div', {'class': 'high'})
                    high = re.sub(r'\s+', '', high_temp.text) if high_temp else "未知"

                    low_temp = item.find('div', {'class': 'low'})
                    low = re.sub(r'\s+', '', low_temp.text) if low_temp else "未知"

                    print(f"Date: {date}  Highest Temperature: {high}  Lowest Temperature: {low}")
            else:
                print("Information of future weather is not available.")
        else:
            print("您的查询失败。")
            print("状态码:", response.status_code)
    if input("Do you want to restart your query process? (y/n):") == 'n':
        break