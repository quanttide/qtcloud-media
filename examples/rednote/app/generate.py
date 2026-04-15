"""
小红书图片生成器 - 从 JSON 到 PNG
"""

import json
import sys
from pathlib import Path
import subprocess


def load_template(name: str) -> str:
    template_path = Path(__file__).parent / "templates" / f"{name}.html"
    return template_path.read_text(encoding="utf-8")


def wrap_html(content: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: 1080px 1440px; margin: 0; }}
        body {{ margin: 0; font-family: -apple-system, "PingFang SC", sans-serif; }}
        .page {{ width: 1080px; height: 1440px; page-break-after: always; padding: 80px; box-sizing: border-box; }}
        .cover {{ background: linear-gradient(135deg, #ff6b6b, #ff4757); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
        .cover h1 {{ font-size: 72px; margin: 0; }}
        .cover p {{ font-size: 40px; opacity: 0.9; margin-top: 30px; }}
        .cta {{ background: linear-gradient(135deg, #ff6b6b, #ff4757); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
        .cta h1 {{ font-size: 64px; margin: 0; }}
        .cta p {{ font-size: 36px; opacity: 0.9; margin: 20px 0; }}
        .cta .tag {{ background: white; color: #ff4757; padding: 20px 40px; border-radius: 50px; font-size: 32px; margin-top: 40px; }}
        .content {{ background: #fff; }}
        .content h2 {{ font-size: 52px; color: #333; margin-bottom: 50px; }}
        .content ul {{ font-size: 36px; line-height: 2.2; padding-left: 40px; }}
        .content li {{ margin: 24px 0; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""


def render_page(page_type: str, data: dict) -> str:
    if page_type == "cover":
        return f"""<div class="page cover">
    <h1>{data.get("title", "")}</h1>
    <p>{data.get("subtitle", "")}</p>
</div>"""
    elif page_type == "cta":
        return f"""<div class="page cta">
    <h1>{data.get("title", "")}</h1>
    <p>{data.get("subtitle", "")}</p>
    <div class="tag">👆 关注我</div>
</div>"""
    else:
        points = "".join(f"<li>{p}</li>" for p in data.get("points", []))
        return f"""<div class="page content">
    <h2>{data.get("title", "")}</h2>
    <ul>{points}</ul>
</div>"""


def generate_html(data: dict, output_dir: Path):
    pages = data.get("pages", [])
    html_files = []

    for i, page in enumerate(pages, 1):
        page_type = page.get("type", "content")
        content = render_page(page_type, page)
        html = wrap_html(content)

        html_file = output_dir / f"page_{i:02d}.html"
        html_file.write_text(html, encoding="utf-8")
        html_files.append(html_file)
        print(f"生成: {html_file.name}")

    return html_files


def generate_images(html_files: list[Path], output_dir: Path):
    output_dir.mkdir(exist_ok=True)

    for html_file in html_files:
        output_file = output_dir / f"{html_file.stem}.png"

        result = subprocess.run(
            [
                "wkhtmltoimage",
                "--quality",
                "95",
                "--width",
                "1080",
                "--height",
                "1440",
                "--zoom",
                "2",
                "--no-stop-slow-scripts",
                "--enable-local-file-access",
                str(html_file),
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"错误: {result.stderr}")
        else:
            print(f"生成: {output_file.name}")

    print(f"\n完成！图片保存在: {output_dir}")


def main():
    json_file = Path(__file__).parent.parent / "sample" / "json" / "xhs_maker.json"
    templates_dir = Path(__file__).parent.parent / "sample" / "templates"
    html_dir = Path(__file__).parent.parent / "sample" / "html"
    output_dir = Path(__file__).parent.parent / "sample" / "png"

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    print("1. 生成 HTML...")
    html_files = generate_html(data, html_dir)

    print("\n2. 生成图片...")
    generate_images(html_files, output_dir)


if __name__ == "__main__":
    main()
