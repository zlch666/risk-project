# -*- coding: utf-8 -*-
"""
数据集梳理脚本（实训项目1 · 任务4）
================================================
读取企业工商注册数据与风险评级数据两张宽表，完成：
  1. 数据加载（统一 dtype=str，避免编号类字段被转成数字）
  2. 数据预览（按中文列名打印前 n 条 + 数据形状）
  3. 数据质量检查（缺失值、空值、异常取值）
  4. 分布统计（企业类别 / 经营状态 / 四类风险指标 / 12 项指标概况）

运行：venv\\Scripts\\python.exe dataset_process.py
      venv\\Scripts\\python.exe dataset_process.py --full     # 用全量 1w 条
"""
import argparse
import os
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# 全量文件与样本文件（命名以实际下发数据为准，脚本自动探测）
ENTERPRISE_FILES = [
    os.path.join(DATASET_DIR, "dwd_essential_info_commercial_reg_info.csv"),
    os.path.join(DATASET_DIR, "dwd_essential_info_commercial_reg_info_1w.csv"),
    os.path.join(DATASET_DIR, "dwd_essential_info_commercial_.csv"),
]
ENTERPRISE_SAMPLE = os.path.join(
    DATASET_DIR, "dwd_essential_info_commercial_reg_info_sample.csv")

RISK_FILES = [
    os.path.join(DATASET_DIR, "ads_company_rating_basis.csv"),
    os.path.join(DATASET_DIR, "ads_company_rating_basis_1w.csv"),
]
RISK_SAMPLE = os.path.join(DATASET_DIR, "ads_company_rating_basis_sample.csv")

# ── 字段映射：英文名 → 中文名（企业表关键字段）─────────────────────────────
ENTERPRISE_CN = {
    "id": "企业唯一标识",
    "firm_eid": "企业EID",
    "firm_id": "企业ID",
    "firm_name": "企业名称",
    "usc_code": "统一社会信用代码",
    "reg_no": "注册号",
    "org_no": "组织机构代码",
    "tax_no": "纳税人识别号",
    "firm_name_sh": "企业简称",
    "firm_name_en": "企业英文名",
    "firm_category": "企业类别",
    "ope_status": "经营状态",
    "legal_rep": "法定代表人",
    "legal_rep_id": "法定代表人证件号",
    "firm_type": "企业类型",
    "firm_org_type": "企业组织形式",
    "firm_properties": "企业性质",
    "est_date": "成立日期",
    "cancel_date": "注销日期",
    "cancel_reason": "注销原因",
    "rev_date": "核准日期",
    "reg_agency": "登记机关",
    "ind_econ_name": "国民经济行业",
    "appr_date": "批准日期",
    "emp_num": "员工人数",
    "insured_emp_num": "参保人数",
    "ope_address": "经营地址",
    "reg_address": "注册地址",
    "province": "省份",
    "city": "城市",
    "district": "区县",
    "bd_longitude": "百度经度",
    "bd_latitude": "百度纬度",
    "gd_longitude": "高德经度",
    "gd_latitude": "高德纬度",
    "reg_cap": "注册资本",
    "reg_cap_cur": "注册资本币种",
    "rec_cap": "实收资本",
    "ope_scope": "经营范围",
    "firm_scale": "企业规模",
    "parent_name": "母公司名称",
    "profile": "企业简介",
    "logo_url": "Logo地址",
    "is_history": "是否历史数据",
    "id_num": "序号",
}

# ── 字段映射：风险表 12 项指标 + 4 项企业属性 ───────────────────────────
RISK_CN = {
    "id": "企业唯一标识",
    "name": "企业名称",
    "cai_1": "近1年裁判次数",
    "cai_2": "近2年裁判次数",
    "cai_3": "近3年裁判次数",
    "s_an_1": "近1年立案数",
    "s_an_2": "近2年立案数",
    "s_an_3": "近3年立案数",
    "li_an_1": "近1年被立案次数",
    "li_an_2": "近2年被立案次数",
    "li_an_3": "近3年被立案次数",
    "zhi_1": "近1年被执行次数",
    "zhi_2": "近2年被执行次数",
    "zhi_3": "近3年被执行次数",
    "f_ren": "法定代表人",
    "zhuce_money": "注册资本",
    "jing_fan": "经营范围",
    "qiye_type": "企业类型",
    "id_num": "序号",
}

# 四类风险指标分组（用于统计1）
RISK_GROUPS = {
    "裁判类(cai)": ["cai_1", "cai_2", "cai_3"],
    "立案类(s_an)": ["s_an_1", "s_an_2", "s_an_3"],
    "被立案类(li_an)": ["li_an_1", "li_an_2", "li_an_3"],
    "被执行类(zhi)": ["zhi_1", "zhi_2", "zhi_3"],
}

# 枚举取值约定
ENUM_MAP = {
    "firm_category": {"E": "企业", "P": "个体户"},
    "ope_status": {"1": "在营", "2": "注销", "3": "吊销"},
}


def _pick(paths):
    """在候选路径里挑第一个存在的文件。"""
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _sep(title):
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)


# ══════════════════ 企业数据：加载 / 预览 / 统计 ══════════════════
def load_enterprise_data(use_sample=False):
    """读取企业工商 CSV，统一 dtype=str，避免编号类字段被转成数字。"""
    # 样本文件缺失时自动回退到全量文件（本次未下发 *_sample.csv）
    if use_sample and os.path.exists(ENTERPRISE_SAMPLE):
        path = ENTERPRISE_SAMPLE
    else:
        path = _pick(ENTERPRISE_FILES)
        if use_sample:
            print("[提示] 未找到样本文件，自动改用全量文件")
    if not path or not os.path.exists(path):
        raise FileNotFoundError(
            f"数据文件不存在，请把 CSV 放到 {DATASET_DIR}\n"
            f"  期望之一：{os.path.basename(ENTERPRISE_FILES[0])}")
    df = pd.read_csv(path, dtype=str, encoding="utf-8", low_memory=False)
    print(f"[企业数据] 加载完成：{os.path.basename(path)}")
    print(f"[企业数据] 共 {len(df)} 条记录，{len(df.columns)} 个字段")
    return df


def preview_enterprise(df, n=5):
    """按中文列名打印前 n 条，并输出数据形状。"""
    _sep(f"企业数据预览（前 {n} 条）")
    want = ["firm_name", "usc_code", "legal_rep", "reg_cap", "est_date",
            "ope_status", "firm_category", "ind_econ_name", "province", "city"]
    cols = [c for c in want if c in df.columns]
    show = df[cols].head(n).rename(columns=ENTERPRISE_CN)
    print(f"数据形状：{df.shape[0]} 行 × {df.shape[1]} 列")
    print(show.to_string(index=False, max_colwidth=18))


def check_enterprise_quality(df):
    """数据质量检查：缺失值最多的字段 + 完全空列。"""
    _sep("企业数据质量检查")
    miss = df.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=False)
    print(f"存在缺失的字段数：{len(miss)} / {len(df.columns)}")
    if len(miss):
        for col, cnt in miss.head(10).items():
            cn = ENTERPRISE_CN.get(col, col)
            print(f"  {col:<22}{cn:<16}缺失 {cnt:>6} 条"
                  f"（{cnt / len(df) * 100:.2f}%）")
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    print(f"完全空列：{empty_cols if empty_cols else '无'}")


def show_enterprise_category(df):
    """统计1：企业类别分布（E=企业，P=个体户）。"""
    _sep("统计1：企业类别分布（firm_category）")
    if "firm_category" not in df.columns:
        print("字段 firm_category 不存在，跳过")
        return
    vc = df["firm_category"].fillna("（空）").value_counts()
    total = len(df)
    for k, v in vc.items():
        label = ENUM_MAP["firm_category"].get(k, k)
        print(f"  {k} = {label:<6}{v:>7} 条  {v / total * 100:6.2f}%")
    print(f"  合计 {total} 条")


def show_enterprise_status(df):
    """统计2：经营状态分布（1=在营，2=注销，3=吊销）。"""
    _sep("统计2：经营状态分布（ope_status）")
    if "ope_status" not in df.columns:
        print("字段 ope_status 不存在，跳过")
        return
    vc = df["ope_status"].fillna("（空）").value_counts()
    total = len(df)
    for k, v in vc.items():
        label = ENUM_MAP["ope_status"].get(k, k)
        print(f"  {k} = {label:<6}{v:>7} 条  {v / total * 100:6.2f}%")
    print(f"  合计 {total} 条")


# ══════════════════ 风险数据：加载 / 预览 / 统计 ══════════════════
def load_risk_data(use_sample=False):
    """读取风险评级 CSV，统一 dtype=str。"""
    if use_sample and os.path.exists(RISK_SAMPLE):
        path = RISK_SAMPLE
    else:
        path = _pick(RISK_FILES)
        if use_sample:
            print("[提示] 未找到样本文件，自动改用全量文件")
    if not path or not os.path.exists(path):
        raise FileNotFoundError(
            f"数据文件不存在，请把 CSV 放到 {DATASET_DIR}\n"
            f"  期望之一：{os.path.basename(RISK_FILES[0])}")
    df = pd.read_csv(path, dtype=str, encoding="utf-8", low_memory=False)
    print(f"[风险数据] 加载完成：{os.path.basename(path)}")
    print(f"[风险数据] 共 {len(df)} 条记录，{len(df.columns)} 个字段")
    return df


def preview_risk(df, n=5):
    """按中文列名打印前 n 条。"""
    _sep(f"风险数据预览（前 {n} 条）")
    want = ["name", "cai_1", "cai_2", "cai_3", "s_an_1", "li_an_1", "zhi_1",
            "qiye_type", "zhuce_money"]
    cols = [c for c in want if c in df.columns]
    show = df[cols].head(n).rename(columns=RISK_CN)
    print(f"数据形状：{df.shape[0]} 行 × {df.shape[1]} 列")
    print(show.to_string(index=False, max_colwidth=18))


def show_risk_indicators(df):
    """统计1：四类风险指标（裁判 / 立案 / 被立案 / 被执行）均值概览。"""
    _sep("统计1：四类风险指标均值概览")
    rows = []
    for group, cols in RISK_GROUPS.items():
        present = [c for c in cols if c in df.columns]
        if not present:
            continue
        num = df[present].apply(pd.to_numeric, errors="coerce")
        rows.append({
            "维度": group,
            "字段数": len(present),
            "均值": round(num.mean().mean(), 4),
            "最大": int(num.max().max()) if num.notna().any().any() else 0,
            "合计": int(num.sum().sum(skipna=True)),
        })
    if rows:
        print(pd.DataFrame(rows).to_string(index=False))
    else:
        print("12 项指标字段均不存在，跳过")


def show_risk_summary(df):
    """统计2：12 项指标总体概况（非零占比 + 零值企业数）。"""
    _sep("统计2：12 项指标总体概况")
    all_cols = [c for cols in RISK_GROUPS.values() for c in cols]
    present = [c for c in all_cols if c in df.columns]
    if not present:
        print("12 项指标字段均不存在，跳过")
        return
    num = df[present].apply(pd.to_numeric, errors="coerce")
    rows = []
    for c in present:
        s = num[c]
        nonzero = int((s.fillna(0) > 0).sum())
        rows.append({
            "字段": c,
            "中文名": RISK_CN.get(c, c),
            "均值": round(float(s.mean()), 4) if s.notna().any() else 0,
            "最大值": int(s.max()) if s.notna().any() else 0,
            "非零企业数": nonzero,
            "非零占比": f"{nonzero / len(df) * 100:.2f}%",
        })
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="实训项目1 数据集梳理")
    ap.add_argument("--full", action="store_true", help="使用全量数据（默认用样本）")
    ap.add_argument("--enterprise-only", action="store_true", help="只跑企业表")
    ap.add_argument("--risk-only", action="store_true", help="只跑风险表")
    args = ap.parse_args()

    print("=" * 78)
    print("  数据集梳理  ·  企业风险评估系统（实训项目 1 · 任务 4）")
    print(f"  数据目录：{DATASET_DIR}")
    print(f"  数据模式：{'全量' if args.full else '样本'}")
    print(f"  pandas  {pd.__version__}   Python {sys.version.split()[0]}")
    print("=" * 78)

    if not args.risk_only:
        try:
            ent = load_enterprise_data(use_sample=not args.full)
            preview_enterprise(ent)
            check_enterprise_quality(ent)
            show_enterprise_category(ent)
            show_enterprise_status(ent)
        except FileNotFoundError as e:
            print(f"\n[跳过企业表] {e}")

    if not args.enterprise_only:
        try:
            risk = load_risk_data(use_sample=not args.full)
            preview_risk(risk)
            show_risk_indicators(risk)
            show_risk_summary(risk)
        except FileNotFoundError as e:
            print(f"\n[跳过风险表] {e}")

    print("\n" + "=" * 78)
    print("  梳理完成")
    print("=" * 78)


if __name__ == "__main__":
    main()
