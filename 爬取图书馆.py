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

    books = []
    for i, book in enumerate(booklist, 1):
        try:
            # 提取书名，并处理可能的引号问题
            raw_title = book.get('title', '标题未找到')
            # 移除书名中的特殊引号，只保留基本字符
            clean_title = raw_title.replace('"', '').replace("'", "").strip()

            book_data = {
                'index': i,
                'title': clean_title,  # 清理后的书名
                'raw_title': raw_title,  # 原始书名
                'author': book.get('author', '作者未找到'),
                'isbn': book.get('isbn', ''),
                'id': book.get('id', '')
            }
            books.append(book_data)
        except Exception as e:
            print(f"第 {i} 本书籍解析出错: {e}")

    return books


def display_all_books(books, start_index=1, books_per_page=100):
    """显示所有书籍列表，可以选择从第几本开始显示"""
    total_books = len(books)

    if not books:
        print("❌ 没有书籍可显示")
        return

    # 计算实际开始索引（确保不超出范围）
    actual_start = max(1, min(start_index, total_books))

    print(f"\n📚 书籍列表（第{actual_start}本开始，共{total_books}本）:")
    print("=" * 100)

    # 显示表头
    print(f"{'编号':<6} {'书名':<60} {'作者':<30}")
    print("-" * 100)

    # 计算结束索引
    end_index = min(actual_start + books_per_page - 1, total_books)

    # 显示指定范围内的书籍
    for i in range(actual_start - 1, end_index):
        book = books[i]
        # 截断过长的书名和作者名
        title = book['title'][:55] + "..." if len(book['title']) > 55 else book['title']
        author = book['author'][:25] + "..." if len(book['author']) > 25 else book['author']

        print(f"{book['index']:<6} {title:<60} {author:<30}")

    print("-" * 100)

    # 显示统计信息
    if end_index < total_books:
        print(f"显示第 {actual_start}-{end_index} 本书籍，还有 {total_books - end_index} 本书籍未显示")
    else:
        print(f"显示第 {actual_start}-{end_index} 本书籍，已显示所有书籍")

    return end_index


def get_download_mode():
    """获取用户选择的下载模式"""
    print("\n请选择下载模式：")
    print("1. 下载指定范围的书籍（例如：1-10）")
    print("2. 下载指定编号的书籍（例如：1,3,5,7）")
    print("3. 从指定编号开始一直下载到末尾")
    print("4. 返回书籍列表，重新选择起始编号")

    while True:
        mode = input("请输入模式编号（1/2/3/4）: ").strip()
        if mode in ['1', '2', '3', '4']:
            break
        print("❌ 输入错误，请输入1、2、3或4")

    return mode


def get_book_selections(books, mode, current_start_index=1):
    """根据模式获取选中的书籍列表"""
    total_books = len(books)

    if mode == '1':
        # 模式1：范围下载
        while True:
            try:
                range_input = input(f"请输入下载范围（格式：开始-结束，例如：1-{total_books}）: ").strip()
                start_str, end_str = range_input.split('-')
                start = int(start_str.strip())
                end = int(end_str.strip())

                if 1 <= start <= end <= total_books:
                    selected_indices = list(range(start, end + 1))
                    break
                else:
                    print(f"❌ 范围无效，请输入1到{total_books}之间的有效范围")
            except (ValueError, IndexError):
                print("❌ 格式错误，请输入正确的范围格式（例如：1-10）")

    elif mode == '2':
        # 模式2：指定编号下载
        while True:
            try:
                indices_input = input(f"请输入要下载的书籍编号（用逗号分隔，例如：1,3,5，范围：1-{total_books}）: ").strip()
                indices = [int(idx.strip()) for idx in indices_input.split(',')]

                valid = all(1 <= idx <= total_books for idx in indices)
                if valid and indices:
                    selected_indices = indices
                    break
                else:
                    print(f"❌ 编号无效，请输入1到{total_books}之间的有效编号")
            except ValueError:
                print("❌ 格式错误，请输入正确的编号格式（例如：1,3,5）")

    elif mode == '3':
        # 模式3：从指定编号开始下载
        while True:
            try:
                start = int(input(f"请输入开始下载的编号（范围：1-{total_books}）: ").strip())
                if 1 <= start <= total_books:
                    selected_indices = list(range(start, total_books + 1))
                    break
                else:
                    print(f"❌ 编号无效，请输入1到{total_books}之间的有效编号")
            except ValueError:
                print("❌ 格式错误，请输入数字")

    elif mode == '4':
        # 模式4：返回书籍列表
        return 'back_to_list'

    return selected_indices


def scroll_and_click_book(driver, book):
    """基于title属性滚动到书籍位置并点击"""
    try:
        # 获取书籍的清理后标题
        book_title = book['title']

        print(f"📖 正在查找书籍: 《{book_title}》")

        # 方法1：尝试通过title属性定位（最可靠）
        # 使用XPath的contains函数，处理标题中的特殊字符
        xpath_selector = f"//z-cover[contains(@title, \"{book_title[:20]}\")]"

        # 等待元素出现
        book_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_selector))
        )

        print(f"✅ 找到书籍元素")

        # 滚动到元素位置
        print(f"📏 滚动到书籍位置...")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", book_element)
        time.sleep(1)  # 等待滚动完成

        # 验证元素是否在视窗内
        is_displayed = book_element.is_displayed()
        is_enabled = book_element.is_enabled()
        print(f"🔍 元素状态: 显示={is_displayed}, 启用={is_enabled}")

        if not is_displayed or not is_enabled:
            print("⚠️ 元素不可见或不可点击，尝试备用方法")

        # 再次等待元素可点击
        book_clickable = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath_selector))
        )

        # 点击书籍
        print(f"🖱️ 尝试点击《{book_title}》...")
        book_clickable.click()
        print(f"✅ 成功点击《{book_title}》")
        return True

    except Exception as e:
        print(f"❌ 无法点击《{book['title']}》: {str(e)[:100]}")

        # 尝试备用方法：通过JavaScript点击
        try:
            print("🔄 尝试备用方法：JavaScript点击")
            driver.execute_script("arguments[0].click();", book_element)
            print(f"✅ 通过JavaScript成功点击《{book_title}》")
            return True
        except Exception as js_e:
            print(f"❌ JavaScript点击也失败: {str(js_e)[:100]}")
            return False


def verify_book_page(driver, book):
    """验证是否成功打开书籍页面（基于title属性）"""
    try:
        # 等待页面标题包含书籍标题的关键部分
        # 使用原始标题的前20个字符进行匹配
        title_part = book['title'][:20]

        # 方法1：等待页面标题包含书名
        print(f"🔍 验证页面标题是否包含: {title_part}...")
        WebDriverWait(driver, 8).until(
            EC.title_contains(title_part)
        )

        current_title = driver.title
        print(f"✅ 成功打开书籍详情页")
        print(f"📄 当前页面标题: {current_title}")
        return True

    except Exception as e:
        # 方法2：检查页面中是否有书籍标题
        print(f"⚠️ 页面标题验证失败，尝试其他验证方法")
        try:
            page_source = driver.page_source
            if book['title'][:20] in page_source:
                print(f"✅ 在页面内容中找到书籍标题")
                return True
        except:
            pass

        # 方法3：检查是否有特定的书籍详情元素
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.book-title"))
            )
            print(f"✅ 找到书籍标题元素")
            return True
        except:
            pass

        print(f"❌ 无法验证是否打开《{book['title']}》的界面")
        return False


def check_download_limit(driver):
    """检查下载限额是否已用完"""
    global download_limit_reached

    try:
        # 检查是否有"每日限额已用完"的提示
        limit_elements = driver.find_elements(By.XPATH,
                                              "//*[contains(text(), '每日限额已用完') or contains(text(), '每日限额')]")

        if limit_elements :
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


def process_book(driver, book, mode):
    """处理单本书籍的完整流程（优化版本）"""
    global download_limit_reached

    # 检查是否已达到下载限额
    if download_limit_reached:
        print("⚠️ 下载限额已用完，停止处理新书籍")
        return "limit_reached"

    print(f"\n📖 正在处理第{book['index']}本书: 《{book['title']}》")

    # 点击书籍进入详情页
    if not scroll_and_click_book(driver, book):
        print("❌ 点击书籍失败，跳过本书")
        # 尝试返回列表
        try:
            driver.back()
            time.sleep(2)
        except:
            pass
        return "skip"

    # 验证是否成功进入书籍页面
    if not verify_book_page(driver, book):
        print("❌ 书籍页面验证失败，返回列表")
        # 尝试返回列表
        try:
            driver.back()
            time.sleep(2)
        except:
            pass
        return "skip"

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
        time.sleep(3)  # 等待下载开始，给浏览器一些时间处理下载
    else:
        print(f"❌ 《{book['title']}》下载失败或无法找到PDF")
        if mode in ['1', '2']:  # 范围下载或指定编号下载，跳过但不影响其他书
            return "skip_no_download"
        else:  # 模式3：跳过这本书，继续下一本
            return "skip"

    # 检查下载后是否达到限额
    if check_download_limit(driver):
        print(f"⚠️ 本次下载后已达到每日限额")
        return "limit_reached"

    # 返回书籍列表
    go_back_to_list(driver)
    time.sleep(2)  # 给页面加载一些时间

    return "success" if download_success else "failed"


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
    """返回书籍列表页面（优化版本）"""
    try:
        # 方法1：使用稳定的CSS选择器定位返回按钮
        print("🔙 尝试点击返回按钮...")

        # 等待页面加载完成
        time.sleep(2)

        # 使用稳定版本中的精确CSS选择器
        book_quit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-title__back-arrow"))
        )

        # 打印按钮信息用于调试
        print(f"返回按钮信息: 是否显示={book_quit_button.is_displayed()}, 是否启用={book_quit_button.is_enabled()}")

        # 先尝试普通点击
        book_quit_button.click()
        print("✅ 成功点击返回键")

        # 验证返回成功 - 更宽松的条件
        try:
            WebDriverWait(driver, 8).until(
                lambda d: "最受欢迎" in d.title or "popular" in d.current_url
            )
            print("✅ 成功返回最受欢迎书籍榜单。")
            return True
        except:
            # 尝试其他验证方法
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "z-cover.ready"))
                )
                print("✅ 检测到书籍列表，返回成功。")
                return True
            except:
                print("⚠️ 返回验证失败，但已尝试返回")
                return True

    except Exception as e:
        print(f"❌ 无法点击返回键: {e}")

        # 方法2：尝试通过XPath定位
        try:
            print("尝试XPath定位返回按钮...")
            back_button = driver.find_element(By.XPATH, "//a[@class='page-title__back-arrow']")
            driver.execute_script("arguments[0].click();", back_button)
            print("✅ 通过JavaScript点击返回键成功")
            time.sleep(2)
            return True
        except Exception as e2:
            print(f"XPath定位也失败: {e2}")

        # 方法3：尝试浏览器后退
        try:
            print("尝试使用浏览器后退...")
            driver.back()
            time.sleep(3)

            # 检查是否返回成功
            if "最受欢迎" in driver.title or "popular" in driver.current_url:
                print("✅ 使用浏览器后退成功")
                return True
        except Exception as e3:
            print(f"浏览器后退失败: {e3}")

        # 方法4：直接导航到最受欢迎页面
        try:
            print("尝试直接导航到最受欢迎页面...")
            driver.get("https://zh.101isfj.ru/popular")
            time.sleep(3)

            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "z-cover.ready"))
            )
            print("✅ 直接导航到最受欢迎页面成功")
            return True
        except Exception as e4:
            print(f"直接导航也失败: {e4}")

        print("❌ 所有返回方法都失败")
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

        # 显示所有书籍（默认从第1本开始）
        start_display_index = 1
        while True:
            end_display_index = display_all_books(books, start_display_index)

            # 获取用户选择的下载模式
            mode = get_download_mode()

            if mode == '4':
                # 用户想要重新选择起始显示位置
                try:
                    new_start = int(input(f"请输入从第几本书开始显示（1-{len(books)}）: ").strip())
                    if 1 <= new_start <= len(books):
                        start_display_index = new_start
                        continue
                    else:
                        print("❌ 输入无效，使用默认值1")
                        start_display_index = 1
                except ValueError:
                    print("❌ 输入无效，使用默认值1")
                    start_display_index = 1
                continue

            # 根据模式获取选中的书籍索引
            selected_indices = get_book_selections(books, mode, start_display_index)

            if selected_indices == 'back_to_list':
                continue

            # 构建要下载的书籍列表
            books_to_download = []
            for idx in selected_indices:
                # 注意：书籍索引从1开始，但列表索引从0开始
                if 1 <= idx <= len(books):
                    books_to_download.append(books[idx - 1])

            if not books_to_download:
                print("❌ 没有选择要下载的书籍")
                continue

            print(f"\n🎯 已选择 {len(books_to_download)} 本书籍进行下载：")
            for i, book in enumerate(books_to_download, 1):
                print(f"{i:3d}. 《{book['title']}》")

            confirm = input("\n确认开始下载？(输入'y'或'是'开始，其他键取消): ").strip().lower()
            if confirm not in ['y', '是', 'yes']:
                print("下载已取消")
                break

            # 统计下载结果
            success_count = 0
            skip_count = 0
            failed_count = 0

            # 处理选中的书籍
            for i, book in enumerate(books_to_download, 1):
                print(f"\n{'=' * 60}")
                print(f"正在处理第 {i} 本/共 {len(books_to_download)} 本")
                print(f"书籍编号: {book['index']}")

                result = process_book(driver, book, mode)

                # 检查是否达到下载限额
                if result == "limit_reached":
                    print("⚠️ 检测到下载限额已用完，停止处理后续书籍")
                    download_limit_reached = True

                    # 处理下载限额情况
                    handle_download_limit(driver)
                    break

                elif result == "success":
                    print(f"✅ 《{book['title']}》处理成功")
                    success_count += 1
                elif result == "skip_no_download":
                    print(f"⚠️ 《{book['title']}》跳过下载（无资源），继续下一本指定书籍")
                    skip_count += 1
                elif result == "skip":
                    print(f"⚠️ 《{book['title']}》跳过，继续下一本")
                    skip_count += 1
                    if mode == '3':  # 模式3继续处理下一本
                        continue
                    else:  # 模式1和2继续处理下一本指定书籍
                        continue
                else:  # failed
                    print(f"❌ 《{book['title']}》处理失败")
                    failed_count += 1
                    if mode == '3':  # 模式3继续处理下一本
                        continue

                # 添加短暂延迟，避免请求过快
                time.sleep(1)

            # 输出统计结果
            print("\n" + "=" * 60)
            print("📊 下载统计结果:")
            print(f"   成功下载: {success_count} 本")
            print(f"   跳过: {skip_count} 本")
            print(f"   失败: {failed_count} 本")

            if download_limit_reached:
                print(f"   因下载限额已满而停止")
            else:
                print(f"   任务完成")

            break  # 完成下载后退出循环

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