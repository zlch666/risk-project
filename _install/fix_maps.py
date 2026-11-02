# -*- coding: utf-8 -*-
"""按真实字段名修正 dataset_process.py 的映射字典，并跑出统计。"""
import re
from pathlib import Path

import pandas as pd

P = Path(r"D:\risk_project\dataset_process.py")
s = P.read_text(encoding="utf-8")

# ── 企业表映射：按真实 59 列重写 ──
ENT = '''ENTERPRISE_CN = {
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
}'''

RISK = '''RISK_CN = {
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
}'''

s = re.sub(r"ENTERPRISE_CN = \{.*?\n\}", ENT, s, count=1, flags=re.S)
s = re.sub(r"RISK_CN = \{.*?\n\}", RISK, s, count=1, flags=re.S)

# ── 文件名候选：加入实际下发的名字 ──
s = s.replace(
    '    os.path.join(DATASET_DIR, "dwd_essential_info_commercial_reg_info_1w.csv"),',
    '    os.path.join(DATASET_DIR, "dwd_essential_info_commercial_reg_info_1w.csv"),\n'
    '    os.path.join(DATASET_DIR, "dwd_essential_info_commercial_.csv"),')

# ── 预览列：用真实存在的字段 ──
s = s.replace(
    '    cols = [c for c in ENTERPRISE_CN if c in df.columns][:10]',
    '    want = ["firm_name", "usc_code", "legal_rep", "reg_cap", "est_date",\n'
    '            "ope_status", "firm_category", "ind_econ_name", "province", "city"]\n'
    '    cols = [c for c in want if c in df.columns]')
s = s.replace(
    '    cols = [c for c in RISK_CN if c in df.columns][:10]',
    '    want = ["name", "cai_1", "cai_2", "cai_3", "s_an_1", "li_an_1", "zhi_1",\n'
    '            "qiye_type", "zhuce_money"]\n'
    '    cols = [c for c in want if c in df.columns]')

P.write_text(s, encoding="utf-8")
print("映射字典已按真实字段改写")
