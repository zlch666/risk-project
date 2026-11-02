# -*- coding: utf-8 -*-
"""
数据库连接测试（实训项目1 · 任务2）
================================================
验证 risk_user 能否连上 risk_assessment，并打印版本与库列表。

安全约定（注意事项第 3 条：账号密码不得硬编码）：
  连接参数从环境变量读取，未设置时回落到 .env 文件，最终才用默认值。
  代码仓库里只提交 .env.example，不提交 .env。
"""
import os
from pathlib import Path

import pymysql

BASE_DIR = Path(__file__).resolve().parent


def load_env_file():
    """极简 .env 读取：KEY=VALUE，忽略注释与空行。"""
    f = BASE_DIR / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env_file()

CONF = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "risk_user"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "risk_assessment"),
    "charset": "utf8mb4",
}


def main():
    print("=" * 60)
    print("  MySQL 连接测试 · 企业风险评估系统")
    print("=" * 60)
    print(f"目标：{CONF['user']}@{CONF['host']}:{CONF['port']}/{CONF['database']}")
    if not CONF["password"]:
        print("[提示] 未配置 DB_PASSWORD，请复制 .env.example 为 .env 后填写")
        return 2
    try:
        conn = pymysql.connect(**CONF)
    except Exception as e:
        print(f"[失败] {type(e).__name__}: {e}")
        return 1

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            print(f"[成功] MySQL 版本：{cur.fetchone()[0]}")
            cur.execute("SELECT DATABASE()")
            print(f"[成功] 当前数据库：{cur.fetchone()[0]}")
            cur.execute("SHOW DATABASES")
            dbs = [r[0] for r in cur.fetchall()]
            print(f"[成功] 可见数据库（{len(dbs)} 个）：{', '.join(dbs)}")
            cur.execute("SHOW GRANTS FOR CURRENT_USER()")
            print("[权限]")
            for (g,) in cur.fetchall():
                print("   " + g)
            cur.execute("SHOW VARIABLES LIKE 'character_set_server'")
            print(f"[字符集] {cur.fetchone()}")
    print("=" * 60)
    print("  连接测试通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
