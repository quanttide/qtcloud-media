"""
小红书图片生成器
"""

import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


class XHSMaker:
    def __init__(self, template_dir: str = "../templates"):
        self.template_dir = Path(template_dir)
        self.templates = {}

    def load_template(self, name: str) -> str:
        template_path = self.template_dir / f"{name}.html"
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {name}")
        return template_path.read_text(encoding="utf-8")

    def render(self, template_name: str, data: dict) -> str:
        template = self.load_template(template_name)

        pages = data.get("pages", [])
        html_parts = []

        for i, page in enumerate(pages):
            page_type = page.get("type", "content")
            html_parts.append(self._render_page(template, page_type, page))

        return self._wrap_html("\n".join(html_parts))

    def _render_page(self, template: str, page_type: str, data: dict) -> str:
        replacements = {
            "{{title}}": data.get("title", ""),
            "{{subtitle}}": data.get("subtitle", ""),
            "{{heading}}": data.get("heading", ""),
            "{{content}}": self._format_content(data.get("points", [])),
            "{{footer}}": data.get("footer", ""),
        }

        page_html = template
        for key, value in replacements.items():
            page_html = page_html.replace(key, value)

        return page_html

    def _format_content(self, points: list) -> str:
        if not points:
            return ""
        items = "".join(f"<li>{p}</li>" for p in points)
        return f"<ul>{items}</ul>"

    def _wrap_html(self, pages_html: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书图片</title>
    <style>
        @page {{ size: 1080px 1440px; margin: 0; }}
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif; }}
        .page {{ width: 1080px; height: 1440px; page-break-after: always; position: relative; overflow: hidden; box-sizing: border-box; padding: 80px 60px; }}
        * {{ box-sizing: border-box; }}
    </style>
</head>
<body>
{pages_html}
</body>
</html>"""

    def generate_images(self, html: str, output_dir: str = "output"):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1440})

            pages = html.split('<div class="page')

            for i, page_content in enumerate(pages[1:], 1):
                full_html = (
                    f"<html><body><div class='page{page_content}</div></body></html>"
                )
                page.set_content(full_html)
                page.screenshot(path=str(output_path / f"page_{i:02d}.png"))

            browser.close()

        print(f"生成 {len(pages) - 1} 张图片 → {output_dir}/")


def main():
    if len(sys.argv) < 3:
        print("用法: python xhs_maker.py <template> <json_data>")
        print("示例: python xhs_maker.py cover.json")
        sys.exit(1)

    template = sys.argv[1]
    data_file = sys.argv[2] if len(sys.argv) > 2 else None

    maker = XHSMaker()

    if data_file:
        with open(data_file, encoding="utf-8") as f:
            data = json.load(f)
        html = maker.render(template, data)
    else:
        template_path = Path(f"../templates/{template}.html")
        if template_path.exists():
            html = template_path.read_text(encoding="utf-8")
        else:
            print(f"模板不存在: {template}")
            sys.exit(1)

    maker.generate_images(html)


if __name__ == "__main__":
    main()
