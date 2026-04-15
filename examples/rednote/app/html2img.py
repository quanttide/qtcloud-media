"""
将 HTML 转成图片（需要安装 playwright）
"""

from playwright.sync_api import sync_playwright


def html_to_images(
    html_file: str, output_dir: str, width: int = 1080, height: int = 1440
):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})

        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        pages = html_content.split('<div class="page')

        for i, page_content in enumerate(pages[1:], 1):
            full_html = f"""
            <html>
            <head>
            <style>{open(html_file.replace(".html", ".css"), "r").read() if __import__("os").path.exists(html_file.replace(".html", ".css")) else ""}</style>
            </head>
            <body><div class="page{page_content}</div></body>
            </html>"""
            page.set_content(full_html)
            page.screenshot(path=f"{output_dir}/page_{i:02d}.png")

        browser.close()
        print(f"生成 {len(pages) - 1} 张图片")


if __name__ == "__main__":
    html_to_images("vibe_coding_xhs.html", "output")
