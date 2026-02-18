from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import time
import re
from bs4 import BeautifulSoup

# 全局变量，用于跟踪下载限制状态
download_limit_reached = False


def setup_browser(headless=False):
    """设置浏览器驱动"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver


def wait_for_title(driver, title_part, timeout=15):
    """等待页面标题包含指定内容"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.title_contains(title_part)
        )
        print(f"✅ 页面加载成功。当前标题: {driver.title}")
        return True
    except Exception as e:
        print(f"❌ 页面加载失败或超时: {e}")
        return False


def login_to_zlibrary(driver, email, password):
    """登录Z-Library"""
    try:
        # 点击登录按钮
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-action="login"]'))
        )
        login_button.click()
        print('✅ 已点击登录按钮，等待弹窗出现。')
        time.sleep(2)

        # 填写登录信息
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='email'], input[placeholder*='mail'], input[placeholder*='电子']"))
        )
        password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')

        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        print('✅ 凭据填写完毕。')

        # 提交登录
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//button[@type='submit'][@name='submit'][text()='登录']"))
        )
        submit_button.click()
        print("✅ 已经点击提交按钮，正在等待结果。")

        # 等待登录成功
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "我的图书馆"))
        )
        print("🎉 登录成功！")
        return True

    except Exception as e:
        print(f"❌ 登录过程中出错: {e}")
        return False


def navigate_to_popular_books(driver):
    """导航到最受欢迎书籍榜单"""
    try:
        # 打开菜单
        time.sleep(3)
        menu_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//section[@class='navigation-element navigation-menu-element']/div[@class='navigation-icon']"))
        )
        menu_button.click()
        print("✅ 成功打开菜单。")

        # 点击最受欢迎
        popular_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/popular']"))
        )
        popular_button.click()
        print("✅ 成功点击最受欢迎书籍榜单。")

        # 验证跳转
        WebDriverWait(driver, 10).until(
            EC.title_contains("最受欢迎")
        )
        print("✅ 成功打开最受欢迎书籍榜单。")
        return True

    except Exception as e:
        print(f"❌ 导航到最受欢迎书籍榜单失败: {e}")
        return False


def extract_books_info(driver):
    """提取书籍列表信息"""
    print("📚 开始提取书籍信息...")

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    booklist = soup.find_all('z-cover', {"class": 'ready'})

    if not booklist:
        print("❌ 未找到书籍条目，请检查页面结构")
        return []

    print(f"✅ 共找到 {len(booklist)} 本书籍")
    print("-" * 80)

    books = []
    for i, book in enumerate(booklist, 1):
        try:
            book_data = {
                'title': book.get('title', '标题未找到'),
                'author': book.get('author', '作者未找到'),
                'isbn': book.get('isbn', ''),
                'id': book.get('id', '')
            }

            print(f"{i:3d}. {book_data['title']}")
            books.append(book_data)

        except Exception as e:
            print(f"第 {i} 本书籍解析出错: {e}")

    print("-" * 80)
    return books


def scroll_and_click_book(driver, book):
    """滚动到书籍位置并点击"""
    try:
        # 尝试使用id定位
        if book.get('id'):
            book_selector = f"z-cover[id='{book['id']}']"
        # 回退到使用isbn定位
        elif book.get('isbn'):
            book_selector = f"z-cover[isbn='{book['isbn']}']"
        # 最后使用title定位
        else:
            book_selector = f"z-cover[title='{book['title']}']"

        # 等待元素出现
        book_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, book_selector))
        )

        # 滚动到元素位置
        driver.execute_script("arguments[0].scrollIntoView();", book_element)
        time.sleep(0.5)

        # 点击书籍
        print(f"尝试点击《{book['title']}》")
        book_cover_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, book_selector))
        )
        book_cover_button.click()
        print(f"✅ 成功点击《{book['title']}》")
        return True

    except Exception as e:
        print(f"❌ 无法点击《{book['title']}》: {e}")
        return False


def verify_book_page(driver, book):
    """验证是否成功打开书籍页面"""
    try:
        WebDriverWait(driver, 5).until(
            EC.title_contains(f"{book['title']}")
        )
        print(f"✅ 成功打开《{book['title']}》的界面")
        return True
    except:
        # 尝试其他验证方法
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.book-title"))
            )
            print(f"✅ 成功打开书籍详情页")
            return True
        except Exception as e:
            print(f"❌ 无法打开《{book['title']}》的界面")
            return False


def check_download_limit(driver):
    """检查下载限额是否已用完"""
    global download_limit_reached

    try:
        # 检查是否有"每日限额已用完"的提示
        limit_elements = driver.find_elements(By.XPATH,
                                              "//*[contains(text(), '每日限额已用完') or contains(text(), '每日限额')]")

        # 检查特定的错误区域（根据HTML文档）
        error_sections = driver.find_elements(By.CSS_SELECTOR,
                                              ".download-limits-error, .download-limits-error__header, .download-limits-error__message")

        # 检查是否有具体的下载数量信息（如"20/20"）
        limit_texts = driver.find_elements(By.XPATH,
                                           "//*[contains(text(), '20/20') or contains(text(), '下载限制') or contains(text(), '下载额度')]")

        if limit_elements or error_sections or limit_texts:
            print("=" * 60)
            print("⚠️ 检测到下载限制提示：")
            print("   每日下载限额已用完！")
            print("=" * 60)

            # 提取更多限制信息
            try:
                limit_info = driver.find_element(By.CSS_SELECTOR, ".download-limits-error__message")
                if limit_info:
                    print(f"   限制详情: {limit_info.text[:100]}...")
            except:
                pass

            try:
                # 检查是否有具体的下载数量信息
                download_count = driver.find_element(By.XPATH, "//*[contains(text(), '20/20')]")
                if download_count:
                    print(f"   下载数量: {download_count.text}")
            except:
                pass

            download_limit_reached = True
            return True

        return False

    except Exception as e:
        print(f"检查下载限制时出错: {e}")
        return False


def download_largest_pdf(driver):
    """下载体积最大的PDF格式"""
    global download_limit_reached

    # 首先检查是否已经达到下载限额
    if download_limit_reached:
        print("❌ 下载限额已用完，跳过下载")
        return False

    print("开始查找PDF格式...")

    try:
        main_download_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.addDownloadedBook.btn.btn-default"))
        )

        # 获取主按钮的格式
        extension_element = main_download_button.find_element(By.CSS_SELECTOR, ".book-property__extension")
        extension = extension_element.text.strip().lower()
        print(f"主按钮格式: {extension}")

        # 获取主按钮的大小
        size_text = ""
        try:
            size_elements = main_download_button.find_elements(By.XPATH,
                                                               ".//*[contains(text(), 'KB') or contains(text(), 'MB')]")
            for elem in size_elements:
                if 'KB' in elem.text or 'MB' in elem.text:
                    size_text = elem.text
                    break
        except:
            pass

        if extension == 'pdf':
            print(f"主按钮是PDF格式，大小: {size_text}")

            # 下载前再次检查限额
            if check_download_limit(driver):
                print("❌ 下载过程中检测到限额已用完，停止下载")
                return False

            main_download_button.click()
            print("✅ 已开始下载PDF")
            return True
        else:
            print(f"主按钮不是PDF，是{extension.upper()}格式")

            # 点击下拉按钮查看其他格式
            try:
                dropdown_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "btnCheckOtherFormats"))
                )

                # 点击前检查限额
                if check_download_limit(driver):
                    print("❌ 下载前检测到限额已用完，停止操作")
                    return False

                dropdown_button.click()
                print("已点击下拉按钮")
                time.sleep(1)

                # 获取下拉菜单中的所有下载项
                download_items = driver.find_elements(By.CSS_SELECTOR, ".dropdown-menu a.addDownloadedBook")
                print(f"找到 {len(download_items)} 个下载选项")

                # 筛选PDF格式并比较大小
                pdf_items = []

                for item in download_items:
                    try:
                        ext_elem = item.find_element(By.CSS_SELECTOR, ".book-property__extension")
                        file_extension = ext_elem.text.strip().lower()

                        size_elem = item.find_element(By.CSS_SELECTOR, ".book-property__size")
                        size_text = size_elem.text.strip()

                        if file_extension == 'pdf':
                            # 将大小转换为KB
                            size_kb = convert_to_kb(size_text)
                            pdf_items.append({
                                'element': item,
                                'size_text': size_text,
                                'size_kb': size_kb,
                            })
                            print(f"找到PDF格式: {size_text}")
                    except:
                        continue

                if not pdf_items:
                    print("❌ 没有找到PDF格式")
                    return False

                # 找出体积最大的PDF
                largest_pdf = max(pdf_items, key=lambda x: x['size_kb'])
                print(f"最大PDF: {largest_pdf['size_text']}")

                # 下载前最后检查一次限额
                if check_download_limit(driver):
                    print("❌ 开始下载前检测到限额已用完，停止下载")
                    return False

                # 点击下载
                largest_pdf['element'].click()
                print(f"✅ 已开始下载最大PDF ({largest_pdf['size_text']})")
                return True

            except Exception as e:
                print(f"处理下拉菜单时出错: {e}")
                return False

    except Exception as e:
        print(f"检查主按钮时出错: {e}")
        return False


def process_book(driver, book):
    """处理单本书籍的完整流程"""
    global download_limit_reached

    # 检查是否已达到下载限额
    if download_limit_reached:
        print("⚠️ 下载限额已用完，停止处理新书籍")
        return "limit_reached"

    print(f"\n📖 正在处理《{book['title']}》")

    # 点击书籍进入详情页
    if not scroll_and_click_book(driver, book):
        return False

    # 验证是否成功进入书籍页面
    if not verify_book_page(driver, book):
        # 如果验证失败，尝试返回
        driver.back()
        time.sleep(2)
        return False

    # 检查下载限额（在开始下载前检查）
    if check_download_limit(driver):
        print(f"❌ 已达到每日下载限额，停止所有下载")
        print("=" * 60)
        print("   每日限额已用完，无法继续下载")
        print("   请等待次日重置或升级账户")
        print("=" * 60)
        return "limit_reached"

    # 尝试下载PDF
    download_success = download_largest_pdf(driver)

    if download_success:
        print(f"✅ 《{book['title']}》下载已开始")
        time.sleep(5)  # 等待下载开始，给浏览器一些时间处理下载
    else:
        print(f"❌ 《{book['title']}》下载失败或无法找到PDF")

    # 检查下载后是否达到限额
    if check_download_limit(driver):
        print(f"⚠️ 本次下载后已达到每日限额")
        return "limit_reached"

    # 返回书籍列表
    go_back_to_list(driver)
    time.sleep(2)  # 给页面加载一些时间

    return download_success


def convert_to_kb(size_str):
    """将文件大小字符串转换为KB"""
    if not size_str:
        return 0

    match = re.search(r'([\d.]+)\s*([KMG]?B)', size_str.upper())
    if not match:
        return 0

    value = float(match.group(1))
    unit = match.group(2)

    if unit == 'KB':
        return value
    elif unit == 'MB':
        return value * 1024
    elif unit == 'GB':
        return value * 1024 * 1024
    else:
        return value


def go_back_to_list(driver):
    """返回书籍列表页面"""
    try:
        # 尝试点击返回按钮
        book_quit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='page-title__back-arrow']"))
        )
        book_quit_button.click()
        print("✅ 成功点击返回键")

        # 验证返回成功
        WebDriverWait(driver, 5).until(
            EC.title_contains("最受欢迎")
        )
        print("✅ 成功返回最受欢迎书籍榜单。")
        return True

    except Exception as e:
        print(f"❌ 无法点击返回键，尝试使用浏览器返回: {e}")
        try:
            driver.back()
            time.sleep(3)

            # 验证是否返回成功
            if "最受欢迎" in driver.title or "popular" in driver.current_url:
                print("✅ 使用浏览器返回成功")
                return True
            else:
                # 如果返回失败，直接导航到最受欢迎页面
                driver.get("https://zh.101isfj.ru/popular")
                time.sleep(3)
                print("✅ 直接导航到最受欢迎页面")
                return True
        except Exception as e2:
            print(f"❌ 返回书籍列表失败: {e2}")
            return False


def handle_download_limit(driver):
    """处理下载限额达到的情况"""
    print("\n" + "=" * 60)
    print("⚠️ 检测到下载限额已达到！")
    print("=" * 60)
    print("   每日下载量：普通账户20/20已用完")
    print("   您可以：")
    print("   1. 等待次日限额重置")
    print("   2. 捐款或升级Premium账户提高限额")
    print("=" * 60)

    # 询问用户是否继续等待
    user_input = input("\n是否等待当前下载完成？(输入'是'等待，其他键立即退出): ").strip().lower()

    if user_input in ['是', 'yes', 'y']:
        print("等待下载完成...")
        wait_time = 30  # 等待30秒让当前下载完成
        print(f"等待 {wait_time} 秒...")
        for i in range(wait_time, 0, -1):
            print(f"剩余等待时间: {i}秒", end='\r')
            time.sleep(1)
        print("\n等待完成")
        return True
    else:
        print("立即停止程序...")
        return False


def main():
    """主函数"""
    global download_limit_reached

    # 设置浏览器
    driver = setup_browser(headless=False)

    try:
        # 访问首页
        driver.get("https://zh.101isfj.ru/")

        # 等待页面加载
        if not wait_for_title(driver, "Z-Library"):
            return

        # 登录
        if not login_to_zlibrary(driver, "85985269@qq.com", "ljg83849"):
            print("❌ 登录失败，程序退出")
            return

        # 导航到最受欢迎书籍
        if not navigate_to_popular_books(driver):
            print("❌ 导航失败，程序退出")
            return

        # 提取书籍信息
        books = extract_books_info(driver)

        if not books:
            print("❌ 没有找到书籍，程序退出")
            return

        print(f"\n开始处理书籍，最多处理 {min(10, len(books))} 本书籍")

        # 处理每本书籍
        for i, book in enumerate(books[:10]):  # 只处理前10本，避免无限循环
            print(f"\n{'=' * 60}")
            print(f"第 {i + 1} 本书籍 / 共 {min(10, len(books))} 本")

            result = process_book(driver, book)

            # 检查是否达到下载限额
            if result == "limit_reached":
                print("⚠️ 检测到下载限额已用完，停止处理后续书籍")
                download_limit_reached = True

                # 处理下载限额情况
                handle_download_limit(driver)
                break

            elif result:
                print(f"✅ 《{book['title']}》处理成功")
            else:
                print(f"❌ 《{book['title']}》处理失败，继续下一本")

            # 添加短暂延迟，避免请求过快
            time.sleep(1)

        if download_limit_reached:
            print("\n📊 下载总结:")
            print(f"   成功处理 {i} 本书籍")
            print(f"   因下载限额已满而停止")
        else:
            print(f"\n🎉 书籍处理完成，共处理了 {min(10, len(books))} 本书籍")

    except Exception as e:
        print(f"❌ 程序执行过程中出错: {e}")

    finally:
        # 询问用户是否关闭浏览器
        if not download_limit_reached:
            user_input = input("\n是否已完成浏览？(输入'是'或'yes'关闭浏览器，其他键继续): ").strip().lower()

            if user_input in ['是', 'yes', 'y']:
                print("正在关闭浏览器...")
                driver.quit()
                print("浏览器已经关闭。")
            else:
                print("浏览器保持打开状态，您可以继续操作")
        else:
            # 如果达到下载限额，等待几秒后自动关闭
            print("\n程序将在10秒后自动关闭...")
            time.sleep(10)
            driver.quit()
            print("浏览器已关闭。")


if __name__ == "__main__":
    main()