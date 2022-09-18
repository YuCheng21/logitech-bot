import threading
import logging
import random
from tkinter import Tk, Button, Label, Entry, StringVar, N, E, \
    messagebox, scrolledtext, END, LabelFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from configparser import ConfigParser

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S')

# define global variable
driver = None
running = None
interrupt = None

# load configparser
config = ConfigParser()
config.read('config.ini', encoding="utf-8")


# logging handler
class TextHandler(logging.Handler):

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)

        self.text.after(0, append)


def auto_run():
    logging.info("--------啟動程序--------")
    global driver, running, interrupt
    interrupt = threading.Event()
    # setting browser
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    driver_path = config["path"]["chrome"]
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.implicitly_wait(15)

    enter_phone(driver, interrupt)


def enter_phone(driver, interrupt):
    global running

    logging.info("進入登入頁面")
    driver.get(config["url"]["home_page"])
    interrupt.wait(timeout=2)

    driver.find_element(By.NAME, "cellPhone").send_keys(config["user"]["account"])
    driver.find_element(By.NAME, "cellPhone").send_keys(Keys.RETURN)
    interrupt.wait(timeout=2)

    PageSource = driver.page_source
    soup = BeautifulSoup(PageSource, 'html.parser')

    result = soup.find("span", type="warning")
    if "號碼格式不正確" in str(result):
        logging.info("號碼格式不正確")
        messagebox.showinfo("訊息", "號碼格式不正確")
        running = False
        logging.info("停止腳本")
        driver.quit()
        logging.info("--------停止程序--------")

    result = soup.find("div", class_="FormTitle-sc-ftjlsr fUvXEU")
    if "密碼" in str(result):
        logging.info("電話輸入成功")
        enter_pwd(driver, interrupt)


def enter_pwd(driver, interrupt):
    global running

    logging.info("進入密碼輸入頁面")
    driver.find_element(By.NAME, "password").send_keys(config["user"]["password"])
    driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    interrupt.wait(timeout=4)

    PageSource = driver.page_source
    soup = BeautifulSoup(PageSource, 'html.parser')

    result = soup.find("span", type="warning")
    if "須輸入 6~20 碼英數字" in str(result):
        logging.info("須輸入 6~20 碼英數字")
        messagebox.showinfo("訊息", "須輸入 6~20 碼英數字")
        running = False
        logging.info("停止腳本")
        driver.quit()
        logging.info("--------停止程序--------")

    result = soup.find("div", class_="Container-sc-a603rc")
    if "帳號密碼有誤，請重新輸入" in str(result):
        logging.info("帳號密碼有誤，請重新輸入")
        messagebox.showinfo("訊息", "帳號密碼有誤，請重新輸入")
        running = False
        logging.info("停止腳本")
        driver.quit()
        logging.info("--------停止程序--------")

    result = soup.find("li", class_="BreadcrumbContent-sc-9ysmd9 idPsKD")
    if "會員專區" in str(result):
        logging.info("密碼輸入成功")
        add(driver, interrupt)


def add(driver, interrupt):
    global running

    driver.get(config["url"]["subject_page"])
    while running:
        PageSource = driver.page_source
        soup = BeautifulSoup(PageSource, 'html.parser')

        result = soup.find("button",
                           class_="sale-page-btn core-btn add-to-cart-btn cms-secondBtnBgColor cms-secondBtnTextColor cms-secondBtnBorderColor")
        if "加入購物車" in str(result):
            logging.info("出現點擊加入購物車按鈕，嘗試點擊中")

            driver.find_element(By.CLASS_NAME, "add-to-cart-btn").click()
            driver.get("https://store.logitech.tw/V2/ShoppingCart")
            interrupt.wait(timeout=2)

            PageSource = driver.page_source
            soup = BeautifulSoup(PageSource, 'html.parser')

            result1 = soup.find("p", translate="frontend.typescripts.shopping_cart.no_items_shop_cart")
            result2 = soup.find("span", translate="frontend.typescripts.shopping_cart.next_step")

            if "您的購物車還未有商品" in str(result1):
                logging.info("加入購物車失敗，重新開始")
                driver.get(config["url"]["subject_page"])

            elif "下一步" in str(result2):
                logging.info("加入購物車成功，開始確認購物車")
                order(driver, interrupt)
                logging.info("訂單提交完成")
                running = False
                logging.info("停止腳本")
                # <----以下可以先別結束執行，能用來觀察結果--->
                # driver.quit()
                # logging.info("--------停止程序--------")

        result = soup.find("button", class_="core-btn disabled-btn")
        if "尚未開賣" in str(result):
            logging.info("尚未開賣")
            interrupt.wait(timeout=random.randint(
                int(config["refresh"]["min"]),
                int(config["refresh"]["max"])
            ))
            driver.refresh()

        elif "售完補貨中" in str(result):
            logging.info("售完補貨中")
            messagebox.showinfo("訊息", "售完補貨中")
            running = False
            logging.info("停止腳本")
            driver.quit()
            logging.info("--------停止程序--------")


def order(driver, interrupt):
    while True:
        PageSource = driver.page_source
        soup = BeautifulSoup(PageSource, 'html.parser')
        result = soup.find("span", translate="frontend.typescripts.shopping_cart.next_step")
        if "下一步" in str(result):
            driver.find_element(By.CLASS_NAME, "next-step-btn").click()
            PageSource = driver.page_source
            soup = BeautifulSoup(PageSource, 'html.parser')
            result = soup.find("h2", translate="frontend.typescripts.shopping_cart.pay_method")
            if "付款方式" in str(result):
                logging.info("確認購物車步驟完成")
                break

    driver.find_element_by_css_selector("div.cart-content-container.has-border.has-bottom-gutter > div > ul > li:nth-child(3)").click()

    driver.find_element(By.CLASS_NAME, "next-step-btn").click()
    logging.info("付款與運送方式步驟完成")

    driver.find_element(By.NAME, "FullName").send_keys(config["receive"]["FullName"])
    driver.find_element(By.NAME, "CellPhone").send_keys(config["receive"]["CellPhone"])
    driver.find_element(By.NAME, "AddressDetail").send_keys(config["receive"]["AddressDetail"])
    city = Select(driver.find_element_by_css_selector("div[class=\"choose-place split\"]>select"))
    city.select_by_visible_text(config["receive"]["City"])
    district = Select(driver.find_element_by_css_selector("div[class=\"choose-place\"]>select"))
    district.select_by_visible_text(config["receive"]["District"])
    # <---關鍵提交按鈕--->
    if config["option"]["commit"] == "true":
        driver.find_element(By.CLASS_NAME, "btn-submit").click()

    elif config["option"]["commit"] == "false":
        logging.info("略過提交訂單步驟")

    else:
        logging.info("略過提交訂單步驟")

    logging.info("資料填寫步驟完成")


def start_func():
    global running
    if not running:
        thread = threading.Thread(target=auto_run)
        thread.setDaemon(True)
        thread.start()
        running = True


def stop_func():
    global driver, running, interrupt
    if running:
        running = False
        interrupt.set()
        logging.info("停止腳本")
        # driver.quit()
        logging.info("--------停止程序--------")


def save_config():
    logging.info("開始儲存")
    global subject_page, account, password, fullName, cellPhone, addressDetail, city, district, min, max, commit

    config["url"]["subject_page"] = subject_page.get()
    config["user"]["account"] = account.get()
    config["user"]["password"] = password.get()
    config["receive"]["FullName"] = fullName.get()
    config["receive"]["CellPhone"] = cellPhone.get()
    config["receive"]["AddressDetail"] = addressDetail.get()
    config["receive"]["City"] = city.get()
    config["receive"]["District"] = district.get()
    config["refresh"]["min"] = min.get()
    config["refresh"]["max"] = max.get()
    config["option"]["commit"] = commit.get()

    with open('config.ini', 'w', encoding="utf-8") as configfile:
        config.write(configfile)
    messagebox.showinfo("訊息", "儲存完成")
    logging.info("儲存完成")


def user_interface():
    windows = Tk()
    windows.title("Logitech 爬蟲腳本")
    windows.geometry("460x650")
    windows.resizable(width=0, height=0)

    global subject_page, account, password, fullName, cellPhone, addressDetail, city, district, min, max, commit
    subject_page = StringVar()
    account = StringVar()
    password = StringVar()
    fullName = StringVar()
    cellPhone = StringVar()
    addressDetail = StringVar()
    city = StringVar()
    district = StringVar()
    min = StringVar()
    max = StringVar()
    commit = StringVar()

    subject_page.set(config["url"]["subject_page"])
    account.set(config["user"]["account"])
    password.set(config["user"]["password"])
    fullName.set(config["receive"]["FullName"])
    cellPhone.set(config["receive"]["CellPhone"])
    addressDetail.set(config["receive"]["AddressDetail"])
    city.set(config["receive"]["City"])
    district.set(config["receive"]["District"])
    min.set(config["refresh"]["min"])
    max.set(config["refresh"]["max"])
    commit.set(config["option"]["commit"])

    config_frame = LabelFrame(windows, text="配置")
    config_frame.grid(row=1, column=0)

    Label(config_frame, text="購買網址").grid(column=0, row=0, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=subject_page, width=40).grid(column=1, row=0, padx=10, pady=5, sticky=N)
    Label(config_frame, text="Logitech 電話").grid(column=0, row=1, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=account, width=40).grid(column=1, row=1, padx=10, pady=5, sticky=N)
    Label(config_frame, text="Logitech 密碼").grid(column=0, row=2, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=password, width=40, show='*').grid(column=1, row=2, padx=10, pady=5, sticky=N)
    Label(config_frame, text="真實姓名").grid(column=0, row=3, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=fullName, width=40).grid(column=1, row=3, padx=10, pady=5, sticky=N)
    Label(config_frame, text="連絡電話").grid(column=0, row=4, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=cellPhone, width=40).grid(column=1, row=4, padx=10, pady=5, sticky=N)
    Label(config_frame, text="完整地址").grid(column=0, row=5, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=addressDetail, width=40).grid(column=1, row=5, padx=10, pady=5, sticky=N)
    Label(config_frame, text="城市").grid(column=0, row=6, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=city, width=40).grid(column=1, row=6, padx=10, pady=5, sticky=N)
    Label(config_frame, text="地區").grid(column=0, row=7, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=district, width=40).grid(column=1, row=7, padx=10, pady=5, sticky=N)
    Label(config_frame, text="最短刷新速度").grid(column=0, row=8, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=min, width=40).grid(column=1, row=8, padx=10, pady=5, sticky=N)
    Label(config_frame, text="最大刷新速度").grid(column=0, row=9, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=max, width=40).grid(column=1, row=9, padx=10, pady=5, sticky=N)
    Label(config_frame, text="提交定單(true/false)").grid(column=0, row=10, ipadx=5, pady=5, sticky=E + N)
    Entry(config_frame, textvariable=commit, width=40).grid(column=1, row=10, padx=10, pady=5, sticky=N)

    Button(config_frame, text="儲存資料", command=save_config, width=60) \
        .grid(column=0, row=11, columnspan=2, padx=10, pady=5, sticky=N)

    auto_frame = LabelFrame(windows, text="自動")
    auto_frame.grid(row=2, column=0)

    Button(auto_frame, text="啟動腳本", command=start_func, width=28) \
        .grid(column=0, row=0, padx=5, pady=5, sticky=N)
    Button(auto_frame, text="停止腳本", command=stop_func, width=28) \
        .grid(column=1, row=0, padx=5, pady=5, sticky=N)

    logging_frame = LabelFrame(windows, text="記錄")
    logging_frame.grid(row=3, column=0)

    st = scrolledtext.ScrolledText(logging_frame, width=50, height=7, state='disabled', font=('微軟正黑體', 10))
    st.grid(column=0, row=0, columnspan=2, padx=10, pady=5, sticky=N)

    text_handler = TextHandler(st)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(message)s')
    text_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(text_handler)

    windows.mainloop()


if __name__ == "__main__":
    user_interface()
