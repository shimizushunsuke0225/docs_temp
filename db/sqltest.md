psql mydatabase -c "
INSERT INTO users(name,email)
SELECT substr(md5(random()::text),1,10),
       substr(md5(random()::text||clock_timestamp()::text),1,12) || '@example.com'
FROM generate_series(1,1000000);
"


pgbench -f users_workload.sql \
        -c 200 \        # 同時クライアント数
        -j 8  \         # スレッド数 (EC2 vCPU 数程度)
        -T 900 \        # テスト時間 900 秒 (=15 分)
        mydatabase
        