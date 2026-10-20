# Seleniumで楽楽販売を操作するRPAツールです
# 端末ID管理－施設テーブル－施設一覧－有償終了日を除外－月次集計よりCSC出力をします

import sys
import io
import time
import subprocess
import tkinter                          as tk
from pathlib                            import Path
from tkinter                            import messagebox
from selenium                           import webdriver
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.common.by       import By
from selenium.webdriver.support.ui      import WebDriverWait
from selenium.webdriver.support         import expected_conditions as EC

import common.common                    as COM
import common.config                    as config

# --------------------------------------------------------------------
# メイン系
# --------------------------------------------------------------------
class MAIN:
    # ----------------------------------------------------------------
    # ヘッダ部
    # ----------------------------------------------------------------
    def proc_head():

        # YAMLファイルの読み込み
        msg = COMMON.get_yaml()
        if msg != None: return msg
        
        return None

    # ----------------------------------------------------------------
    # メイン部
    # ----------------------------------------------------------------
    def proc_main():

        # 初期処理
        PROC.init_selenium()
        
        # ログイン
        msg = PROC.disp_login()
        if msg != None: return msg
        
        # 端末ID一覧を表示
        PROC.disp_tanmatuid()

        # 月次集計を表示
        PROC.disp_select()

        # ハンバーガーメニューをクリック
        PROC.disp_hamburger()

        return None

    # ----------------------------------------------------------------
    # フッター部
    # ----------------------------------------------------------------
    def proc_footer():
            
        download_path = Path.home() / "Downloads"

        # エクスプローラーを起動
        subprocess.Popen(["explorer", str(download_path)])


# --------------------------------------------------------------------
# 処理系
# --------------------------------------------------------------------
class PROC:
    
    # ----------------------------------------------------------------
    # 初期処理
    # ----------------------------------------------------------------
    def init_selenium():
        
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument("--log-level=1")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=options)
        config.driver = driver

        config.driver.get("https://hncapitol.rakurakuhanbai.jp/wfecn6a/")
        time.sleep(0.3)
            
    # ----------------------------------------------------------------
    # ログイン処理
    # ----------------------------------------------------------------
    def disp_login():
            
        # ログインID
        config.driver.find_element(By.NAME, "loginId").send_keys(config.rakuraku["id"])
        time.sleep(0.2)

        # パスワード
        config.driver.find_element(By.NAME, "loginPassword").send_keys(config.rakuraku["pw"])
        time.sleep(0.2)

        # ログインボタン
        config.driver.find_element(By.ID, "jq-loginSubmit").click()
        time.sleep(0.3)

        # ログイン判断
        if len(config.driver.find_elements(By.CLASS_NAME, "fw-message-text-main")) >= 1:
            msg = config.driver.find_element(By.CLASS_NAME, "fw-message-text-main").text
            if "ログインに失敗" in msg:
                return "ログインID、または、パスワードに誤りがあります。"

        return None
        
    # ----------------------------------------------------------------
    # 端末ID管理－施設テーブル－施設一覧を選択
    # ----------------------------------------------------------------
    def disp_tanmatuid():

        # iframeを取得
        config.driver.switch_to.frame("side")

        # 端末ID管理
        config.driver.find_element(By.ID, "nav-dbg-100169").click()
        time.sleep(0.3)

        # 施設テーブル
        config.driver.find_element(By.ID, 'nav-db-101341').click()
        time.sleep(0.3)

        # 施設一覧
        config.driver.find_element(By.ID, 'menuli_102259').click()
        time.sleep(0.3)

    # ----------------------------------------------------------------
    # 絞込み＋一覧画面を選択
    # ----------------------------------------------------------------
    def disp_select():

        # 画面遷移
        config.driver.switch_to.default_content()
        config.driver.switch_to.frame("main")

        # 絞込みのプルダウンをクリック
        wait = WebDriverWait(config.driver, 3)
        dropdown = wait.until(EC.element_to_be_clickable((By.ID, "listFormatId_chosen")))
        dropdown.click()
        time.sleep(0.3)

        # 「月次集計」をクリック
        option = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//div[@id='listFormatId_chosen']//li[normalize-space()='月次集計']"
            ))
        )
        option.click()
        time.sleep(0.3)

        # 一覧画面のプルダウンをクリック
        dropdown = wait.until(EC.element_to_be_clickable((By.ID, "searchFormatId_chosen")))
        dropdown.click()
        time.sleep(0.3)

        # 「有償終了日を除外」をクリック
        option = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//div[@id='searchFormatId_chosen']//li[normalize-space()='有償終了日を除外']"
            ))
        )
        option.click()
        time.sleep(0.3)

    # ----------------------------------------------------------------
    # ハンバーガーメニューをクリック
    # ----------------------------------------------------------------
    def disp_hamburger():

        # 画面遷移
        config.driver.switch_to.default_content()
        config.driver.switch_to.frame("main")

        # ハンバーガーメニュー
        config.driver.find_element(By.ID, "link_menu_box").click()
        time.sleep(0.5)

        # CSV出力
        config.driver.find_element(By.ID, "popupCsvExport").click()
        time.sleep(0.3)

        config.driver.find_element(By.CSS_SELECTOR, "label[for='csv_downloadUtf8']").click()
        time.sleep(0.3)

        # ダウンロード
        config.driver.find_element(By.ID, "csv_confirm_start").click()
        time.sleep(8.0)

        # ダウンロードファイル
        config.driver.find_element(By.ID, "csv_complete_link").click()
        time.sleep(2.5)

        # 閉じる
        config.driver.find_element(By.ID, "csv_complete_close").click()
        time.sleep(0.3)


# --------------------------------------------------------------------
# メッセージ表示系
# --------------------------------------------------------------------
class TKINTER():
    # ----------------------------------------------------------------
    # メッセージＢＯＸの形成
    # ----------------------------------------------------------------
    def tkinter_init():
            
        processing_window.overrideredirect(True)
        processing_window.geometry("250x70")
        processing_window.resizable(False, False)
        processing_window.update_idletasks()

        status_label.pack(expand = True)

        width = processing_window.winfo_width()
        height = processing_window.winfo_height()
        x = (processing_window.winfo_screenwidth() - width) // 2
        y = (processing_window.winfo_screenheight() - height) // 2
        processing_window.geometry(f"{width}x{height}+{x}+{y}")

        processing_window.deiconify()
        processing_window.update()

# --------------------------------------------------------------------
# 開発テスト用
# --------------------------------------------------------------------
class TEST_DEV:
    # ソースを標準出力する
    def disp_source():
        # GUIで動作させるときはコメントにしてコンパイルしないとエラーになります。
        # デバックでCLIで動作させるときはコメントを外さないと標準出力で文字化けが発生します。
        #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf-8')
        print(config.driver.page_source)

# --------------------------------------------------------------------
# 初期処理
# --------------------------------------------------------------------
def init():
    try:
        global COMMON, root, processing_window, status_label

        COMMON = COM.COMMON()

        root = tk.Tk()
        root.withdraw()
        processing_window = tk.Toplevel(root)
        processing_window.withdraw()
        status_label = tk.Label(processing_window, text = "準備中です・・・", font = ("Meiryo", 9))

        # メッセージ表示の初期処理
        TKINTER.tkinter_init()

        status_label.config(text = "ライブラリをロードしています・・・")
        processing_window.update()
        time.sleep(0.3)
        processing_window.withdraw()

        return True

    except Exception as e:
        messagebox.showerror("エラー", f"{COMMON.log_exception(e)}")
        processing_window.destroy()
        root.destroy()
    finally:
        None

# --------------------------------------------------------------------
# メイン処理
# --------------------------------------------------------------------
def main():
    try:
        # ヘッダ部
        msg = MAIN.proc_head()
        if msg != None: messagebox.showerror("エラー", msg); return None
        
        # メイン部
        MAIN.proc_main()
        if msg != None: messagebox.showerror("エラー", msg)

        # フッター部
        MAIN.proc_footer()
        
    except Exception as e:
        messagebox.showerror("エラー", f"{COMMON.log_exception(e)}")
    finally:
        processing_window.destroy()
        root.destroy()

# --------------------------------------------------------------------
# グローバル処理
# --------------------------------------------------------------------

# 初期処理
if not init(): exit(1)

# メイン処理
main()
