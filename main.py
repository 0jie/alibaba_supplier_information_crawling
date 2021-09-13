from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from multiprocessing import Pool
# from selenium.webdriver.common.action_chains import ActionChains
import re
import time
from lxml import etree
import csv
import sys


# 登陆
class Chrome_drive():
    def __init__(self):
        self.t1 = time.time()
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        NoImage = {"profile.managed_default_content_settings.images": 2}  # 控制 没有图片
        option.add_experimental_option("prefs", NoImage)
        # option.add_argument(f'user-agent={ua.chrome}')  # 增加浏览器头部
        # chrome_options.add_argument(f"--proxy-server=http://{self.ip}")  # 增加IP地址
        option.add_argument('--headless')  # 无头浏览
        self.browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        })  # 去掉selenium的驱动设置

        self.browser.set_window_size(1200, 768)
        self.wait = WebDriverWait(self.browser, 12)

    def get_login(self):
        url = 'https://passport.alibaba.com/icbu_login.htm'
        print("正在登录...")
        self.browser.get(url)
        # self.browser.maximize_window()
        self.browser.find_element_by_id('fm-login-id').send_keys(username)
        self.browser.find_element_by_id('fm-login-password').send_keys(password)

        time.sleep(3)
        self.browser.switch_to.frame('baxia-dialog-content')
        btn = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
        actions = ActionChains(self.browser)
        actions.click_and_hold(btn).move_by_offset(360, 0).release().perform()
        self.browser.switch_to.default_content()
        time.sleep(2)
        self.browser.find_element_by_xpath('//*[@id="fm-login-submit"]').click()
        time.sleep(5)

        # k = input("1：")
        # if 'Your Alibaba.com account is temporarily unavailable' in self.browser.page_source:
        #     self.browser.close()
        # while k == 1:
        #     break
        self.browser.refresh()  # 刷新
        print("登录成功！")
        return

    # 获取判断网页文本的内容：
    def index_page(self, page, wd):


        """
        抓取索引页
        :param page: 页码
        """
        print('正在爬取第', page, '页')

        url = f'https://www.alibaba.com/trade/search?page={page}&keyword={wd}&f1=y&indexArea=company_en&viewType=L&n=38'
        js1 = f" window.open('{url}')"  # 执行打开新的标签页
        print(url)
        self.browser.execute_script(js1)  # 打开新的网页标签
        # 打开新标签
        self.browser.switch_to.window(self.browser.window_handles[-1])  # 此行代码用来定位当前页面窗口
        self.buffer()  # 网页滑动  成功切换
        # 等待加载
        time.sleep(3)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J-items-content')))

        # 获取源代码
        html = self.browser.page_source

        self.get_products(wd, html, page)

        self.close_window()

    def get_products(self, wd, html_text, page):
        """
        提取数据
        """
        e = etree.HTML(html_text)
        item_main = e.xpath('//div[@id="J-items-content"]//div[@class="item-main"]')
        items = e.xpath('//div[@id="J-items-content"]//div[@class="item-main"]')

        if items:
            print('当前页公司数:', len(items))
            j = 1
            for li in items:
                t3 = time.time()
                company_phone_page = ''.join(li.xpath('./div[@class="top"]//a[@class="cd"]/@href'))  # 公司电话连接
                product = ''.join(li.xpath('.//div[@class="value ellipsis ph"]/text()'))  # 主要产品
                # Attrs = li.xpath('.//div[@class="attrs"]//span[@class="ellipsis search"]/text()')
                # length = len(Attrs)
                counctry = ''
                total_evenue = ''
                sell_adress = ''
                product_img = ''
                # if length > 0:
                #     counctry = ''.join(Attrs[0])  # 国家
                # if length > 1:
                #     total_evenue = ''.join(Attrs[1])  # Total 收入
                # if length > 2:
                #     sell_adress = ''.join(Attrs[2])  # 主要销售地
                # if length > 3:
                #     sell_adress += '、' + ''.join(Attrs[3])  # 主要销售地
                # if length > 4:
                #     sell_adress += '、' + ''.join(Attrs[4])  # 主要销售地
                # product_img_list = li.xpath('.//div[@class="product"]/div/a/img/@src')
                # if len(product_img_list) > 0:
                #     product_img = ','.join(product_img_list)  # 产品图片

                self.browser.get(company_phone_page)

                try:
                    for k in range(0, 3):
                        self.browser.switch_to.window(self.browser.window_handles[-1])
                        if 'Your Alibaba.com account is temporarily unavailable' in self.browser.page_source:
                            self.browser.close()

                    self.browser.find_element_by_xpath('//div[@class="sens-mask"]/a').click()
                    self.browser.find_element_by_xpath('//*[@id="dialog-footer-2"]/div/button[1]').click()
                    time.sleep(2)

                    tree = etree.HTML(self.browser.page_source)
                    company_name = tree.xpath('.//div[@class="content"]/table/tr[1]/td/text()')[0]  # 公司名称
                    contact_name = tree.xpath('.//div[@class="contact-name"]/text()')[0]    # 联系人
                    phone = ''.join(re.findall('Telephone:</th><td>(.*?)</td>', self.browser.page_source, re.S))    # 座机
                    mobilePhone = ''.join(re.findall('Mobile Phone:</th><td>(.*?)</td>', self.browser.page_source, re.S))   # 手机
                    address = tree.xpath('.//div[@class="content"]/table/tr[2]/td/text()')[0]   # 地址
                    website = tree.xpath('.//div[@class="content"]/table/tr[3]/td/div/text()')[0]   # 网址
                except:
                    print("None")
                    # k = input("1：")
                    # if 'Your Alibaba.com account is temporarily unavailable' in self.browser.page_source:
                    #     self.browser.close()
                    # while k == 1:
                    #     break
                    # self.browser.refresh()  # 刷新
                    continue

                all_down = [wd, company_name, company_phone_page, product, contact_name, phone, mobilePhone, address, website]
                save_csv(all_down, wd)
                t4 = time.time()
                print("正在爬取第 {} 页的第 {} 个，用时 {:.2f} 秒：".format(page, j, (t4-t3)), company_name, company_phone_page, contact_name, phone, mobilePhone)
                self.close_window()
                j += 1

        else:
            self.close_window()
            t2 = time.time()
            print("爬取完毕！总用时：%d 分钟" % ((t2-self.t1)/60))
            sys.exit(0)

    def buffer(self):  # 滑动网页
        for i in range(33):
            time.sleep(0.1)
            self.browser.execute_script('window.scrollBy(0,380)', '')  # 向下滑行

    def close_window(self):
        length = self.browser.window_handles
        if len(length) > 3:
            self.browser.switch_to.window(self.browser.window_handles[1])
            self.browser.close()
            time.sleep(1)
            self.browser.switch_to.window(self.browser.window_handles[-1])


def save_csv(lise_line, wd):
    file = csv.writer(open(f"./alibaba_{wd}_.csv", 'a', newline="", encoding="utf-8"))
    file.writerow(lise_line)


def main():
    """
    遍历每一页
    """
    run = Chrome_drive()
    run.get_login()
    for i in range(1, 100):
        run.index_page(i, wd)


if __name__ == '__main__':
    wd = 'led lights'
    csv_title = '关键词,公司名,店铺地址,主营产品,联系人,电话,手机,公司地址,公司官网'.split(',')
    username = "redheart7@163.com"
    password = "xsl1995950719.$"
    save_csv(csv_title, wd)
    main()
