import fitz
import re

# paper = fitz.open("Test_pdf.pdf")
# page1 = paper[0]

# blocks = page1.get_text("dict")["blocks"]

def print_text_blocks(blocks):
    for block in blocks:
        if block.get("type") == 0:
            for line in block["lines"]:
                for span in line["spans"]:
                    font_name = span["font"]
                    font_size = span["size"]
                    text = span["text"]

                    print(f"Font: {font_name}, Size: {font_size:.2f}, Text: {text}")

#遞迴每一頁，以尋找目錄的位置
def find_content_page(file_path):
    paper = fitz.open(file_path)
    total_pages = len(paper)
    content_idx = [0,1]
    is_found = False

    for page_idx in range(total_pages):
        page = paper[page_idx]
        matchs = page.search_for("目錄")
        if matchs:
            if not is_found:
                is_found = True
                content_idx[0] = page_idx
            elif is_found and content_idx[0] > content_idx[1]:
                content_idx[1] = page_idx-1
            
            print(f"Page {page_idx + 1}: {matchs}")
    return content_idx

#
def print_content_page(file_path, content_idx):
    paper = fitz.open(file_path)
    pattern = re.compile(r"(.+?)\s*[\.]{2,}\s*(\d+)")

    #列印完整目錄
    for page_idx in range(content_idx[0], content_idx[1] + 1):
        page = paper[page_idx]
        text = page.get_text()
        # print(f"Page {page_idx + 1} Content:\n{text}\n")
        matches = pattern.findall(text)
        for title, page_num_str in matches:
            page_num = int(page_num_str)
            # page_num_idx = page_num - 1
            #檢查目錄頁碼是否正確
            # if 0 <= page_num_idx < total_pages:
                # print(f"Title: {title}, Page Number: {page_number}")

            

# paper.close()