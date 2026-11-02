# 企业风险评估系统 · 实训项目 1

环境安装与数据集梳理（课程：模型开发综合实训 20262011）

## 目录结构

```
risk_project/
├── venv/                    虚拟环境（Python 3.11.9）
├── dataset/                 数据集目录（CSV + 字段定义 xlsx）
├── dataset_process.py       数据集梳理脚本（任务 4）
├── requirements.txt         依赖清单
└── README.md
```

## 环境

| 组件 | 版本 | 位置 |
|---|---|---|
| Python | 3.11.9 | C:\Users\34701\AppData\Local\Programs\Python\Python311 |
| 虚拟环境 | venv | D:\risk_project\venv |
| Django | 4.2 | venv 内 |
| pandas | 3.1.0 | venv 内 |
| PyMySQL | 1.2.3 | venv 内 |
| MySQL | 8.0.28 | D:\mysql8 |

## 运行

```bat
cd /d D:\risk_project
venv\Scripts\activate
python dataset_process.py            :: 样本
python dataset_process.py --full     :: 全量 1 万条
```

## 数据库

```sql
CREATE DATABASE risk_assessment DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'risk_user'@'localhost' IDENTIFIED BY 'risk123456';
GRANT ALL PRIVILEGES ON risk_assessment.* TO 'risk_user'@'localhost';
FLUSH PRIVILEGES;
```
