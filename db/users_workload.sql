-- users_workload.sql -----------------------------
BEGIN;

-- ① ランダム行を参照（読込み負荷）
SELECT * FROM users
 WHERE id = floor(random() * (SELECT max(id) FROM users)) + 1;

-- ② 既存行を更新（WAL 発生）
UPDATE users
   SET name = substr(md5(random()::text),1,10)
 WHERE id  = floor(random() * (SELECT max(id) FROM users)) + 1;

-- ③ 新規行を挿入（UNIQUE 制約に注意）
INSERT INTO users(name, email)
VALUES (
    substr(md5(random()::text),1,10),
    substr(md5(random()::text||clock_timestamp()::text),1,12) || '@example.com'
);

COMMIT;
-- -----------------------------------------------
