import pymupdf as fitz
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


#取得總頁數
def get_total_pages(paper):
    return len(paper)

#遞迴每一頁，以尋找目錄的位置
def find_content_page(paper):
    total_pages = len(paper)
    content_idx = None
    # is_found = False

    for page_idx in range(1,total_pages):
        text = paper[page_idx].get_text()
        has_catalog_keyword = bool(re.search(r"目\s*錄|table\s*of\s*contents|contents", text, re.IGNORECASE))
        has_lines_or_digits = bool(re.search(r"[\.\-_]{2,}|\d+", text))

        if has_catalog_keyword and has_lines_or_digits:
            clean_text = text.replace(" ", "").replace("\n", "").lower()
            if ("圖目錄" in clean_text or "表目錄" in clean_text) and not any(k in clean_text for k in ["中文摘要","摘要","第一章","第三章","誌謝"]):
                if content_idx is None:
                    continue

            if content_idx is None:
                content_idx = [page_idx, page_idx]
            else:
                if page_idx == content_idx[1]+1:
                    content_idx[1] = page_idx

    if content_idx is None:
        print("【系統提示】啟用硬體防護備援定位...")
        for page_idx in range(4, min(12, total_pages)):
            text = paper[page_idx].get_text()
            if len(re.findall(r"[\.\-_]{3,}", text)) >=3:
                content_idx = [page_idx, page_idx]
                if page_idx +1 < total_pages and len(re.findall(r"[\.\-_]{3,}", paper[page_idx+1].get_text())) >=3:
                    content_idx[1] = page_idx
                break
    if content_idx:
        print(f"【定位成功】目錄位於 PDF 第 {content_idx[0]+1} ~ {content_idx[1]+1} 頁 (索引 {content_idx})")
    else:
        print("【定位失敗】未能找到明確的目錄頁面!")

    return content_idx


# 提取目錄(章節、頁碼)，並回傳目錄
def extract_content(paper, content_idx):
    if not content_idx:
        return []
    
    pattern = re.compile(r"([^\.\-_\n\r]+?)[\.\-_]{2,}\s*(\d+|\b[IVXLCDM]+\b)", re.IGNORECASE)
    matches = []
    # 常見需要排除的目錄標頭（移除空格、轉小寫比較）
    exclude_words = {"目錄", "contents", "tableofcontents", "圖目錄", "表目錄", "圖表目錄", "listoffigures", "listoftables"}
    
    
    for page_idx in range(content_idx[0], content_idx[1] + 1):
        text = paper[page_idx].get_text()
        found = pattern.findall(text)
        for title, page_num in found:
            clean_title = title.strip() #去除標題前後的空白

            if clean_title:
                # 移除所有空格並轉小寫，進行更嚴格的標頭排除
                check_title = clean_title.replace(" ", "").lower()
                if check_title not in exclude_words:
                    matches.append((clean_title, page_num))

    return matches


#尋找第一章的位置
def find_first_page(paper, content_idx):
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


#取得正文總頁數
def get_main_total_pages(paper, content_idx):
    if not content_idx:
        return 0
    total_pages = len(paper)
    first_page_idx = find_first_page(paper, content_idx)
    if first_page_idx is None:
        return 0
    return max(0, total_pages-first_page_idx)
    # head_idx = first_page_idx
    # main_total_pages = total_pages-head_idx



#check目錄頁碼是否正確
def check_content_page(paper, content_idx):
    total_pages = len(paper)
    first_page_idx = find_first_page(paper, content_idx)
    head_idx = first_page_idx - 1
    result = True
    error_dict = {}

    #從正文的第一頁開始檢查到最後
    for page_idx in range(first_page_idx, total_pages):
        page = paper[page_idx]
        text = page.get_text()
        content = extract_content(paper, content_idx)

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

    return result
