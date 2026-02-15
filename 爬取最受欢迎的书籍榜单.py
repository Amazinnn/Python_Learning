import re
import cloudscraper
from bs4 import BeautifulSoup


def scrape_site(url):
    try:
        # 1. 创建scraper，增加更多参数
        scraper = cloudscraper.create_scraper(
            delay=15,  # 增加延迟时间
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False,
                'desktop': True,
            }
        )

        # 2. 添加更完整的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
        }

        # 3. 发送请求
        print(f"正在访问: {url}")
        response = scraper.get(url, headers=headers, timeout=30)

        # 4. 检查响应状态
        print(f"状态码: {response.status_code}")
        print(f"响应大小: {len(response.text)} 字节")

        # 5. 检查多种可能的反爬提示
        anti_bot_indicators = [
            "Checking your browser",
            "Just a moment",
            "DDOS protection",
            "Cloudflare",
            "Ray ID",
            "Please enable JavaScript",
            "Please enable Cookies",
            "正在检查您的浏览器"
        ]

        found_anti_bot = False
        for indicator in anti_bot_indicators:
            if indicator in response.text:
                print(f"检测到反爬虫提示: {indicator}")
                found_anti_bot = True
                break

        if found_anti_bot:
            print("仍然被反爬虫机制拦截！")

            # 保存响应用于调试
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text[:5000])  # 只保存前5000字符

            print("已保存响应内容到 debug_page.html，请检查")
            return None

        # 6. 解析HTML
        print("成功获取页面内容！")
        print(f"页面标题: {response.text[:100]}...")  # 显示前100个字符

        # 注意：response.text已经是字符串，不要再次编码！
        soup = BeautifulSoup(response.text, "html.parser")

        # 7. 提取所有<a>标签，先不筛选
        all_links = soup.find_all('a')
        print(f"\n总共找到 {len(all_links)} 个<a>标签")

        # 8. 查看前几个链接的结构
        print("\n前10个<a>标签的信息:")
        for i, link in enumerate(all_links[:10], 1):
            print(f"{i}. 文本: {link.get_text(strip=True)[:30]}")
            print(f"   属性: {link.attrs}")
            print()

        # 9. 根据实际HTML结构调整搜索条件
        # 先查看是否有author属性
        links_with_author = soup.find_all('a', attrs={'author': True})
        print(f"\n找到 {len(links_with_author)} 个带有author属性的<a>标签")

        # 10. 尝试使用正则表达式查找所有可能的图书链接
        # 首先查找包含特定class或id的容器
        book_containers = soup.find_all(['div', 'section', 'article'],
                                        class_=re.compile(r'book|item|card|product', re.I))

        print(f"\n找到 {len(book_containers)} 个可能的图书容器")

        # 11. 在这些容器中查找链接
        book_links = []
        for container in book_containers[:5]:  # 只检查前5个容器
            container_links = container.find_all('a')
            book_links.extend(container_links)

        print(f"\n在图书容器中找到 {len(book_links)} 个链接")

        # 12. 显示找到的链接
        if book_links:
            print("\n前10个可能的图书链接:")
            for i, link in enumerate(book_links[:10], 1):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                author = link.get('author', '无')
                print(f"{i}. 文本: {text[:30]:30} 作者: {author:10} 链接: {href[:50]}")

        return soup

    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


# 主程序
if __name__ == "__main__":
    base_url = "https://zh.101isfj.ru/popular"

    # 尝试访问网站
    soup = scrape_site(base_url)

    if soup:
        print("\n=== 进一步分析 ===")

        # 查看页面结构
        print("页面中的主要容器:")
        containers = soup.find_all(['div', 'section', 'main', 'article'])
        for container in containers[:5]:
            class_attr = container.get('class', [])
            id_attr = container.get('id', '')
            print(f"  容器: {container.name}, class: {class_attr}, id: {id_attr}")

        # 查看所有脚本
        scripts = soup.find_all('script')
        print(f"\n页面中有 {len(scripts)} 个<script>标签")

        # 查看页面标题
        title = soup.title
        print(f"页面标题: {title.string if title else '无标题'}")

        # 保存完整HTML用于分析
        with open('full_page.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print("\n已将完整页面保存到 full_page.html")
    else:
        print("无法获取页面内容，请尝试以下方法：")
        print("1. 使用Selenium模拟浏览器")
        print("2. 增加请求延迟")
        print("3. 使用代理IP")
        print("4. 检查网站是否可正常访问")