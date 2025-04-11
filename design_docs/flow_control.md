
CloudFront単体では「セッションを保持しているユーザーだけ通す」といった**状態に基づく判定（ステートフルな判定）**を直接行うことはできません。CloudFrontは**CDNかつリバースプロキシ**であり、主に**リクエスト単位の処理（ステートレス）**を前提としています。

ただし、以下のような方法を組み合わせることで、**セッション保持ユーザーを通すような振る舞いを実現**することは可能です：

---

### ✅ 方法1: Lambda@Edge / CloudFront Functions を使ってCookieを判定する

- セッションID（例: `session_id`）が `Cookie` に含まれている前提で、
- CloudFront Functions または Lambda@Edge を使ってその Cookie の有無や値をチェックします。
- セッションが存在する場合のみリクエストを通し、それ以外はアクセス制限やリダイレクトするように振り分けます。

```js
function handler(event) {
  var request = event.request;
  var headers = request.headers;

  if (headers.cookie && headers.cookie.value.includes("session_id=")) {
    // セッションあり → 通す
    return request;
  } else {
    // セッションなし → エラーレスポンスなど
    return {
      statusCode: 403,
      statusDescription: 'Forbidden',
      body: 'Access Denied',
    };
  }
}
```

---

### ✅ 方法2: オリジン側（例: ALB + EC2, API Gateway）で制御

- CloudFrontはあくまでキャッシュ＆転送の役割にとどめ、
- セッションの存在判定は**オリジン側で行う**。
- CloudFrontは特定条件でキャッシュバイパスして、オリジンに転送するよう設定する（例: `CachePolicy`で `Cookie` をForward）。

---

### ✅ 方法3: AWS WAFを併用する

- WAFはCookieの値を使ったカスタムルールの定義が可能です。
- 例として「`session_id`というCookieが存在しなければブロック」といったルールを作成できます。
- ただし、WAFはCloudFrontより**下流のレイヤーで実行**されるため、リクエストはCloudFrontまで到達します。

---

### 🚫 CloudFront単体ではできないこと

- セッションの有効期限の検証
- セッション情報の永続的な管理やDB参照
- IPやセッション単位でのリクエストレート制御（これはWAFのレートベースルールやAPI Gatewayで対応）

---

### 実現イメージ（まとめ）

| 判定方法 | 使用サービス | 備考 |
|----------|----------------|------|
| Cookieあり判定 | Lambda@Edge or CloudFront Functions | 軽量＆高速 |
| セッション詳細検証 | オリジンサーバー側 | 状態管理が必要 |
| Cookie有無の条件付きアクセス制御 | AWS WAF | 簡易ルールに向く |


---

## ✅ [方法3: AWS WAFを併用する] 構成イメージ

```
[ユーザー] → [CloudFront] → [AWS WAF] → [オリジン（ALBやS3など）]
                   ↑
         Cookieによるアクセス制御
```

---

## ✅ 前提

- CloudFrontディストリビューションがすでにある。
- ユーザーのブラウザには `session_id` というCookieが設定されている。
- WAFをCloudFrontにアタッチして、Cookieの値に基づいてアクセス制御したい。

---

## ✅ 手順

### Step 1: AWS WAFのWebACLを作成

1. **AWSマネジメントコンソール**にログイン  
2. **WAF & Shield** → **Web ACL** を選択 → **Web ACLの作成**

   - 名前: `AllowWithSessionCookie`
   - リソースタイプ: `CloudFront`
   - CloudFrontディストリビューションを選択

---

### Step 2: ルールの作成

1. ルールを追加 → **ルールビルダーでルールを作成**
2. ルールタイプ: **カスタムルール**
3. ルール名: `AllowIfSessionCookieExists`
4. スコープ: `リクエスト`

#### 条件の設定（Cookieの値を使う）

- **一致の一致条件タイプ**: `リクエストヘッダー`
- **ヘッダー名**: `cookie`
- **マッチタイプ**: `含む（contains）`
- **文字列**: `session_id=`

※`session_id=` が含まれているかどうかを判定します。

5. このルールのアクション: `許可（Allow）`

---

### Step 3: デフォルトアクションを「拒否」にする

- ルールの優先順位が重要です。
- `AllowIfSessionCookieExists` が一致しなかった場合、**他のリクエストはブロック（Deny）**するように、WebACLの**デフォルトアクションを「拒否」**に設定してください。

---

### Step 4: Web ACLをCloudFrontにアタッチ

- WebACL作成時に選択していない場合、あとから **「WebACL」→「リソースの関連付け」** で CloudFront にアタッチ可能です。

---

## ✅ 補足

- Cookieの値が `session_id=` を含むリクエストのみ許可され、それ以外はブロックされます。
- セッションの有効期限まではチェックできません（WAFはステートレスです）。
- 複雑なパターンマッチが必要なら、**正規表現ルールセット（Regex Match Statement）**の使用も可能です。

---

## ✅ 例：複数条件を追加したい場合

例えば、次のような高度な条件も可能です：

- `session_id=` が含まれている **かつ**
- `User-Agent` が特定の値（例えばbot以外）

この場合は、**「AND条件のルール」**を作成して複数ステートメントを組み合わせます。

---
