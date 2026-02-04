## ゴールと成果物

**ゴール**

* Issue を “編集フォーム” にして、Issue close + `publish` ラベルで記事を生成/更新
* 記事本文内の `![...](https://...)` と front matter の `cover:` などにある画像URLを、
  リポジトリ内のローカル画像に差し替える（ホットリンクしない）

**成果物**

* 記事ファイル：`src/content/articles/<slug>.md`
* 画像ファイル：`public/images/articles/<slug>/...`
* ワークフロー：`.github/workflows/issue-to-article.yml`
* 変換スクリプト：`.github/scripts/issue_to_article.py`
* （任意）許可ドメイン設定：`.github/allowed_image_hosts.txt`

---

## 1) リポジトリ構成の決定

1. 記事保存先（指定）

    * `src/content/articles/<slug>.md`
2. 画像保存先（推奨：公開パスが単純）

    * `public/images/articles/<slug>/cover.<ext>`
    * `public/images/articles/<slug>/img-<hash>.<ext>`
3. 記事中の参照ルール

    * 置換後は `/images/articles/<slug>/...` の **絶対パス**に統一
      （ビルドツールに依存しにくく、Markdownでも素直）

---

## 2) Issue 側の運用ルール（最小）

* Issue 本文は「そのまま記事Markdown」。先頭に front matter（`---`）があってもOK
* 画像の入れ方は2パターンを許可

    1. Issue にドラッグ&ドロップで添付（GitHub 由来URL）
    2. 外部画像URL（例：Substack CDN）の直貼り
* 公開フロー

    * `publish` ラベルを付けて Issue を Close → Actions 実行
    * （任意）更新も同様に、再度 close（または `publish` の付け直し）で再実行

---

## 3) GitHub Actions のトリガーと安全策

### トリガー

* `issues` イベントで `closed` と `labeled` を監視
* 条件

    * `publish` ラベルが付いている
    * `state == closed`
    * 投稿者が OWNER/MEMBER/COLLABORATOR など（不正実行防止）
* `permissions: contents: write` で push できるようにする（`GITHUB_TOKEN`）

### 追加の安全策（強く推奨）

* **画像ダウンロード先URLの制限（allowlist）**

    * GitHub添付系（`github.com/user-attachments/...` 等）＋必要な外部ドメインのみ
* **サイズ上限**（例：10MB/枚、合計50MB）
* **Content-Type が `image/*` 以外は拒否**
* **https のみ許可**
* **並列実行抑止**（`concurrency` で同時コミット衝突を避ける）

---

## 4) 変換スクリプトの処理パイプライン（核心）

### 入力

* Issue API から取得した

    * `title`
    * `body`（front matter + Markdown）
    * `number`（Issue番号）

### 出力

* `src/content/articles/<slug>.md`
* `public/images/articles/<slug>/...`（画像群）

### ステップ

1. **front matter 抽出**

* `---` で囲われたブロックがあれば抜き出す（なければ空）
* ここでは YAML を “完全パース” しなくてOK（外部依存を避ける）
  → 必要なキーだけ行単位で拾う（`slug:` / `pubDate:` / `cover:` / `isDraft:` など）

2. **slug 決定**

* `slug:` があればそれを採用
* 無ければ Issue title から slugify（英数字+ハイフン、最大長制限）
* slug はパスに使うので、`..` や `/` など危険文字は除去

3. **記事ファイルパス決定**

* `src/content/articles/<slug>.md`
* 既存があれば上書き更新（Issue＝単一ソースにする）

4. **画像URL収集**

* front matter の `cover:`（必要なら他のキーも：`ogImage:` など）からURLを拾う
* Markdown 本文から `!\[alt\]\(url\)` を正規表現で拾う

    * 例：あなたのサンプルだと `cover:` と本文の画像URLが同じなので、重複除外できると良い

5. **画像ダウンロード & 命名**

* 保存ディレクトリ：`public/images/articles/<slug>/`
* 命名ポリシー（再実行しても同じファイル名になるのが重要）

    * `cover` は固定名：`cover.<ext>`
    * 本文画像は URL からハッシュ：`img-<sha1_8>.<ext>`
* 拡張子決定

    * URL末尾から推測できないことが多い（クエリ付与など）ので、
    * **レスポンスの `Content-Type` を優先**して `.png/.jpg/.webp` を決める

6. **本文・front matter の URL 置換**

* 置換ルール

    * `cover: <URL>` → `cover: /images/articles/<slug>/cover.<ext>`
    * `![...](<URL>)` → `![...]( /images/articles/<slug>/img-....<ext> )`
* 同じ URL が複数箇所に出る場合も、一括置換できるよう **URL→ローカルパスのマップ**を作る

7. **記事を書き出し**

* front matter が無い場合でも、最低限あなたのスキーマに合わせて付与可能
  （例：`isDraft` が無ければ `true/false` を決める、`pubDate` を補完する等）
* ただし「Issueが真実」運用にするなら、基本は Issue 本文をそのまま尊重して、補完は最小に

---

## 5) ワークフローの実装タスク分解

### A. 最小リリース（画像置換まで動く）

* [ ] `.github/workflows/issue-to-article.yml` 作成
* [ ] `.github/scripts/issue_to_article.py` 作成
* [ ] `publish` ラベル運用開始（ラベル作成）
* [ ] 生成先ディレクトリ（`src/content/articles`, `public/images/articles`）を用意
* [ ] `GITHUB_TOKEN` の権限（repo settings / workflow permissions）確認

**受け入れ条件**

* Issue を close + `publish` で、`src/content/articles/<slug>.md` が更新される
* 本文の `![...](https://...)` が `/images/articles/<slug>/...` に置換される
* `public/images/articles/<slug>/...` に画像が保存される