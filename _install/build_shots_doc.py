# -*- coding: utf-8 -*-
"""《环境配置与运行记录》：把 7 张截图编入 docx，每张带说明。"""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

SHOT = Path(r"D:\risk_project\截图")
OUT = r"C:\Users\34701\Desktop\249990326-蒲小龙-环境配置与运行记录.docx"

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.0)
    s.left_margin = s.right_margin = Cm(2.0)


def nosnap(p):
    pPr = p._p.get_or_add_pPr()
    el = pPr.find(qn("w:snapToGrid"))
    if el is None:
        el = pPr.makeelement(qn("w:snapToGrid"), {}); pPr.append(el)
    el.set(qn("w:val"), "0")


def H(t, lv=1):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(10 if lv == 1 else 6); pf.space_after = Pt(4)
    pf.keep_with_next = True
    r = p.add_run(t)
    r.font.size = Pt(13.5 if lv == 1 else 11); r.bold = True
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    nosnap(p)


def P(t, size=10.5, ind=True, color=None, after=4):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0); pf.space_after = Pt(after)
    pf.line_spacing = 1.3
    if ind: pf.first_line_indent = Pt(21)
    r = p.add_run(t)
    r.font.size = Pt(size); r.font.name = "Times New Roman"
    if color: r.font.color.rgb = color
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    nosnap(p)


def CAP(t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(10)
    r = p.add_run(t); r.font.size = Pt(9); r.bold = True
    r.font.name = "Times New Roman"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    nosnap(p)


def IMG(name, cap):
    path = SHOT / name
    if not path.exists():
        P(f"（缺图：{name}）", color=RGBColor(0xB4, 0x35, 0x2E))
        return
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Cm(16.6))
    CAP(cap)


# ── 标题 ──
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(2)
r = p.add_run("环境配置与运行记录")
r.font.size = Pt(18); r.bold = True
r.font.name = "Times New Roman"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
nosnap(p)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(10)
r = p.add_run("企业风险评估系统 · 实训项目 1 ｜ 蒲小龙 249990326 24 智科 2 班")
r.font.size = Pt(10)
r.font.name = "Times New Roman"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
nosnap(p)

P("本记录对应实训任务 1（环境安装与配置验逐项截图）与任务 4（脚本运行结果），"
  "共 7 张证据图。所用命令均在 D:\\risk_project 目录下、已激活 venv 的环境中实际执行，"
  "图中输出为原始结果。")

# ══════════ 一、环境验证 ══════════
H("一、环境安装与配置验证")

H("1.1　Python 版本与解释器路径", 2)
P("验证 Python 版本不低于 3.10，且虚拟环境解释器指向工程目录内的 venv，"
  "而不是系统全局解释器。")
IMG("截图01_Python版本与虚拟环境路径.png", "图 1　python --version 与 sys.prefix 输出")

H("1.2　虚拟环境与依赖版本", 2)
P("激活虚拟环境后命令行前缀出现 (venv)；pip 指向 venv 内的站点包目录；"
  "Django、pandas、PyMySQL 三个关键依赖版本符合要求（Django 4.2 LTS、pandas ≥1.5、PyMySQL ≥1.0）。")
IMG("截图02_虚拟环境与依赖版本.png", "图 2　venv 激活状态与关键依赖版本")

H("1.3　MySQL 服务与数据库", 2)
P("MySQL 8.0.28 已以 risk_user 账号成功登录，字符集为 utf8mb4；"
  "数据库列表中存在本次实训创建的 risk_assessment；该账号仅对 risk_assessment 拥有权限，"
  "符合最小权限原则。")
IMG("截图03_MySQL版本与数据库列表.png", "图 3　MySQL 版本、数据库列表与 risk_user 授权")

H("1.4　依赖清单", 2)
P("requirements.txt 由 pip freeze 导出，可直接用于环境重建。")
IMG("截图04_requirements依赖清单.png", "图 4　requirements.txt 内容")

# ══════════ 二、运行结果 ══════════
doc.add_page_break()
H("二、数据集梳理脚本运行结果")
P("执行 python dataset_process.py --full，全量读取两张宽表，输出数据规模、字段预览、"
  "缺失值统计、类别分布与四类指标统计，共 93 行，分 3 页截图。")

H("2.1　数据加载与预览", 2)
P("两张表均为 10000 条记录，企业表 59 个字段、风险表 19 个字段，与指导书一致。"
  "预览按中文列名输出，可直观看到统一社会信用代码、法定代表人、注册资本、成立日期、"
  "经营状态等关键字段的取值。")
IMG("截图05_脚本运行结果_P1of3.png", "图 5　企业数据加载、预览与质量检查（第 1 / 3 页）")

H("2.2　质量检查与分布统计", 2)
P("企业表 41 个字段存在缺失，其中 17 个字段完全为空；企业类别全部为 E（个体户 0 条）；"
  "经营状态以在营为主（61.46%），注销 26.87%、吊销 11.67%。")
IMG("截图05_脚本运行结果_P2of3.png", "图 6　类别/状态分布与风险数据预览（第 2 / 3 页）")

H("2.3　四类风险指标统计", 2)
P("裁判、立案、被立案三类指标均值约 9.5，被执行类约 6.6；12 项指标最大值 25，"
  "被执行类上限 20。需要注意的是三类指标的非零占比均为 100%，与指导书“多数企业指标为 0”"
  "的预期不符，该差异已在《数据集梳理记录》问题 6 中说明。")
IMG("截图05_脚本运行结果_P3of3.png", "图 7　四类指标均值与 12 项指标概况（第 3 / 3 页）")

# ══════════ 三、说明 ══════════
H("三、结论")
P("1. Python、虚拟环境、MySQL、依赖四项均通过验证，环境可用。")
P("2. dataset_process.py 可在全量数据上一次性跑通，输出覆盖任务要求的全部统计项。")
P("3. 截图中暴露的两个问题（17 个空字段、风险指标无零值）已写入《数据集梳理记录》，"
  "作为后续数据导入与风险评分算法设计的输入。")

doc.save(OUT)
print("saved:", OUT)
print("图片张数:", len([1 for n in ["截图01_Python版本与虚拟环境路径.png",
      "截图02_虚拟环境与依赖版本.png", "截图03_MySQL版本与数据库列表.png",
      "截图04_requirements依赖清单.png", "截图05_脚本运行结果_P1of3.png",
      "截图05_脚本运行结果_P2of3.png", "截图05_脚本运行结果_P3of3.png"]
      if (SHOT / n).exists()]))
