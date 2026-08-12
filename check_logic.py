import pymupdf as fitz
import re

# paper = fitz.open("Test_pdf.pdf")
# page1 = paper[0]

# blocks = page1.get_text("dict")["blocks"]

#取得總頁數
def get_total_pages(file_path):
    paper = fitz.open(file_path)
    total_pages = len(paper)
    return total_pages

#取得正文總頁數
def get_main_total_pages(file_path, content_idx):
    paper = fitz.open(file_path)
    total_pages = len(paper)
    first_page_idx = find_first_page(file_path, content_idx)
    head_idx = first_page_idx
    main_total_pages = total_pages-head_idx
    return main_total_pages

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
        matches = page.search_for("目錄")
        if matches:
            if not is_found:
                is_found = True
                content_idx[0] = page_idx
            elif is_found and content_idx[0] > content_idx[1]:
                content_idx[1] = page_idx-1
            
            # print(f"Page {page_idx + 1}: {matchs}")
    return content_idx

#提取目錄(章節、頁碼)，並回傳目錄
def extract_content(file_path, content_idx):
    paper = fitz.open(file_path)
    total_pages = len(paper)
    pattern = re.compile(r"(.+?)\s*[\.]{2,}\s*(\d+)")
    matches = pattern.findall(paper[content_idx[0]].get_text())
    #列印完整目錄
    for page_idx in range(content_idx[0]+1, content_idx[1] + 1):
        page = paper[page_idx]
        text = page.get_text()
        # print(f"Page {page_idx + 1} Content:\n{text}\n")
        matches.extend(pattern.findall(text))
        for title, page_num_str in matches:
            page_num = int(page_num_str)
            # print(f"Title: {title}, Page Number: {page_num}\n")
            page_num_idx = page_num - 1
            #檢查目錄頁碼是否正確
            # if page_num_idx >=0 and page_num_idx < total_pages:
            #     print(f"Title: {title}, Page Number: {page_num}\n")
    return matches

#尋找第一章的位置
def find_first_page(file_path, content_idx):
    paper = fitz.open(file_path)
    total_pages = len(paper)
    pattern = re.compile(r"(.+?)\s*[\.]{2,}\s*(\d+)")
    matches = pattern.findall(paper[content_idx[0]].get_text())
    first_chaper = matches[0][0] #第一章的標題
    first_page_idx = 1 #第一章的索引值

    #尋找第一章的位置
    for page_idx in range(content_idx[1]+1, total_pages):
        page = paper[page_idx]
        first_page = page.search_for(first_chaper)
        if first_page:
            # print(f"First Chapter '{first_chaper}' found on Page {page_idx + 1}")
            first_page_idx = page_idx
            break
    return first_page_idx

#check目錄頁碼是否正確
def check_content_page(file_path, content_idx):
    paper = fitz.open(file_path)
    total_pages = len(paper)
    first_page_idx = find_first_page(file_path, content_idx)
    head_idx = first_page_idx - 1
    result = True
    error_dict = {}

    #從正文的第一頁開始檢查到最後
    for page_idx in range(first_page_idx, total_pages):
        page = paper[page_idx]
        text = page.get_text()
        content = extract_content(file_path, content_idx)

        for title, content_num_str in content:
            content_num = int(content_num_str)
            if page.search_for(title):
                if content_num + head_idx == page_idx:
                    # print(f"Title: {title} is on Page {page_idx + 1}, and it's correct")
                    pass
                else:
                    result = False
                    error_dict[title] = content_num+head_idx
                    print(f"Title: {title} is on Page {page_idx + 1}, but should be on Page {content_num + head_idx + 1}")

    #第二次檢查;直接跳到那一頁去檢查
    for key, value in error_dict.items():
        page = paper[value]
        if page.search_for(key):
            result = True

    paper.close()
    return result


# paper.close()