# Naoya's Personal Website

## Getting Started
Install Dependencies
```sh
pnpm install
```

Development
```sh
pnpm run dev
```

Build
```sh
pnpm run build
```

Preview
```sh
pnpm run preview
```

## Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
/
├── public/
│   └── favicon.ico
│   └── social-image.svg
├── src/
│   ├── actions/
│   │   └── # Astro server actions
│   ├── assets/
│   │   └── # Images that are transformed, optimized and bundled by Astro 
│   ├── components/
│   │   └── # Astro and React components
│   ├── layouts/
│   │   └── RootLayout.astro
│   └── pages/
│   │   └── blog/
│   │   │   └── index.astro
│   │   │   └── [...slug].astro
│   │   └── about.astro
│   │   └── contact.astro
│   │   └── index.astro
│   │   └── projects.astro
│   └── styles/
│   │   └── global.css
└── .gitignore
└── astro.config.mjs
└── package.json
└── tsconfig.json
```

## Deployment
Deployed on [Cloudflare Pages](https://pages.cloudflare.com/). For more information, see the [Cloudflare Pages documentation](https://developers.cloudflare.com/pages/).

## Issue to Article (自動記事生成)

GitHub Issueからブログ記事を自動生成する機能です。

### 使い方

1. **Issueを作成**：リポジトリで新しいIssueを作成
2. **front matter付きで本文を記述**：

```markdown
---
title: 記事タイトル
slug: article-slug
snippet: 記事の概要
category: カテゴリ名
pubDate: 2025-03-01
readingDuration: 5
coverAlt: カバー画像の説明
originalLink: https://example.com/original
cover: https://example.com/cover-image.jpg
---

# 記事本文

ここに本文を書く...

![画像の説明](https://example.com/image.jpg)
```

3. **`publish` ラベルを付与**
4. **Issueを閉じる**：Closeすると自動的にGitHub Actionsが起動

### 動作

- 画像は自動的にダウンロードされ、`public/images/articles/{slug}/` に保存
- MarkdownファイルのURLはローカルパスに置換
- 記事は `src/content/articles/{slug}.md` として生成
- 許可されたドメインからのみ画像をダウンロード（`.github/allowed_image_hosts.txt`で設定）

### セキュリティ

- OWNER/MEMBER/COLLABORATORのみ実行可能
- HTTPSのみ許可
- 画像サイズ制限: 1ファイル10MB、合計50MB
- 許可リスト方式でドメイン制御
