#!/usr/bin/env python3
"""
Issue to Article Converter

Issueの本文からMarkdown記事を生成し、画像をダウンロードしてローカル参照に置換する。
"""

import os
import re
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# ========== 設定 ==========
ARTICLES_DIR = Path("src/content/articles")
IMAGES_DIR = Path("public/images/articles")

# 許可するドメイン（画像ダウンロード元）
ALLOWED_DOMAINS = [
    "github.com",
    "user-attachments",
    "githubusercontent.com",
    "avatars.githubusercontent.com",
    "raw.githubusercontent.com",
    "substackcdn.com",
    "substack-post-media.s3.amazonaws.com",
]

# サイズ制限
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB per image
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total

# Content-Type to extension mapping
CONTENT_TYPE_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


def slugify(text: str, max_length: int = 50) -> str:
    """テキストをスラッグに変換"""
    # 小文字化
    slug = text.lower()
    # 英数字とスペース以外を削除
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # スペースをハイフンに
    slug = re.sub(r'[\s_]+', '-', slug)
    # 連続ハイフンを1つに
    slug = re.sub(r'-+', '-', slug)
    # 前後のハイフンを削除
    slug = slug.strip('-')
    # 長さ制限
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    return slug or "untitled"


def extract_frontmatter(body: str) -> tuple[dict, str]:
    """front matterを抽出"""
    frontmatter = {}
    content = body

    # front matterの検出（---で囲まれた部分）
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', body, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        content = body[fm_match.end():]

        # 行単位でパース（シンプルなキー: 値 形式のみ対応）
        for line in fm_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip()
                # 引用符を除去
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                frontmatter[key] = value

    return frontmatter, content


def extract_image_urls(frontmatter: dict, content: str) -> list[tuple[str, str]]:
    """画像URLを抽出。(url, type) のリストを返す。typeは 'cover' または 'body'"""
    urls = []
    seen = set()

    # front matterからcover画像を抽出
    if 'cover' in frontmatter:
        cover_url = frontmatter['cover']
        if cover_url.startswith('http'):
            urls.append((cover_url, 'cover'))
            seen.add(cover_url)

    # 本文から画像URLを抽出
    img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(img_pattern, content):
        url = match.group(2).strip()
        if url.startswith('http') and url not in seen:
            urls.append((url, 'body'))
            seen.add(url)

    return urls


def is_allowed_domain(url: str) -> bool:
    """URLが許可ドメインかチェック"""
    for domain in ALLOWED_DOMAINS:
        if domain in url:
            return True
    return False


def download_image(url: str, save_path: Path, total_downloaded: int) -> tuple[bool, int]:
    """画像をダウンロード。成功時は(True, bytes)、失敗時は(False, 0)を返す"""
    if not url.startswith('https://'):
        print(f"  ⚠️ HTTPSではないURLをスキップ: {url}")
        return False, 0

    if not is_allowed_domain(url):
        print(f"  ⚠️ 許可されていないドメイン: {url}")
        return False, 0

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            content_type = response.headers.get('Content-Type', '').split(';')[0].strip()

            # Content-Typeチェック
            if not content_type.startswith('image/'):
                print(f"  ⚠️ 画像ではないContent-Type: {content_type}")
                return False, 0

            # 拡張子を決定
            ext = CONTENT_TYPE_TO_EXT.get(content_type)
            if not ext:
                # URLから拡張子を推測
                url_path = url.split('?')[0]
                for e in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                    if url_path.lower().endswith(e):
                        ext = '.jpg' if e == '.jpeg' else e
                        break
                else:
                    ext = '.jpg'  # デフォルト

            # 最終的な保存パス（拡張子を追加）
            final_path = save_path.with_suffix(ext)

            # サイズチェック
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > MAX_IMAGE_SIZE:
                print(f"  ⚠️ 画像サイズが大きすぎます: {int(content_length) / 1024 / 1024:.1f}MB")
                return False, 0

            # ダウンロード
            data = response.read()
            if len(data) > MAX_IMAGE_SIZE:
                print(f"  ⚠️ 画像サイズが大きすぎます: {len(data) / 1024 / 1024:.1f}MB")
                return False, 0

            if total_downloaded + len(data) > MAX_TOTAL_SIZE:
                print(f"  ⚠️ 合計サイズ上限に達しました")
                return False, 0

            # 保存
            final_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.write_bytes(data)
            print(f"  ✅ ダウンロード完了: {final_path.name} ({len(data) / 1024:.1f}KB)")

            return True, len(data)

    except urllib.error.URLError as e:
        print(f"  ❌ ダウンロード失敗: {url} - {e}")
        return False, 0
    except Exception as e:
        print(f"  ❌ エラー: {url} - {e}")
        return False, 0


def get_image_filename(url: str, img_type: str) -> str:
    """画像のファイル名を生成（拡張子なし）"""
    if img_type == 'cover':
        return 'cover'
    else:
        # URLからハッシュを生成
        url_hash = hashlib.sha1(url.encode()).hexdigest()[:8]
        return f'img-{url_hash}'


def find_actual_image_path(base_path: Path) -> Optional[Path]:
    """拡張子なしのパスから、実際に存在する画像ファイルを探す"""
    for ext in ['.jpg', '.png', '.gif', '.webp', '.svg']:
        path = base_path.with_suffix(ext)
        if path.exists():
            return path
    return None


def main():
    # 環境変数から入力を取得
    issue_number = os.environ.get('ISSUE_NUMBER', '0')
    issue_title = os.environ.get('ISSUE_TITLE', 'Untitled')
    issue_body = os.environ.get('ISSUE_BODY', '')

    print(f"📝 Issue #{issue_number}: {issue_title}")
    print("=" * 50)

    if not issue_body:
        print("❌ Issue本文が空です")
        return

    # 1. front matter抽出
    frontmatter, content = extract_frontmatter(issue_body)
    print(f"📋 Front matter keys: {list(frontmatter.keys())}")

    # 2. slug決定
    slug = frontmatter.get('slug', '')
    if not slug:
        slug = slugify(issue_title)
    # 危険文字を除去
    slug = re.sub(r'[./\\]', '', slug)
    print(f"📌 Slug: {slug}")

    # 3. 画像URL収集
    image_urls = extract_image_urls(frontmatter, content)
    print(f"🖼️ 画像URL数: {len(image_urls)}")

    # 4. 画像ダウンロード & URL→ローカルパスのマッピング作成
    url_to_local: dict[str, str] = {}
    images_dir = IMAGES_DIR / slug
    total_downloaded = 0

    for url, img_type in image_urls:
        filename = get_image_filename(url, img_type)
        save_path = images_dir / filename  # 拡張子なし

        success, size = download_image(url, save_path, total_downloaded)
        if success:
            total_downloaded += size
            # 実際のファイルパスを探す
            actual_path = find_actual_image_path(save_path)
            if actual_path:
                # 公開パス（/images/articles/slug/filename.ext）
                local_path = f"/images/articles/{slug}/{actual_path.name}"
                url_to_local[url] = local_path

    print(f"📦 ダウンロード合計: {total_downloaded / 1024:.1f}KB")

    # 5. front matterのcover URLを置換
    updated_frontmatter = frontmatter.copy()
    if 'cover' in frontmatter and frontmatter['cover'] in url_to_local:
        # Astroのimage()用に相対パス形式に変換
        # /images/articles/slug/cover.jpg -> ../../../public/images/articles/slug/cover.jpg
        local_path = url_to_local[frontmatter['cover']]
        # 相対パス形式に変換（src/content/articles からの相対パス）
        relative_path = f"../../../public{local_path}"
        updated_frontmatter['cover'] = relative_path

    # 6. 本文の画像URLを置換
    updated_content = content
    for url, local_path in url_to_local.items():
        # Markdown画像記法の置換
        # ![alt](url) -> ![alt](local_path)
        pattern = re.escape(url)
        updated_content = re.sub(
            rf'(!\[[^\]]*\]\(){pattern}(\))',
            rf'\g<1>{local_path}\g<2>',
            updated_content
        )

    # 7. 記事ファイルを生成
    article_path = ARTICLES_DIR / f"{slug}.md"

    # front matterを再構築
    fm_lines = ['---']
    for key, value in updated_frontmatter.items():
        # 値にスペースや特殊文字が含まれる場合の処理
        if isinstance(value, str) and (':' in value or '\n' in value or value.startswith(' ')):
            # 引用符で囲む必要がある場合
            if '"' in value:
                value = f"'{value}'"
            else:
                value = f'"{value}"'
        fm_lines.append(f'{key}: {value}')
    fm_lines.append('---')
    fm_lines.append('')

    # ファイル出力
    article_content = '\n'.join(fm_lines) + updated_content
    article_path.parent.mkdir(parents=True, exist_ok=True)
    article_path.write_text(article_content, encoding='utf-8')

    print(f"✅ 記事を保存しました: {article_path}")
    print("=" * 50)


if __name__ == '__main__':
    main()

