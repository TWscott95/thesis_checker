import flet as ft
import check_logic
import os
import shutil

file_path = "Test_pdf.pdf"
TARGET_FOLDER = "./uploaded_theses"
total_pages = check_logic.get_total_pages(file_path)
content_idx = check_logic.find_content_page(file_path)
# print(f"Content Page Number: {content_idx}")
# check_logic.find_first_page(file_path, content_idx)
main_total_pages = check_logic.get_main_total_pages(file_path, content_idx)
result = check_logic.check_content_page(file_path, content_idx)

# UI介面
def main(page: ft.Page):
    page.title = "論文檢查系統(未完成測試版 v0.1)"
    page.window.width = 750
    page.window.height = 600
    page.padding = 40
    # page.bgcolor = ft.Colors.GREY_50


    page.add(ft.Text(f"Hello, World! (Page 1 of {total_pages})"))
    page.add(ft.Text(f"目錄審查結果: {'頁碼全部正確' if result else '頁碼可能有錯誤'}"))
    page.add(ft.Text(f"內文總頁數: {main_total_pages}"))

ft.run(main)