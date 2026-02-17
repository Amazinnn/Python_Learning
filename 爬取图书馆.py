from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import requests
from bs4 import BeautifulSoup
'''
# 1. 启动Chrome浏览器(无头模式）
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)  # 确保chromedriver在PATH中，或使用 executable_path 参数指定路径
driver.maximize_window()  # 最大化窗口，方便查看和定位
'''
driver = webdriver.Chrome()
driver.maximize_window()

# 2. 访问Z-Library首页
driver.get("https://zh.101isfj.ru/")

# 3. 等待页面主要元素加载完成（例如，等待“登录”按钮出现）
# 这里我们用显式等待，更稳定
try:
    # 等待页面标题包含“Z-Library”，证明首页基本加载完毕
    WebDriverWait(driver, 15).until(
        EC.title_contains("Z-Library")
    )
    print("✅ 页面加载成功。当前标题:", driver.title)
except Exception as e:
    print("❌ 页面加载失败或超时:", e)
    driver.quit()
    exit()

# 至此，浏览器已打开并停留在首页，与您手动操作时看到的一样。

# 4. 定位并点击“登录”按钮
try:
    # 方法A：使用更精确的CSS选择器，定位 data-action="login" 的元素
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-action="login"]'))
    )
    print('✅ 找到登录按钮。')

    # 方法B：如果上述失败，可以尝试通过链接文本（您文档中显示的‘登录’文字）
    # login_button = WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.LINK_TEXT, “登录”))
    # )

    login_button.click()
    print('✅ 已点击登录按钮，等待弹窗出现。')
    time.sleep(2)  # 等待弹窗动画加载
except Exception as e:
    print('❌ 找不到或无法点击登录按钮:', e)
    # 可以在这里截屏以帮助调试
    #driver.save_screenshot('debug_login_button.png')
    driver.quit()
    exit()

# 5. 等待登录弹窗出现，并定位其中的输入框
try:
    # 首先，需要找到弹窗的容器。根据【文档1】，弹窗可能是一个模态框(modal)。
    # 通常模态框会有特定的class或id。我们需要通过检查器确认，但可以先尝试通用方法。

    # 等待邮箱输入框出现。在您的【链接内容】中，弹窗内应有“电子邮件”或“邮箱”字段。
    # 我们通过 ‘input’ 元素的 type=’email’ 或 placeholder 文本来定位。
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='email'], input[placeholder *= 'mail'], input[placeholder *= '电子']"))
    )
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[type ="password"]')

    print("✅ 成功定位到登录表单输入框。")

    # 6. 清空并输入您的凭据 (请替换为您的实际邮箱和密码)
    your_email = "85985269@qq.com" # 请替换
    your_password = "ljg83849"  # 请替换

    email_input.clear()
    email_input.send_keys(your_email)

    password_input.clear()
    password_input.send_keys(your_password)

    print('✅ 凭据填写完毕。')

except Exception as e:
    print("❌ 找不到登录表单输入框:", e)
    driver.save_screenshot("debug_login_modal.png")
    # 也可以打印当前页面的HTML片段来辅助调试
    # print(driver.page_source[:2000])
    driver.quit()
    exit()

try:
    # 注意XPath字符串内的英文引号
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
                                    "//button[@type='submit'][@name='submit'][text()='登录']"))
    )
    submit_button.click()
    print("✅ 已经点击提交按钮，正在等待结果。")

    # 等待登录成功标志
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "我的图书馆"))
    )
    print("🎉 登录成功！正在导向登录后界面。")

except Exception as e:
    print("❌ Login process might have issues:", e)
    try:
        error_msg = driver.find_element(By.CSS_SELECTOR, ".error, .alert, [role='alert']").text
        print(f"Error message: {error_msg}")
    except:
        print("No clear error message found.")
    driver.save_screenshot("login_failed.png")

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-action="login"]'))
    )
    print('✅ 找到登录按钮。')

try:
    menu_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH,
            "//section[@class='navigation-element navigation-menu-element']/div[@class='navigation-icon']"))
    )
    menu_button.click()
    print("✅ 成功打开菜单。")
except Exception as e:
    print("菜单打开失败！")
    time.sleep(10)
    driver.quit()

try:
    popular_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='/popular']"))
    )
    popular_button.click()
    print("✅ 成功点击最受欢迎书籍榜单。")
except Exception as e:
    print("无法点击最受欢迎书籍榜单。")

try:
    WebDriverWait(driver, 10).until(
        EC.title_contains("最受欢迎")
    )
    print("✅ 成功打开最受欢迎书籍榜单。")
except Exception as e:
    print("无法打开最受欢迎书籍榜单。")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urljoin

# ... (前面的登录和导航代码保持不变，直到成功进入最受欢迎页面)

# 解析当前页面的HTML，提取书籍信息
print("📚 开始提取书籍信息...")

# 获取页面HTML源码
page_source = driver.page_source

# 使用BeautifulSoup解析
from bs4 import BeautifulSoup

soup = BeautifulSoup(page_source, 'html.parser')

# 查找所有书籍条目
book_items = soup.find_all('div', class_='item')

if not book_items:
    print("未找到书籍条目，请检查页面结构")
else:
    print(f"✅ 共找到 {len(book_items)} 本书籍")
    print("-" * 80)

    for i, item in enumerate(book_items, 1):
        try:
            # 提取链接
            link_tag = item.find('a')
            if link_tag and 'href' in link_tag.attrs:
                # 处理相对URL，拼接完整的URL
                book_url = link_tag['href']
                if not book_url.startswith(('http://', 'https://')):
                    book_url = urljoin("https://zh.101isfj.ru", book_url)
            else:
                book_url = "链接未找到"

            # 提取书籍信息
            cover_tag = item.find('z-cover')
            if cover_tag:
                title = cover_tag.get('title', '标题未找到')
                author = cover_tag.get('author', '作者未找到')
            else:
                # 尝试从img的alt属性提取
                img_tag = item.find('img')
                if img_tag and 'alt' in img_tag.attrs:
                    alt_text = img_tag['alt']
                    if '—' in alt_text:
                        author, title = alt_text.split('—', 1)
                    else:
                        author = "未知作者"
                        title = alt_text
                else:
                    title = "标题未找到"
                    author = "作者未找到"

            # 打印书籍信息
            print(f"{i:3d}. {title}")
            print(f"     作者: {author}")
            print(f"     链接: {book_url}")
            print()

        except Exception as e:
            print(f"第 {i} 本书籍解析出错: {e}")
            print()

print("-" * 80)
print(f"✅ 提取完成，共 {len(book_items)} 本书籍")

# 询问用户是否完成浏览
user_input = input("\n是否已完成浏览？(输入'是'或'yes'关闭浏览器，其他键继续): ").strip().lower()

while True:
    time.sleep(10)
    user_input = input("\n是否已完成浏览？(输入'是'或'yes'关闭浏览器，其他键继续): ").strip().lower()
    if user_input in ['是', 'yes', 'y','Y']:
        print("正在关闭浏览器...")
        break
    else:
        print("浏览器保持打开状态，您可以继续操作")

print("\n浏览器将在10秒内关闭……")
time.sleep(10)
driver.quit()
print("浏览器已经关闭。")


