# OpenClaw 復旧手順書（Zorin OS / まいちゃん専用機）

最終更新: 2026-03-21

## 0. 方針

このPCは「壊れても復旧できる」前提で運用する。
復旧の対象は主に以下:

- OpenClawワークスペース（人格・設定・記憶）
- OpenClaw状態ディレクトリ（セッション等）

---

## 1. 事前に守るもの

最低限、次をバックアップしておく。

- `~/.openclaw/workspace`
- `~/.openclaw`（可能なら全体）

この環境では、バックアップ例:

- `~/.openclaw/workspace/backups/workspace-*.tar.gz`
- `~/.openclaw/workspace/backups/openclaw-home-*.tar.gz`

加えて、workspaceは GitHub private repo に push 済み:

- `git@github.com:ldk00315-jpg/openclaw-mai.git`

---

## 2. OS再インストール後の最短復旧（推奨）

### 2-1. OpenClaw を再インストール

```bash
npm install -g openclaw
```

必要に応じて初期設定:

```bash
openclaw configure
```

### 2-2. SSH鍵を復元（GitHub pull用）

以前の鍵を保存している場合は `~/.ssh/id_ed25519_openclaw` を復元。
ない場合は再作成してGitHubに再登録。

### 2-3. workspace をGitHubから復元

```bash
mkdir -p ~/.openclaw
cd ~/.openclaw
git clone git@github.com:ldk00315-jpg/openclaw-mai.git workspace
```

すでに `workspace` がある場合:

```bash
cd ~/.openclaw/workspace
git pull
```

### 2-4. 必要なら ~/.openclaw 全体をバックアップtarから復元

```bash
# 例: openclaw-home-YYYYMMDD-HHMMSS.tar.gz を使う
cd ~
tar -xzf /path/to/openclaw-home-YYYYMMDD-HHMMSS.tar.gz
```

> 注意: 既存 `~/.openclaw` と競合する場合は、先に退避してから展開する。

---

## 3. 起動確認

```bash
openclaw --version
openclaw status
```

必要ならGateway起動:

```bash
openclaw gateway start
openclaw gateway status
```

---

## 4. 整合性チェック

バックアップ作成時の `.sha256` がある場合:

```bash
sha256sum -c /path/to/backup-file.tar.gz.sha256
```

`OK` が出れば改ざん・破損の可能性が低い。

---

## 5. 日常運用ルール（推奨）

- 重要変更のたびに `git add/commit/push`
- 大きい変更前に `~/.openclaw/workspace` をtarバックアップ
- 週1で `~/.openclaw` 全体バックアップ

---

## 6. 緊急時チェックリスト

1. まずGitHubのworkspaceをpull/clone
2. 起動不能なら `~/.openclaw` 全体バックアップを展開
3. `openclaw status` でチャンネルとGateway確認
4. Telegramでテスト送信
5. 問題なければ新しいバックアップを取り直す

---

## 7. 権限を戻す手順（NOPASSWD sudo を解除）

全権限運用をやめるときは、次を実行:

```bash
sudo rm -f /etc/sudoers.d/99-tomoyuki-nopasswd
sudo -k
```

確認:

```bash
sudo -n true && echo "まだNOPASSWD" || echo "NOPASSWD解除済み"
```
