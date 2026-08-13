from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


RUN = Path(__file__).resolve().parents[2]
OUT = RUN / "paper"
FIG = RUN / "outputs" / "figures_v2"
RESULTS = json.loads((RUN / "outputs" / "data" / "final_results.json").read_text(encoding="utf-8"))

TITLE = "周期边界下导电介质填充的连通概率界与整数成本优化"
BODY_FONT = "SimSun"
HEAD_FONT = "SimHei"
LATIN_FONT = "Times New Roman"
MATH_FONT = "Cambria Math"
INK = "000000"
HEADER_FILL = "E7EEF3"


def set_run_font(run, east=BODY_FONT, latin=LATIN_FONT, size=12, bold=False, italic=False, color=INK):
    run.font.name = latin
    run._element.get_or_add_rPr()
    fonts = run._element.rPr.get_or_add_rFonts()
    fonts.set(qn("w:eastAsia"), east)
    fonts.set(qn("w:ascii"), latin)
    fonts.set(qn("w:hAnsi"), latin)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    flag = OxmlElement("w:tblHeader")
    flag.set(qn("w:val"), "true")
    tr_pr.append(flag)


def set_cell_margins(cell, top=80, start=110, bottom=80, end=110):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def shade_cell(cell, fill=HEADER_FILL):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_table_geometry(table, widths_cm):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    total = int(sum(widths_cm) / 2.54 * 1440)
    tbl_w.set(qn("w:w"), str(total))
    tbl_w.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_cm:
        dxa = int(width / 2.54 * 1440)
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(dxa))
        grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            dxa = int(widths_cm[idx] / 2.54 * 1440)
            tc_w = cell._tc.get_or_add_tcPr().first_child_found_in("w:tcW")
            tc_w.set(qn("w:w"), str(dxa))
            tc_w.set(qn("w:type"), "dxa")
            cell.width = Cm(widths_cm[idx])
            set_cell_margins(cell)


class Paper:
    def __init__(self):
        self.doc = Document()
        self.md: list[str] = []
        self.fig_no = 0
        self.table_no = 0
        self.eq_no = 0
        self._setup()

    def _setup(self):
        doc = self.doc
        sec = doc.sections[0]
        sec.page_width = Cm(21)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(2.35)
        sec.bottom_margin = Cm(2.25)
        sec.left_margin = Cm(2.45)
        sec.right_margin = Cm(2.35)
        sec.header_distance = Cm(1.2)
        sec.footer_distance = Cm(1.25)

        normal = doc.styles["Normal"]
        normal.font.name = LATIN_FONT
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        normal.font.size = Pt(11.5)
        normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal.paragraph_format.first_line_indent = Cm(0.74)
        normal.paragraph_format.space_after = Pt(3)
        normal.paragraph_format.line_spacing = 1.22

        for name, size, before, after in (("Heading 1", 15, 10, 5), ("Heading 2", 13, 7, 4), ("Heading 3", 12, 5, 3)):
            style = doc.styles[name]
            style.font.name = LATIN_FONT
            style._element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_FONT)
            style.font.size = Pt(size)
            style.font.bold = True
            style.font.color.rgb = RGBColor(0, 0, 0)
            style.paragraph_format.space_before = Pt(before)
            style.paragraph_format.space_after = Pt(after)
            style.paragraph_format.keep_with_next = True
            style.paragraph_format.first_line_indent = Cm(0)

        if "Figure Caption" not in [s.name for s in doc.styles]:
            cap = doc.styles.add_style("Figure Caption", WD_STYLE_TYPE.PARAGRAPH)
        else:
            cap = doc.styles["Figure Caption"]
        cap.font.name = LATIN_FONT
        cap._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        cap.font.size = Pt(10)
        cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(5)
        cap.paragraph_format.keep_with_next = False
        cap.paragraph_format.first_line_indent = Cm(0)

        footer = sec.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        self._append_field(p, "PAGE", "1")

    @staticmethod
    def _append_field(p, instruction: str, display: str):
        run = p.add_run()
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = instruction
        separate = OxmlElement("w:fldChar")
        separate.set(qn("w:fldCharType"), "separate")
        text = OxmlElement("w:t")
        text.text = display
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        for node in (begin, instr, separate, text, end):
            run._r.append(node)
        set_run_font(run, size=10)

    def meta_line(self):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(4)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run("参赛组别：________    参赛队号：CM________")
        set_run_font(r, size=10.5)

    def title(self):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        r = p.add_run(TITLE)
        set_run_font(r, east=HEAD_FONT, size=18, bold=True)
        self.md += [f"# {TITLE}", ""]

    def abstract_heading(self):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("摘要")
        set_run_font(r, east=HEAD_FONT, size=15, bold=True)
        self.md += ["## 摘要", ""]

    def paragraph(self, text: str, *, first=True, size=11.5, after=3, keep=False):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74) if first else Cm(0)
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.line_spacing = 1.22
        p.paragraph_format.keep_with_next = keep
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(text)
        set_run_font(r, size=size)
        self.md += [text, ""]
        return p

    def keyword(self, text: str):
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(3)
        r = p.add_run("关键词：")
        set_run_font(r, east=HEAD_FONT, size=11.5, bold=True)
        r = p.add_run(text)
        set_run_font(r, size=11.5)
        self.md += [f"**关键词：** {text}", ""]

    def page_break(self):
        p = self.doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)

    def heading(self, text: str, level=1):
        p = self.doc.add_paragraph(style=f"Heading {level}")
        r = p.add_run(text)
        set_run_font(r, east=HEAD_FONT, size={1: 15, 2: 13, 3: 12}[level], bold=True)
        self.md += [f"{'#' * (level + 1)} {text}", ""]

    def equation(self, expression: str, explanation: str | None = None):
        self.eq_no += 1
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_together = True
        p_pr = p._p.get_or_add_pPr()
        tabs = OxmlElement("w:tabs")
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), "right")
        tab.set(qn("w:pos"), "9000")
        tabs.append(tab)
        p_pr.append(tabs)
        math_para = OxmlElement("m:oMathPara")
        omath = OxmlElement("m:oMath")
        mr = OxmlElement("m:r")
        mt = OxmlElement("m:t")
        mt.text = expression
        mr.append(mt)
        omath.append(mr)
        math_para.append(omath)
        p._p.append(math_para)
        r = p.add_run(f"\t({self.eq_no})")
        set_run_font(r, latin=MATH_FONT, size=11.5)
        self.md += [f"$$ {expression} \tag{{{self.eq_no}}} $$", ""]
        if explanation:
            self.paragraph(explanation)

    def figure(self, filename: str, caption: str, width_cm=15.5):
        self.fig_no += 1
        p = self.doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(1)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        picture = p.add_run().add_picture(str(FIG / filename), width=Cm(width_cm))
        picture._inline.docPr.set("title", f"图{self.fig_no} {caption}")
        picture._inline.docPr.set("descr", caption)
        cap = self.doc.add_paragraph(style="Figure Caption")
        cap.paragraph_format.keep_together = True
        r = cap.add_run(f"图{self.fig_no}  {caption}")
        set_run_font(r, size=10)
        self.md += [f"![图{self.fig_no} {caption}](../outputs/figures_v2/{filename})", "", f"图{self.fig_no}  {caption}", ""]

    def table(self, caption: str, headers, rows, widths_cm, aligns=None, font_size=9.5):
        self.table_no += 1
        cap = self.doc.add_paragraph(style="Figure Caption")
        cap.paragraph_format.space_before = Pt(4)
        cap.paragraph_format.space_after = Pt(2)
        cap.paragraph_format.keep_with_next = True
        r = cap.add_run(f"表{self.table_no}  {caption}")
        set_run_font(r, size=10)
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        set_table_geometry(table, widths_cm)
        set_repeat_table_header(table.rows[0])
        aligns = aligns or [WD_ALIGN_PARAGRAPH.CENTER] * len(headers)
        for idx, h in enumerate(headers):
            cell = table.rows[0].cells[idx]
            cell.text = ""
            shade_cell(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(h))
            set_run_font(r, east=HEAD_FONT, size=font_size, bold=True)
        for row in rows:
            cells = table.add_row().cells
            for idx, value in enumerate(row):
                cell = cells[idx]
                cell.text = ""
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.05
                p.alignment = aligns[idx]
                r = p.add_run(str(value))
                set_run_font(r, size=font_size)
        set_table_geometry(table, widths_cm)
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(1)
        spacer.paragraph_format.first_line_indent = Cm(0)

        self.md += [f"**表{self.table_no}  {caption}**", ""]
        self.md.append("| " + " | ".join(map(str, headers)) + " |")
        self.md.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            self.md.append("| " + " | ".join(str(v) for v in row) + " |")
        self.md.append("")

    def code_block(self, code: str):
        for line in code.splitlines():
            p = self.doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            r = p.add_run(line or " ")
            set_run_font(r, east="Microsoft YaHei", latin="Consolas", size=7.4)
        self.md += ["```python", code, "```", ""]

    def save(self, docx: Path, md: Path):
        props = self.doc.core_properties
        props.title = TITLE
        props.subject = "2026华数杯A题赛后研究与复盘稿"
        props.author = ""
        props.last_modified_by = ""
        self.doc.save(docx)
        md.write_text("\n".join(self.md), encoding="utf-8")


def q1_result_rows():
    rows = []
    for item in RESULTS["Q1"]:
        path = "-".join(str(x).replace("LEFT", "左面").replace("RIGHT", "右面") for x in item["conductive_path_1_based"]) if item["connected"] else "无"
        rows.append([item["group"], item["row_count"], item["edge_count"], item["left_contact_count"], item["right_contact_count"], "导通" if item["connected"] else "不导通", path])
    return rows


def q1_cert_rows():
    rows = []
    for item in RESULTS["Q1"]:
        for c in item["path_certificates"]:
            if c["type"] == "interior_side_to_side":
                s, t = c["segment_parameters"]
                rows.append([item["group"], f"{c['from']}-{c['to']}", f"{c['axis_distance_nm']:.3f}", f"{s:.3f}", f"{t:.3f}", "通过"])
    return rows


def build_paper():
    OUT.mkdir(parents=True, exist_ok=True)
    p = Paper()
    p.meta_line()
    p.title()
    p.abstract_heading()
    p.paragraph("本文研究周期立方微构体中导电介质的左右导通判定、随机填充概率估计与成本优化问题。针对附件给出的确定性构型，将每个平端圆柱视为图节点，以介质间最短距离和介质—电极距离为连边准则；对胶囊超集给出的候选边，再以轴段内部最短点参数作为平端圆柱侧面接触证书。针对随机填充，利用周期边界产生的单粒子直接贯通事件构造总导通概率下界，并对“无直接贯通但仍存在通路”的剩余事件建立终端薄壳联合上界。最后在整数域内完整枚举低成本方案，分别讨论允许某类介质数量为零和两类介质均为正两种题意口径。")
    p.paragraph("结果表明：附件组1不导通，组2和组3导通，显式通路分别为左面-2-12-24-39-右面和左面-63-264-216-351-右面。A 的体积分数为0.50%、0.60%、0.70%和1.00%时，仅直接贯通事件已使不导通概率上界分别降至10^-45.20、10^-54.13、10^-63.20和10^-90.27量级。仅填充A时，7根A的总导通概率上界为0.872279，8根A的直接贯通概率下界为0.904810，故达到90%导通概率的最小数量为8根，对应体积分数0.01131%，按百分号后两位报告为0.01%。")
    p.paragraph("混合填充中，若允许某类介质数量为零，非负整数域最优方案为0A+57B，成本0.09550元；若“同时填充”要求两类介质均出现，则正混合域最优方案为1A+50B，成本0.09862元。全文区分精确概率、严格下界和严格上界，阈值与最优性结论均由相邻不可行方案的上界证据闭合。")
    p.keyword("周期边界；随机几何图；导通概率界；联合界；整数优化")
    p.page_break()

    p.heading("1  问题重述与问题分析")
    p.heading("1.1  问题背景与研究对象", 2)
    p.paragraph("题目给定边长L=10000 nm的立方微构体，左右带电面位于x=-5000 nm与x=5000 nm。当导电介质之间或介质与带电面的表面最短距离不超过g=1.8 nm时，视为接触导通。介质A为高度H=5000 nm、半径r_A=30 nm的平端直圆柱；介质B为半径r_B=200 nm的球。边界采用周期平移截断规则，即越过边界的部分从对侧进入且仍属于同一导体。图1概括了几何对象和接触口径。")
    p.figure("01_problem_geometry.png", "问题几何、介质类型与周期边界示意", 15.3)
    p.heading("1.2  四个问题的输入、输出与难点", 2)
    p.paragraph("问题一的输入是附件中的三组圆柱轴段坐标，输出是每组是否导通及可复核的通路；难点在于平端圆柱不能直接等同于端部为半球的胶囊体。问题二将确定性坐标改为随机位置和随机方向，要求计算四个体积分数下的导通概率。问题三寻找仅填充A且导通概率不低于90%的最低填充率，需要同时证明候选值充分和前一整数不足。问题四加入B及材料成本，形成带概率约束的二元整数优化，并存在“是否允许某类介质数量为零”的题意歧义。")
    p.heading("1.3  总体技术路线", 2)
    p.paragraph("本文把四问组织为三个层次：第一层为确定性几何图和路径证书；第二层为所有随机问题共享的直接贯通下界与非直接通路上界；第三层为基于概率界的整数阈值和成本优化。该结构使Q2-Q4共享同一母模型，避免每问重复定义概率口径。技术路线如图2所示。")
    p.figure("02_workflow.png", "四问依赖关系与总体技术路线", 15.3)

    p.heading("2  模型假设、符号与量纲")
    p.heading("2.1  题面条件与补充假设", 2)
    p.table("题面条件、补充假设及失效影响", ["类别", "内容", "使用位置", "改变后的影响"], [
        ["题面条件", "每行附件数据表示一个A；边界越界部分周期平移", "Q1-Q4", "改变介质身份或周期解释会改变全部结果"],
        ["几何口径", "Q1保持附件轴段的截断状态，不擅自延长为5000 nm", "Q1", "延长会制造非真实接触边"],
        ["补充假设", "介质中心独立且在立方体内均匀分布", "Q2-Q4", "排斥或团聚会破坏独立乘积式"],
        ["补充假设", "A的轴向独立且各向同性", "Q2-Q4", "取向偏置会改变q_A及整数阈值"],
        ["补充假设", "随机介质允许重叠，忽略制造排斥", "Q2-Q4", "不可重叠时需改用相关随机几何模型"],
    ], [2.2, 6.2, 2.4, 5.1], aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT], font_size=9)
    p.heading("2.2  主要符号", 2)
    p.table("主要符号及含义", ["符号", "含义", "取值或单位"], [
        ["L", "立方体边长", "10000 nm"], ["g", "表面导通阈值", "1.8 nm"],
        ["H, r_A", "介质A的高度与半径", "5000 nm, 30 nm"], ["r_B", "介质B半径", "200 nm"],
        ["n_A, n_B", "A、B填充数量", "非负整数"], ["a_x", "粒子在x方向的支撑半宽", "nm"],
        ["D", "至少一个粒子直接贯通事件", "事件"], ["T", "整体左右导通事件", "事件"],
        ["S_i^L, S_i^R", "粒子i未越界但接触左/右电极的剩余薄壳事件", "事件"],
        ["P_dir", "直接贯通事件D的概率", "[0,1]"], ["C", "材料成本", "元"],
    ], [2.7, 8.7, 4.5], aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER], font_size=9.4)
    p.heading("2.3  体积与成本换算", 2)
    p.equation("V_A=pi*r_A^2*H=1.4137167e7 nm^3,  V_B=4*pi*r_B^3/3=3.3510322e7 nm^3")
    p.equation("C=1.05*V_A*n_A/1e9+0.05*V_B*n_B/1e9=0.0148440253*n_A+0.0016755161*n_B")
    p.paragraph("式(1)按真实圆柱与球体积计算，式(2)把nm^3换算为um^3。所有数量先在整数域内求解，体积分数仅作为结果的物理表达，不用四舍五入后的体积分数反推粒子数。")

    p.heading("3  问题一：确定性构型的几何连通模型")
    p.heading("3.1  附件数据审计", 2)
    p.paragraph("三组附件分别包含12、49和535个介质A。轴段长度范围为1019.117-5000.000 nm、577.474-5000.000 nm和525.697-5000.000 nm，说明附件中存在大量边界截断轴段。组1、组2和组3触及任一边界面的介质比例分别为58.3%、44.9%和71.0%。因此不能把所有截断轴段无条件延长，也不能因端点落在边界上而跨行合并介质身份。数据特征见图3。")
    p.figure("03_data_audit.png", "附件三组数据规模与边界截断特征", 15.3)
    p.heading("3.2  行级连通图", 2)
    p.paragraph("建立无向图G=(V,E)。V由两个虚拟电极节点LEFT、RIGHT和每一行对应的圆柱节点组成。若圆柱与电极的最短距离不超过g，则连接圆柱节点与相应电极；若两个圆柱的表面最短距离不超过g，则连接对应节点。LEFT与RIGHT位于同一连通分量当且仅当该构型导通。")
    p.equation("(i,j) in E  iff  dist(A_i,A_j)<=g;   (LEFT,i) in E  iff  dist(A_i,F_L)<=g")
    p.heading("3.3  平端圆柱的候选边与充分证书", 2)
    p.paragraph("两条轴段的最短距离不超过2r_A+g=61.8 nm时，相应胶囊体必接触，因此该条件可用于生成候选边。但胶囊体把圆柱端部替换为半球，可能把端点附近接近误判为平端圆柱接触。为避免这一问题，对正例路径中的每条圆柱—圆柱边保存轴段最短点参数s,t。当0<s<1且0<t<1时，两个最短点均位于轴段内部，表面间隙等于max(0,d_axis-2r_A)，可作为真实侧面接触的充分证书。对负例，胶囊体是平端圆柱的超集；若胶囊超图仍不连通，则真实图一定不连通。图4解释了证书条件。")
    p.figure("06_flat_cylinder_certificate.png", "平端圆柱侧面接触的轴段最短点证书", 14.7)
    p.heading("3.4  三组构型的求解结果", 2)
    p.paragraph("对每组数据先计算电极接触，再全对全生成候选边，以广相位空间索引复核边数，最后用广度优先搜索恢复一条LEFT-RIGHT路径。图5和图6从x-y、x-z两个投影展示全部轴段及显式路径；投影只用于解释，最终连边仍在三维空间中计算。")
    p.figure("04_q1_xy_projection.png", "三组构型的x-y投影与显式导通路径", 15.3)
    p.figure("05_q1_xz_projection.png", "三组构型的x-z投影与显式导通路径", 15.3)
    p.table("Q1三组附件构型的连通结果", ["组别", "节点数", "边数", "左接触", "右接触", "结论", "显式路径"], q1_result_rows(), [1.1, 1.4, 1.3, 1.3, 1.3, 1.5, 8.1], aligns=[WD_ALIGN_PARAGRAPH.CENTER]*6+[WD_ALIGN_PARAGRAPH.LEFT], font_size=8.6)
    p.paragraph("组1在更易连通的胶囊超图中仅有2条介质间边，LEFT与RIGHT仍分属不同连通分量，因此真实平端圆柱构型必不导通。组2和组3均找到显式路径；表4列出的6条介质间边均满足s,t位于(0,1)，故正例不依赖胶囊端部近似。")
    p.table("Q1正例路径的侧面接触证书", ["组别", "边", "轴距/nm", "s", "t", "证书"], q1_cert_rows(), [1.5, 2.5, 3.0, 2.2, 2.2, 2.7], font_size=9.2)

    p.heading("4  Q2-Q4共享的随机填充概率模型")
    p.heading("4.1  单粒子直接贯通事件", 2)
    p.paragraph("若某粒子在x方向跨越任一周期边界，其越界片段从对侧进入且保持同一导体身份，于是该粒子自身形成左右贯通。该事件是总导通事件T的充分条件而非必要条件，因此由它得到的是严格概率下界。图7分别示意圆柱A和球B的直接贯通机制。")
    p.figure("07_direct_bridge_mechanism.png", "A、B单粒子跨越周期边界的直接贯通机制", 15.3)
    p.heading("4.2  圆柱A的直接贯通概率", 2)
    p.paragraph("设圆柱轴向单位向量的x分量为u_x。平端圆柱在x方向的支撑半宽由轴向投影和端面圆盘投影共同组成。固定方向后，圆柱中心落入任一边界内侧a_x范围即越界，两侧合计条件概率为2a_x/L。")
    p.equation("a_x=(H/2)*abs(u_x)+r_A*sqrt(1-u_x^2)")
    p.paragraph("各向同性方向满足E|u_x|=1/2以及E sqrt(1-u_x^2)=pi/4，故对方向积分可得q_A。图8给出条件越界概率随|u_x|的变化及其方向平均。")
    p.equation("q_A=2*E(a_x)/L=(H/2+pi*r_A/2)/L=0.25471238898")
    p.figure("08_orientation_support_curve.png", "圆柱取向对支撑半宽和条件越界概率的影响", 15.3)
    p.heading("4.3  球B与多粒子的直接贯通下界", 2)
    p.paragraph("球的支撑半宽恒为r_B，故球心落入任一边界内侧r_B范围即可越界。不同粒子的位置和方向独立时，至少一个粒子直接贯通的概率可由补事件乘积得到。")
    p.equation("q_B=2*r_B/L=0.04")
    p.equation("P_dir=P(D)=1-(1-q_A)^n_A*(1-q_B)^n_B")
    p.heading("4.4  非直接通路的剩余薄壳联合上界", 2)
    p.paragraph("为证明某个较低填充方案不可能达到90%，仅有下界不够。定义D_i为粒子i直接越界，C_i^L为粒子i接触左电极。固定其x向支撑半宽a_i时，无条件接触层宽为a_i+g，因此不能把P(C_i^L)误写成g/L。关键在于研究无直接贯通事件D^c中的剩余接触：粒子既不越界又接触左电极时，中心只能位于宽度恰为g的薄壳。")
    p.equation("S_i^L=C_i^L intersect D_i^c={-L/2+a_i<X_i<=-L/2+a_i+g},  P(S_i^L)=g/L")
    p.paragraph("令N=T交D^c。任何N中的左右路径都必须包含不同的终端粒子i和j，分别落入左、右剩余薄壳；若由同一粒子承担两端接触，则该粒子已经属于直接贯通事件D。对所有有序粒子对使用独立性和Boole联合界[3]，得到式(9)。事件关系见图9。")
    p.equation("P_dir<=P(T)<=min{1, P_dir+n*(n-1)*(g/L)^2},  n=n_A+n_B")
    p.figure("09_event_bounds.png", "总导通、直接贯通与剩余薄壳事件的上下界关系", 15.3)
    p.heading("4.5  概率模型的解释边界", 2)
    p.paragraph("式(9)的上界用于证明“不足”，不用于精确估计真实导通概率；它忽略了中间粒子如何连接，因此通常偏松，但不会漏掉曲折通路。式(8)的下界用于证明“充分”，也不等于总导通概率。只有当上下界位于阈值两侧时，才能给出严格整数阈值或最优性结论。若粒子中心存在排斥、团聚或取向相关，式(8)中的独立乘积和式(9)中的跨粒子独立性需要重建。")

    p.heading("5  问题二：给定体积分数下的导通概率")
    p.heading("5.1  体积分数到整数数量的换算", 2)
    p.paragraph("设目标体积分数为phi。粒子数必须取整数，本文选择使n_A V_A/L^3最接近目标phi的整数n_A，并同时报告目标值与实际值。四个目标体积分数对应354、424、495和707根A。")
    p.equation("n_A=round(phi*L^3/V_A),  phi_actual=n_A*V_A/L^3")
    p.heading("5.2  概率结果与解释", 2)
    q2_rows = [[f"{100*r['requested_fraction']:.2f}%", r["a_count"], f"{100*r['achieved_fraction']:.5f}%", f"{r['log10_failure_probability_upper_bound']:.2f}", f"至少1-10^{r['log10_failure_probability_upper_bound']:.2f}"] for r in RESULTS["Q2"]]
    p.table("Q2体积分数、整数数量与直接贯通下界", ["目标体积分数", "A数量", "实际体积分数", "log10不导通上界", "导通概率下界"], q2_rows, [2.5, 1.7, 2.7, 4.0, 5.0], font_size=9)
    p.paragraph("表5中的“不导通上界”仅考虑没有任何A直接贯通的概率(1-q_A)^n_A。粒子间进一步接触只会增加总导通概率，因此该量确为总不导通概率的上界。四个数量级远低于常规数值显示精度，故可以表述为“在报告精度内导通概率为1”，但不能写成数学上精确等于1。图10展示其对数数量级。")
    p.figure("10_q2_failure_scale_cn.png", "Q2四种体积分数下不导通概率上界的数量级", 15.3)

    p.heading("6  问题三：仅填充A的最低填充量")
    p.heading("6.1  候选阈值定位", 2)
    p.paragraph("由式(8)可知直接贯通下界随n_A单调增加。解1-(1-q_A)^n_A>=0.90可将候选值定位在8根。证明“8根是最小值”还需验证8根充分和7根不足。")
    p.equation("n_A>=ceil(log(0.10)/log(1-q_A))=8")
    p.heading("6.2  7根不足与8根充分", 2)
    p.paragraph("当n_A=8时，直接贯通概率下界为0.9048100243>0.90，故8根充分。当n_A=7时，直接贯通概率为0.8722775285；剩余非直接通路上界增量为7*6*(1.8/10000)^2=1.3608e-6，因而总导通概率上界为0.8722788893<0.90，故7根不足。图11显示上下界几乎重合但分别位于阈值两侧。")
    q3_rows = [[r["a_count"], f"{r['direct_bridge_lower_bound']:.6f}", f"{r['non_direct_path_upper_addition']:.2e}", f"{r['conduction_upper_bound']:.6f}"] for r in RESULTS["Q3"]["proof_rows"]]
    p.table("Q3从1至8根A的导通概率上下界", ["A数量", "直接贯通下界", "非直接上界增量", "总导通上界"], q3_rows, [2.3, 4.4, 4.7, 4.4], font_size=9.2)
    p.figure("11_q3_threshold_cn.png", "Q3中7根不足、8根充分的严格夹逼", 15.3)
    p.heading("6.3  填充率报告", 2)
    p.paragraph("8根A对应体积分数8V_A/L^3=0.0001130973，即0.01131%。若按百分号后保留两位，应报告0.01%；但必须同时保留“8根”和未过度舍入的0.01131%，因为相邻整数在两位百分数下可能显示相同。")

    p.heading("7  问题四：混合填充的整数成本优化")
    p.heading("7.1  优化模型", 2)
    p.paragraph("以n_A,n_B为整数决策变量，目标是最小化式(2)的材料成本，约束为总导通概率不低于0.90。由于总导通概率难以精确闭式计算，本文采用“候选方案用下界证明可行、所有更便宜方案用上界证明不可行”的双向证书。")
    p.equation("min C(n_A,n_B),  s.t. P(T)>=0.90,  n_A,n_B in nonnegative integers")
    p.heading("7.2  非负整数域的边界解", 2)
    p.paragraph("若允许某一类介质数量为零，0A+57B的直接贯通下界为0.9023976480，成本0.0955044元，故该方案可行。以该成本为上限，枚举全部216个更低成本非负整数点；其中总导通上界最大的是0A+56B，上界0.8984306753<0.90。因此所有更便宜方案均不可行，0A+57B在非负整数域严格最优。")
    p.heading("7.3  两类介质均为正的主口径", 2)
    p.paragraph("题目中的“同时填充A、B”可能要求两类介质均出现。增加n_A>=1,n_B>=1后，1A+50B的直接贯通下界为0.9031977272，成本0.0986198元。枚举164个更低成本正混合点后，最危险方案1A+49B的总导通上界为0.8992436792<0.90。因此若按“同时填充”解释，应把1A+50B作为正式答案，0A+57B仅作为放宽约束后的对照。")
    q4 = RESULTS["Q4"]
    q4_rows = [[f"{x['a_count']}A+{x['b_count']}B", f"{x['cost_cny']:.6f}", f"{x['direct_bridge_probability']:.6f}", f"{x['conduction_upper_bound']:.6f}", "更便宜，不可行"] for x in q4["cheaper_frontier"]]
    q4_rows += [["0A+57B", f"{q4['selected']['cost_cny']:.6f}", f"{q4['selected']['direct_bridge_lower_bound']:.6f}", "-", "非负整数域最优"], ["1A+50B", f"{q4['strictly_positive_mixture']['selected']['cost_cny']:.6f}", f"{q4['strictly_positive_mixture']['selected']['direct_bridge_lower_bound']:.6f}", "-", "正混合域最优"]]
    p.table("Q4低成本前沿与两种口径的候选解", ["方案", "成本/元", "直接下界", "总上界", "结论"], q4_rows, [2.5, 2.5, 3.0, 3.0, 5.2], font_size=8.8)
    p.figure("12_q4_integer_domain.png", "Q4低成本整数域排除与两种口径的最优解", 15.3)
    p.heading("7.4  成本效率解释", 2)
    p.paragraph("A单体直接贯通概率高，但单体成本约为B的8.86倍；B虽需要更多数量，却具有更高的单位成本概率收益，因此非负整数域最优点落在纯B边界。强制两类均出现时，加入1根A可以减少7个B，形成1A+50B的正混合最优点。该解释只针对本题给定价格和尺寸，若B单价上升或半径改变，整数前沿会发生跳变。")

    p.heading("8  模型检验、灵敏度与稳健性")
    p.heading("8.1  几何算法检验", 2)
    p.paragraph("几何测试覆盖平行、相交、端点最近、轴段换序和多对批量计算等情形；对附件三组数据，全对全枚举与KD树广相位得到相同的连通结论和边数。正例路径逐边检查s,t与轴距，负例则利用胶囊超集反证。当前测试共16项通过，其中新增测试明确区分无条件电极接触层a_i+g与非越界剩余薄壳g，防止把g/L误写成无条件接触概率。")
    p.heading("8.2  概率与整数域复核", 2)
    p.paragraph("q_A由方向积分解析得到，q_B由球的边界层宽度直接得到；Q3分别重算7根上界与8根下界。Q4不是只比较表7中的前沿点，而是完整枚举成本严格低于候选的所有整数点，再取其总导通上界最大者。因此216和164是搜索域内实际候选数，不是抽样规模。")
    p.heading("8.3  几何参数灵敏度", 2)
    p.paragraph("保持其他参数不变，A高度H增大时q_A线性增大，达到90%所需A数量呈阶梯下降；B半径增大时q_B=2r_B/L增大，达到90%所需B数量下降。图13给出H在3500-6500 nm、r_B在120-280 nm范围内的阈值变化。基准H=5000 nm对应8根A，r_B=200 nm对应57个B。")
    p.figure("13_parameter_sensitivity.png", "A高度与B半径变化对90%阈值数量的影响", 15.3)
    p.heading("8.4  假设敏感性与失效情形", 2)
    p.table("关键假设变化对结论的影响", ["变化", "直接影响", "最可能受影响的结论", "建议改进"], [
        ["A取向偏向x轴", "q_A增大", "Q3阈值下降，Q4更偏向A", "用实测取向分布替代各向同性积分"],
        ["粒子不可重叠", "位置不再独立", "Q2-Q4乘积式和联合界需重建", "随机序列吸附或排斥点过程模拟"],
        ["粒子团聚", "局部连接增强但边界分布改变", "总概率与解析界间隙增大", "相关随机几何图与蒙特卡洛校准"],
        ["周期片段不保持导体身份", "直接贯通事件失效", "Q2-Q4全部数值失效", "按新边界物理重新定义连接图"],
        ["要求A、B均出现", "可行域删去坐标轴", "Q4主答案变为1A+50B", "论文同时报告两种口径"],
    ], [3.0, 4.0, 4.6, 4.6], aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=8.8)

    p.heading("9  模型评价与改进")
    p.heading("9.1  模型优点", 2)
    p.paragraph("第一，Q1采用路径证书而非只给程序布尔值，负例和正例分别由超集反证与侧面充分证书支撑。第二，Q2-Q4明确区分精确直接贯通概率、总导通下界和总导通上界，避免把蒙特卡洛频率或下界误当作真实概率。第三，Q4对候选成本以下的有限整数域完整枚举，最优性证据可逐点复算。第四，所有关键数值集中写入结构化结果文件并由测试检查，论文图表直接从附件和结果文件生成。")
    p.heading("9.2  模型局限", 2)
    p.paragraph("随机模型的主要局限是独立均匀、各向同性和允许重叠三项补充假设不一定符合真实材料制备。非直接通路联合上界只适合做不足性证明，不能精确刻画粒子间簇连通。Q1的正例证书只需证明所给路径有效，不代表候选图中的所有端部边都已完成严格平端圆柱距离分类。")
    p.heading("9.3  后续改进", 2)
    p.paragraph("后续可在三方面扩展：其一，实现平端圆柱—圆柱、圆柱—球的完整最近距离求解器，替代胶囊候选超图；其二，引入不可重叠随机序列吸附、取向偏置或团聚点过程，并用方差缩减蒙特卡洛估计真实导通概率；其三，在解析界与模拟之间建立校准区间，使模型既能证明阈值，又能给出阈值以外更精细的工程概率估计。")

    p.heading("10  结论")
    p.paragraph("(1) 附件组1不导通，组2和组3导通；组2显式路径为左面-2-12-24-39-右面，组3为左面-63-264-216-351-右面。所有正例介质间边均具有轴段内部最短点证书。", first=False)
    p.paragraph("(2) A体积分数0.50%、0.60%、0.70%和1.00%对应354、424、495和707根A；总不导通概率分别不超过10^-45.20、10^-54.13、10^-63.20和10^-90.27量级。", first=False)
    p.paragraph("(3) 仅填充A时，7根的总导通上界0.872279低于90%，8根的直接贯通下界0.904810高于90%，故最小数量为8根；体积分数为0.01131%，按百分号后两位报告为0.01%。", first=False)
    p.paragraph("(4) 混合填充时，非负整数域最优为0A+57B，成本0.09550元；若A、B必须均出现，则正混合域最优为1A+50B，成本0.09862元。后者应作为“同时填充”口径下的主答案。", first=False)

    p.heading("参考文献")
    refs = [
        "[1] 华数杯大学生数学建模竞赛组委会，2026年第七届华数杯大学生数学建模竞赛A题：微构体中填充导电介质的仿真优化，2026。",
        "[2] 华数杯大学生数学建模竞赛组委会，2026年华数杯数学建模竞赛论文格式规范与提交说明，https://m.saikr.com/chinamcm26，访问日期：2026-08-13。",
        "[3] Feller W. An Introduction to Probability Theory and Its Applications, Vol. 1. New York: Wiley, 1968.",
        "[4] Ericson C. Real-Time Collision Detection. Boca Raton: CRC Press, 2005.",
        "[5] Meester R, Roy R. Continuum Percolation. Cambridge: Cambridge University Press, 1996.",
    ]
    for ref in refs:
        p.paragraph(ref, first=False, size=10.5, after=2)

    p.page_break()
    p.heading("附录A  复现环境与命令")
    p.paragraph("软件环境：Python 3.13；numpy 2.2.6；pandas 3.0.3；openpyxl 3.1.5；scipy 1.16.3；pytest 9.1.0。图表和文档生成使用工作区绑定运行时。", first=False)
    commands = """cd mathmodel/runs/huashubei-2026-final-001
python -m pip install -r requirements.txt
python src/a/build_corrected_results.py
python src/a/build_final_artifacts.py
python -m pytest tests -q"""
    p.code_block(commands)
    p.paragraph("当前仓库完整测试共46项通过，项目证据登记表与论文正文哈希可由随附脚本重建和复核。", first=False)

    p.heading("附录B  关键源程序")
    for filename in ("analytic_bounds.py", "geometry.py", "build_corrected_results.py"):
        p.heading(f"B.{('analytic_bounds.py','geometry.py','build_corrected_results.py').index(filename)+1}  src/a/{filename}", 2)
        code = (RUN / "src" / "a" / filename).read_text(encoding="utf-8")
        p.code_block(code)

    docx = OUT / "华数杯A题完整论文_清洁版.docx"
    md = OUT / "paper_full.md"
    p.save(docx, md)
    return docx, md


def main():
    docx, md = build_paper()
    print(docx)
    print(md)


if __name__ == "__main__":
    main()
