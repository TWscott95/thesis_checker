import flet as ft
import check_logic

file_path = "Test_pdf.pdf"
content_idx = check_logic.find_content_page(file_path)
print(f"Content Page Number: {content_idx}")



# UI介面
# def main(page: ft.Page):
#     page.title = "測試"
    # page.add(ft.Text(f"Hello, World! (Page 1 of {total_pages})"))


# ft.run(main)