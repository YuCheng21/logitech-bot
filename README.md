## Description

大學的時候搶羅技過年 28 折特價寫的下單機器人，偶然翻到留個紀錄，有些地方可能需要修改，只有一些陽春的功能。

附上人權圖證明這個垃圾曾經還是有點用的。
![screenshot](./static/screenshot.png)

## Environment

```bash
pip install -r ./requirements.txt
```

- 需要在 `config.ini` 指定 chromedriver.exe 的路徑，記得要下載符合自己電腦瀏覽器版本的 chrome driver。

2022.09.18: 在 Windows10 上使用 Python3.9 測試可以執行開啟瀏覽器嘗試登入網站。

## RUN

```bash
python Logitech.py
```

開啟 GUI 後把資料填一填按儲存資料，接著就可以按啟動腳本，程式會根據填寫的資料開啟瀏覽器開始操作網頁。

刷新速度是設定重新整理的間隔時間，會在範圍隨機時間重新整理網頁，檢查商品是否已經開賣。

如果可以開始購買就會填寫使用者資料，並執行下單。將提交訂單設為 `false` 則不會進行最後一步下單動作，要下單記得改成 `true`。