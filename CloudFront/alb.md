ALB（Application Load Balancer）で、配下のターゲットグループに **一台もターゲットが登録されていない** または **登録されているが全てのターゲットが非正常（unhealthy）** な場合、リクエストに対しては **HTTPステータスコード 503 (Service Unavailable)** が返されます。

---

### 🔍 詳細
- **対象のターゲットグループに Healthy なターゲットが存在しない場合**
  - ALBは処理すべき宛先がないと判断し、**503** を返します。
  - これは以下のようなケースでも発生します：
    - タスクが ECS でまだ起動していない
    - タスクがヘルスチェックに失敗している
    - ターゲットが登録されていない

---

### 📘 AWS 公式ドキュメントにも記載あり：
> If no targets are registered with a target group, or if all targets are deemed unhealthy, the load balancer responds with an HTTP 503 error.

[参考: ALB ドキュメント – Target health](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)

---

必要であれば、CloudWatch Logs の ALB アクセスログを有効にしておくと、503 エラーが発生したタイミングの詳細な情報を取得できます。