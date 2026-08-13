import os
import shutil
import flet as ft
import pymupdf as fitz
import check_logic

TARGET_FOLDER = "./uploaded_theses"
if not os.path.exists(TARGET_FOLDER):
    os.makedirs(TARGET_FOLDER)

# total_pages = 0
# content_idx = []
# # print(f"Content Page Number: {content_idx}")
# # check_logic.find_first_page(file_path, content_idx)
# main_total_pages = 0
# result = False

# UI介面
async def main(page: ft.Page):
    page.title = "論文檢查系統(未完成測試版 v0.1)"
    page.window.width = 750
    page.window.height = 600
    page.padding = 40
    # page.bgcolor = ft.Colors.GREY_50

    #建立UI元件
    status_text = ft.Text("請選擇檔案...", size=16)
    total_pages_text = ft.Text("總頁數: -", size=16)
    check_result_text = ft.Text("目錄審查結果: 尚未審查", size=16)
    main_total_pages_text = ft.Text("內文總頁數: -", size=16)

    #處理選擇檔案
    async def handle_pick_files(e):
        status_text.value = "正在開啟選單..."
        status_text.color = ft.Colors.BLACK
        page.update()

        files = await ft.FilePicker().pick_files(
            allow_multiple=False,
            dialog_title="請選擇要上傳的檔案"
        )

        destination_path = None

        #判斷 files(list) 中是否有東西
        if files and len(files) >0:
            try:
                picked_file = files[0]
                source_path = picked_file.path
                destination_path = os.path.join(TARGET_FOLDER,picked_file.name)

                #複製檔案
                shutil.copy2(source_path, destination_path)
                status_text.value = f"檔案讀取成功，執行審查邏輯中..."
                status_text.color = ft.Colors.BLUE
                page.update()

                #審查邏輯
                with fitz.open(destination_path) as paper:
                    total_pages = check_logic.get_total_pages(paper)
                    content_idx = check_logic.find_content_page(paper)
                    main_total_pages = check_logic.get_main_total_pages(paper, content_idx)
                    check_result = check_logic.check_content_page(paper, content_idx)

                #更新UI文字內容
                total_pages_text.value = f"總頁數: {total_pages}"
                main_total_pages_text.value = f"內文總頁數: {main_total_pages}"
                check_result_text.value = (f"目錄審查結果: {'頁碼全部正確' if check_result else '頁碼可能有錯誤'}")
                # 處理成功提示
                status_text.value = "處理邏輯執行完畢！"
                status_text.color = ft.Colors.GREEN

            except Exception as error:
                status_text.value = f"處理失敗：{str(error)}"
                status_text.color = ft.Colors.RED

            finally:
                #執行最後自動刪除暫存檔案
                if destination_path and os.path.exists(destination_path):
                    try:
                        os.remove(destination_path)
                        print(f"【系統通知】暫存檔已安全刪除：{destination_path}")
                    except Exception as delete_err:
                        print(f"【系統錯誤】無法刪除暫存檔：{str(delete_err)}")
        else:
            status_text.value = "已取消選擇檔案。"
            status_text.color = ft.Colors.ORANGE
        page.update()


    #選擇檔案按鈕的建立
    select_btn = ft.Button(
        "從電腦選擇檔案並上傳",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=handle_pick_files,
    )

    page.add(
            total_pages_text,
            check_result_text,
            main_total_pages_text,
            select_btn,
            ft.Divider(),
            status_text
    )


ft.run(main)