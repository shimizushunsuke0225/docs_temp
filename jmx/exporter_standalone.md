ありがとうございます。  
これまで `-javaagent:jmx_prometheus_javaagent.jar=9404:/path/config.yaml` のように **Javaプロセスの起動引数**で `jmx_exporter` を組み込んでいたということですね。

今回はそれを **Javaアプリとは独立して、OS上の常駐プロセスとして起動したい**という意図だと理解しました。  
この目的に適しているのは以下のような「**Standalone JMX Exporter（Exporter単独プロセス）」の構成です。

---

## ✅ JMX ExporterをOS上の常駐プロセスとして起動する方法（Standaloneモード）

JavaアプリからJMX経由でメトリクスを取得する形になります。

---

### 📌 前提条件

- Javaアプリ側に **JMX Remote** が有効であること
- `jmx_prometheus_httpserver-*.jar` を使う（`javaagent`ではない）

---

### 🛠️ 手順

#### 1. Javaアプリ側にJMX Remoteを有効にする

アプリの起動時に以下のようなオプションを付与：

```bash
-Dcom.sun.management.jmxremote
-Dcom.sun.management.jmxremote.port=9010
-Dcom.sun.management.jmxremote.authenticate=false
-Dcom.sun.management.jmxremote.ssl=false
-Djava.rmi.server.hostname=127.0.0.1
```

> ⚠️ `rmi.hostname` はExporterから接続できるように設定してください。リモートで取得するために必須です。

---

#### 2. Exporter側でHTTP Serverとして起動（9404番ポート）

```bash
wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_httpserver/0.20.0/jmx_prometheus_httpserver-0.20.0-jar-with-dependencies.jar
```

起動コマンド：

```bash
java -jar jmx_prometheus_httpserver-0.20.0-jar-with-dependencies.jar 9404 config.yaml
```

- `9404`：Exporterが待ち受けるHTTPポート（CloudWatch Agentが叩く用）
- `config.yaml`：どのJMXメトリクスを取得するか定義する設定ファイル（今までと同じ形式）

---

#### 3. CloudWatch Agentから `localhost:9404/metrics` をPull

CloudWatch Agent の設定は変更不要でそのまま使えます。

---

## 🧾 config.yaml の例（JMX Remote用）

```yaml
startDelaySeconds: 0
jmxUrl: service:jmx:rmi:///jndi/rmi://127.0.0.1:9010/jmxrmi
username:
password:
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  - pattern: "java.lang:type=MemoryPool,name=(.*)"
    name: jvm_memory_pool_bytes_used
    type: GAUGE
    attrNameSnakeCase: true
    value: usage.used
    labels:
      pool: "$1"
```

> `jmxUrl` で Javaアプリの JMX ポートと接続

---

## ✅ systemd サービスとして常駐させる（オプション）

```ini
# /etc/systemd/system/jmx_exporter.service
[Unit]
Description=Prometheus JMX Exporter
After=network.target

[Service]
ExecStart=/usr/bin/java -jar /opt/jmx_exporter/jmx_prometheus_httpserver-0.20.0-jar-with-dependencies.jar 9404 /opt/jmx_exporter/config.yaml
User=ec2-user
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable jmx_exporter
sudo systemctl start jmx_exporter
```

---

## ✅ 構成図

```
[Javaバッチ] ←(JMX 9010)→ [JMX Exporter (9404)] ←GET− [CloudWatch Agent]
```

---

## 🔒 セキュリティ補足

- 本番環境では `jmxremote.authenticate=true` でユーザー認証を設定してください。
- 必要であれば JMX にファイアウォール制限やSSHトンネル経由の制限を設けましょう。

---

必要であれば、`config.yaml` や `systemd` ファイルのテンプレートもお渡しします。  
この方向性で問題なければ、構成を一緒に固めましょうか？