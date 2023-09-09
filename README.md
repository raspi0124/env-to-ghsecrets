# env-to-ghsecrets

任意の.env ファイルを特定の GitHub レポジトリの Secrets に登録するだけ

## 使い方

### 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 実行

```bash
python convert.py --env-file .env --repo <repo_name> --owner <owner> --token <token>
```
