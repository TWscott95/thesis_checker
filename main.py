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
    # 設置頁面基礎佈局
    page.title = "論文檢查系統(未完成測試版 v0.2)"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.window.width = 750
    page.window.height = 600
    page.padding = 30

    # ---------- 啟動說明對話框 ----------
    def close_dialog(e):
        notice_dialog.open = False
        page.update()

    notice_dialog = ft.AlertDialog(
        modal=True, #對話框以外，對話框不會關閉
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=28),
            ft.Text("系統使用說明與免責聲明", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
        ]),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    "本應用程式目前仍處於開發測試階段，仍然有許多 BUG 存在，其審查結果可作為部分參考，但還是有可能出現錯誤判斷。",
                    size=14, color="#E0E0E0"
                ),
                ft.Divider(color="#333333"),
                ft.Text("如有發現 BUG 或有開發建議，歡迎寄信回報：", size=13, color="#AAAAAA"),
                ft.Text("📧 tkchang.work1@gmail.com", size=14, color=ft.Colors.BLUE_400, weight=ft.FontWeight.BOLD),
                ft.Container(height=8),
                ft.Text("【目前支援功能】", size=14, color=ft.Colors.CYAN_400, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "．封面文字水平置中校對\n"
                    "．摘要與內文邊界檢查 (左邊界 3cm / 右邊界 2cm，自動排除圖表與頁碼)\n"
                    "．目錄自動定位與頁碼正確性比對",
                    size=13, color="#CCCCCC"
                )
            ], tight=True, spacing=8),
            width=500,
            padding=10
        ),
        actions=[
            ft.Button(
                "OK 我了解",
                on_click=close_dialog,
                style=ft.ButtonStyle(color=ft.Colors.CYAN_300)
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END, #操作按鈕（actions）的水平對齊方式，將所有按鈕推至對話框的最右側
        bgcolor="1E1E1E"
    )

    # ---------- 建立UI狀態與文字元件 ----------
    status_text = ft.Text("請點擊下方按鈕選擇 PDF 論文...", size=14, color=ft.Colors.GREY_400)
    total_pages_text = ft.Text("總頁數: -", size=15, color=ft.Colors.GREY_400)
    main_total_pages_text = ft.Text("內文總頁數: -", size=15, color=ft.Colors.GREY_400)
    
    cover_check_text = ft.Text("• 封面置中審查: 尚未審查", size=15, color=ft.Colors.GREY_400)
    margin_check_text = ft.Text("• 邊界格式審查 (左3/右2): 尚未審查", size=15, color=ft.Colors.GREY_400)
    check_result_text = ft.Text("• 目錄審查結果: 尚未審查", size=15, color=ft.Colors.GREY_400)

    error_list_view = ft.ListView(
        expand=True,
        spacing=8,
        height=240,
        visible=False
    )

    


    
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

    #
    if hasattr(page, "services"):
        page.services.append(ft.FilePicker())
    else:
        page.overlay.append(ft.FilePicker())

    # ---------- 審查核心邏輯函式 ----------
    async def process_pdf_file(picked_file):
        destination_path = None
        try:
            status_text.value = "檔案讀取成功，執行審查邏輯中..."
            status_text.color = ft.Colors.CYAN_300
            page.update()

            source_path = picked_file.path
            destination_path = os.path.join(TARGET_FOLDER, destination_path)

            shutil.copy2(source_path, destination_path)
            #清除上一次的審查結果
            error_list_view.controls.clear()
            error_list_view.visible = False
            all_errors = []

            with fitz.open(destination_path) as paper:
                total_pages = check_logic.get_total_pages(paper)
                content_idx = check_logic.find_content_page(paper)

                # 1.封面置中
                cover_is_centered, cover_errors = check_logic.check_cover_center(paper)
                if not cover_is_centered:
                    all_errors.extend(cover_errors)

                # 2.邊界檢測 (左 3cm/ 右 2cm)
                margin_is_correct, margin_errors = check_logic.check_margins(paper)
                if not margin_is_correct:
                    all_errors.extend(margin_errors)

                # 3.目錄與頁碼比對
                if content_idx is None:
                    main_total_pages = 0
                    catalog_is_correct = False
                    all_errors.append("【定位失效】無法在 PDF 中找到目錄頁面!")
                else:
                    main_total_pages = check_logic.get_main_total_pages(paper, content_idx)
                    catalog_is_correct, catalog_errors = check_logic.check_content_page(paper, content_idx)
                    if not catalog_is_correct:
                        all_errors.extend(catalog_errors)

            #更新UI頁面數據
            total_pages_text.value = f"總頁數: {total_pages}"
            main_total_pages_text.value = f"內文總頁數: {main_total_pages}"

            cover_check_text.value = "• 封面置中審查: ✅ 通過" if cover_is_centered else f"• 封面置中審查: ❌ 未通過 (發現 {len(cover_errors)} 處未置中)"
            cover_check_text.color = ft.Colors.GREEN_400 if cover_is_centered else ft.Colors.RRD_400

            margin_check_text.value = "• 邊界格式審查: ✅ 通過 (符合左 3cm / 右 2cm)" if margin_is_correct else f"• 邊界格式審查: ❌ 未通過 (發現 {len(margin_errors)} 處邊界異常)"
            margin_check_text.color = ft.Colors.GREEN_400 if margin_is_correct else ft.Colors.RED_400

            check_result_text.value = "• 目錄審查結果: ✅ 通過 (頁碼精準對應)" if catalog_is_correct else "• 目錄審查結果: ❌ 未通過 (目錄頁碼有誤)"
            check_result_text.color = ft.Colors.GREEN_400 if margin_is_correct else ft.Colors.RED_400

            #渲染錯誤與疑點列表
            if all_errors:
                error_list_view.controls.append(
                    ft.Text("【詳細檢查報告 / 疑點記錄】", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_300, size=15)
                )
                for err in all_errors:
                    error_list_view.controls.append(
                        ft.Container(
                            content=ft.Text(err, color=ft.Colors.WHITE, size=13),
                            bgcolor="#2A1818" if "❌" in err or "└─" in err else "#2A2010",
                            border=ft.Border.all(1, ft.Colors.RED_900 if "❌" in err else ft.Colors.ORANGE_900),
                            border_radius=8,
                            padding=12
                        )
                    )
                error_list_view.visible = True
            #處理成功顯示
            status_text.value = "審查完畢!請參閱下方報告。"
            status_text.color = ft.Colors.GREEN_400

        except Exception as error:
            status_text.value = f"處理失敗：{str(error)}"
            status_text.color = ft.Colors.RED_400
        finally:
            if destination_path and os.path.exists(destination_path):
                try:
                    os.remove(destination_path)
                except Exception:
                    pass
            page.update()

    # ---------- 開啟選單與觸發進入點 ----------
    async def trigger_pick_files(e):
        status_text.value = "正在開啟選單..."
        status_text.color = ft.Colors.AMBER_300
        page.update()

        #直接 await 取得選取結果(files)
        files = await ft.FilePicker().pick_files(
            dialog_title="請選擇要審查的論文 PDF",
            allowed_extensions=["pdf"]
        )

        #根據回傳值判斷是選取檔案還是取消
        if files and len(files) >0:
            await process_pdf_file(files[0])
        else:
            status_text.value = "已取消選擇檔案"
            status_text.color = ft.Colors.AMBER_400
            page.update()

    #選擇檔案按鈕的建立
    select_btn = ft.Button(
        "選擇 PDF 論文進行審查",
        icon=ft.Icons.UPLOAD_FILE_ROUNDED,
        on_click=trigger_pick_files,
        style=ft.ButtonStyle(
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.CYAN_400,
            padding=20
        )
    )

    # 組合頁面 UI
    page.add(
        notice_dialog,
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, size=36, color=ft.Colors.CYAN_400),
                ft.Column([
                    ft.Text("論文格式自動審核系統", size=22, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text("Thesis Auto-Checker v0.2 Beta", size=12, color=ft.Colors.GREY_500)
                ], spacing=2)
            ]),
            padding=15,
            bgcolor="#1E1E1E",
            border_radius=12,
            border=ft.Border.all(1, "#333333")
        ),
        ft.Container(height=10),
        ft.Container(
            content=ft.Column([
                ft.Row([total_pages_text, ft.Container(width=20), main_total_pages_text]),
                cover_check_text,
                margin_check_text,
                check_result_text
            ], spacing=10),
            padding=20,
            bgcolor="#1E1E1E",
            border_radius=12,
            border=ft.Border.all(1,"#333333")
        ),
        ft.Container(height=10),
        ft.Row([select_btn, status_text], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Divider(color="#333333", height=20),
        error_list_view
    )

    # notice_dialog.open=True
    page.update()


if __name__ == "__main__":
    ft.run(main)