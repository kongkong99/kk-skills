#!/usr/bin/env python3
"""
build_order_xlsx.py —— 工单驱动 PPT 生产：工单工作簿的生成与校验

子命令
  build     由工单 JSON 生成三 sheet 工单 xlsx（页面工单 / 模板目录 / 全局设置）。
            有错误（超容量、不适用字段有内容、必填为空……）时不出文件。
  check     回读工单 xlsx（含用户改过的版本）：复核全部约束、列出剩余待补项；
            --out 导出逐页 JSON 供出片使用；--pptx 比对成品页数、页序、空白页。
  demo      写出一份最小示例 JSON，并据此生成示例工单。
  selftest  自测（正例、反例、回读往返、成品比对），全部通过时退出码为 0。

用法
  python build_order_xlsx.py build order.json -o 工单.xlsx
  python build_order_xlsx.py check 工单.xlsx [--strict] [--out pages.json] [--pptx 成品.pptx]
  python build_order_xlsx.py demo --outdir ./demo
  python build_order_xlsx.py selftest

退出码
  0 通过；1 有错误；2 仅 check --strict：没有错误但仍有待补项。

依赖
  openpyxl（必需）；python-pptx（仅 --pptx 比对时需要）。

输入 JSON 结构、单元格取值语义、校验规则见 references/order-schema.md。
"""

import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:  # pragma: no cover
    sys.stderr.write("缺少 openpyxl，请先安装：pip install openpyxl\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 常量：列定义、占位语义
# ---------------------------------------------------------------------------

SHEET_PAGES = "页面工单"
SHEET_TPLS = "模板目录"
SHEET_GLOBAL = "全局设置"

FIELDS = ["主标题", "副标题", "正文块1", "正文块2", "正文块3",
          "配图描述", "配图URL文件", "演讲者备注"]
BODY = ["正文块1", "正文块2", "正文块3"]
TEMPLATE_FIELDS = [f for f in FIELDS if f != "演讲者备注"]  # 演讲者备注对所有版式都是可选
PAGE_COLUMNS = ["页码", "页型", "推荐模板", "主标题", "副标题", "正文块1", "正文块2",
                "正文块3", "配图描述", "配图URL文件", "演讲者备注", "待补项", "制作备注"]
TPL_COLUMNS = ["模板（下拉值）", "模板ID", "中文名", "页型", "长什么样", "适合什么时候用",
               "必填字段", "可选字段", "正文槽位数", "并列点数上限", "主标题字数上限",
               "副标题字数上限", "正文块字数上限", "内容形态", "配图需求", "节奏定位",
               "来源", "本套使用次数", "占比"]
GLOBAL_COLUMNS = ["设置项", "值", "用在哪里 / 填写说明"]
LIMIT_KEYS = {"主标题": "主标题字数上限", "副标题": "副标题字数上限", "正文块": "正文块字数上限"}

NA = "/"
TODO_PREFIX = "【待补】"
DRAFT_SEP = "｜暂定："
PENDING_FILL = "FDE7E9"
ACCENT_RHYTHM = "节奏点"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
DISPLAY_RE = re.compile(r"^(.*?)[（(]\s*([A-Za-z0-9][A-Za-z0-9_-]*)\s*[）)]\s*$")

GLOBAL_KEYS = [
    ("讲师姓名", "封面署名、讲师介绍页"),
    ("讲师头衔", "讲师介绍页副标题"),
    ("活动名称", "封面署名行、结束页"),
    ("活动日期", "封面署名行"),
    ("品牌主色", "标题与强调色，填 HEX，如 #1F6FEB"),
    ("品牌辅色", "卡片底色、分隔线，填 HEX"),
    ("字体", "中文标题/正文字体，如 思源黑体"),
    ("Logo文件", "封面与结束页角标，填文件名或链接"),
]

LEGEND = [
    "填写说明",
    "浅红底 + 「【待补】」开头 = 开工前必须补齐：直接用真实内容覆盖整格，红底会自动消失。",
    "「/」= 该字段对这一页不适用，不用填，也不要删掉。",
    "推荐模板请从下拉框选，格式是「中文名（ID）」；每种版式长什么样、能放多少字，见「模板目录」。",
    "正文块里一行 = 一个并列点；字数按去掉空格后的字符数算，上限见「模板目录」。",
    "改完把整个文件交回。出片以这份工单为唯一依据，不会再凭记忆改写措辞。",
]

# ---------------------------------------------------------------------------
# 默认 9 种版式（与 references/template-constraints.md 保持一致）
# ---------------------------------------------------------------------------

DEFAULT_TEMPLATES = [
    {"id": "cover", "name": "封面", "page_type": "封面",
     "looks_like": "满版品牌色或背景图，居中大标题，下方一行副标题，底部一行署名（讲师｜活动｜日期）",
     "use_when": "整套第 1 页，且只用一次",
     "required": ["主标题", "正文块1"], "optional": ["副标题", "配图描述", "配图URL文件"],
     "max_points": 1, "limits": {"主标题": 18, "副标题": 28, "正文块": 30},
     "content_form": "标题 + 署名行", "rhythm": "开场", "source": "内置骨架"},
    {"id": "speaker", "name": "讲师介绍", "page_type": "讲师介绍",
     "looks_like": "左侧讲师照片，右侧姓名、头衔和 3 行以内履历要点",
     "use_when": "开场第 2 页；对外分享、需要建立信任时",
     "required": ["主标题", "副标题", "正文块1", "配图描述", "配图URL文件"], "optional": [],
     "max_points": 3, "limits": {"主标题": 10, "副标题": 24, "正文块": 72},
     "content_form": "人物 + 头衔 + 履历要点", "rhythm": "开场", "source": "内置骨架"},
    {"id": "section", "name": "章节过渡", "page_type": "章节过渡",
     "looks_like": "大号章节名居中，可带一句本章要点，大面积留白或品牌色底",
     "use_when": "进入新章节前；整套 3 章以上才需要",
     "required": ["主标题"], "optional": ["副标题"],
     "max_points": 0, "limits": {"主标题": 12, "副标题": 24},
     "content_form": "章节名 + 一句话", "rhythm": "转场", "source": "内置骨架"},
    {"id": "two-col", "name": "双栏文字", "page_type": "双栏文字",
     "looks_like": "顶部标题，下方左右两栏，每栏最多 3 行（首行可作小标题）",
     "use_when": "对比（之前/之后、A/B）或两件并列的事",
     "required": ["主标题", "正文块1", "正文块2"], "optional": ["副标题"],
     "max_points": 6, "limits": {"主标题": 20, "副标题": 28, "正文块": 60},
     "content_form": "两组并列要点", "rhythm": "主体", "source": "内置骨架"},
    {"id": "three-card", "name": "三卡片", "page_type": "三卡片",
     "looks_like": "顶部标题，下方三张等宽卡片；每张卡片一行，写成「卡片标题：一句说明」",
     "use_when": "恰好 3 个并列点；多于 3 个必须拆页或换版式",
     "required": ["主标题", "正文块1", "正文块2", "正文块3"], "optional": ["副标题"],
     "max_points": 3, "limits": {"主标题": 20, "副标题": 28, "正文块": 36},
     "content_form": "三个并列点", "rhythm": ACCENT_RHYTHM, "source": "内置骨架"},
    {"id": "viewpoint", "name": "观点页", "page_type": "观点页",
     "looks_like": "上方一句大字观点，下方 3 行以内论据，右侧可放一张小配图",
     "use_when": "抛出一个判断并给理由；主体内容的主力版式",
     "required": ["主标题", "正文块1"], "optional": ["副标题", "配图描述", "配图URL文件"],
     "max_points": 3, "limits": {"主标题": 24, "副标题": 30, "正文块": 80},
     "content_form": "观点 + 论据", "rhythm": "主体", "source": "内置骨架"},
    {"id": "quote", "name": "金句页", "page_type": "金句页",
     "looks_like": "整页只有一句大字金句，可带一行出处或补充",
     "use_when": "章节收束或全场落点；全套少量使用",
     "required": ["主标题"], "optional": ["副标题"],
     "max_points": 0, "limits": {"主标题": 30, "副标题": 20},
     "content_form": "一句话", "rhythm": ACCENT_RHYTHM, "source": "内置骨架"},
    {"id": "img-text", "name": "图文页", "page_type": "图文页",
     "looks_like": "左侧大图（截图/照片/示意图），右侧标题 + 4 行以内说明",
     "use_when": "演示、案例、截图讲解",
     "required": ["主标题", "正文块1", "配图描述", "配图URL文件"], "optional": ["副标题"],
     "max_points": 4, "limits": {"主标题": 20, "副标题": 28, "正文块": 90},
     "content_form": "图 + 说明", "rhythm": "主体", "source": "内置骨架"},
    {"id": "ending", "name": "结束页", "page_type": "结束页",
     "looks_like": "一句行动号召 + 二维码或联系方式，信息只留一个出口",
     "use_when": "整套最后一页，且只用一次",
     "required": ["主标题"], "optional": ["副标题", "正文块1", "配图描述", "配图URL文件"],
     "max_points": 2, "limits": {"主标题": 16, "副标题": 24, "正文块": 40},
     "content_form": "行动号召 + 出口", "rhythm": "收尾", "source": "内置骨架"},
]

# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Pending:
    """待补：开工前必须补齐的内容/素材。desc 写缺什么，draft 为可选的暂定文字。"""
    desc: str
    draft: str = ""

    def cell(self) -> str:
        return TODO_PREFIX + self.desc + (DRAFT_SEP + self.draft if self.draft else "")

    def to_json(self):
        d = {"todo": self.desc}
        if self.draft:
            d["draft"] = self.draft
        return d


@dataclass
class Template:
    id: str
    name: str
    page_type: str
    looks_like: str = ""
    use_when: str = ""
    required: list = field(default_factory=list)
    optional: list = field(default_factory=list)
    max_points: int = 0
    limits: dict = field(default_factory=dict)
    content_form: str = ""
    rhythm: str = ""
    source: str = ""
    declared_slots: object = None

    @property
    def display(self) -> str:
        return f"{self.name}（{self.id}）"

    @property
    def slots(self) -> int:
        return sum(1 for b in BODY if b in self.required or b in self.optional)

    @property
    def image_need(self) -> str:
        if "配图URL文件" in self.required:
            return "必需"
        if "配图URL文件" in self.optional:
            return "可选"
        return "无"

    @property
    def accent(self) -> bool:
        return self.rhythm == ACCENT_RHYTHM

    def status(self, f: str) -> str:
        if f == "演讲者备注" or f in self.optional:
            return "optional"
        if f in self.required:
            return "required"
        return "na"

    def limit_for(self, f: str):
        key = "正文块" if f in BODY else f
        return self.limits.get(key)


@dataclass
class Page:
    page: object
    page_type: str
    template_id: str
    template_display: str
    fields: dict
    note: str = NA  # 制作备注


class Report:
    def __init__(self):
        self.errors, self.warnings, self.pendings, self.infos = [], [], [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def print(self, stream=sys.stdout):
        for tag, items in (("错误", self.errors), ("提醒", self.warnings),
                           ("待补", [f"第 {p} 页 {f}：{d}" if p else f"{f}：{d}"
                                     for p, f, d in self.pendings]),
                           ("信息", self.infos)):
            for m in items:
                print(f"[{tag}] {m}", file=stream)
        print(f"—— 错误 {len(self.errors)} · 提醒 {len(self.warnings)} · "
              f"待补 {len(self.pendings)}", file=stream)


# ---------------------------------------------------------------------------
# 取值规整
# ---------------------------------------------------------------------------


def parse_pending_text(s: str) -> Pending:
    body = s[len(TODO_PREFIX):]
    if DRAFT_SEP in body:
        desc, draft = body.split(DRAFT_SEP, 1)
        return Pending(desc.strip() or "未说明缺什么", draft.strip())
    return Pending(body.strip() or "未说明缺什么")


def norm_value(v):
    """JSON 或单元格里的原始值 → None（空）/ NA / Pending / str。"""
    if v is None:
        return None
    if isinstance(v, dict):
        if "todo" not in v:
            raise ValueError(f"对象取值只支持 {{\"todo\": ..., \"draft\": ...}}，收到 {v}")
        return Pending(str(v["todo"]).strip() or "未说明缺什么", str(v.get("draft") or "").strip())
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        v = str(int(v)) if float(v).is_integer() else str(v)
    if not isinstance(v, str):
        raise ValueError(f"不支持的取值类型：{type(v).__name__}")
    s = v.replace("\r\n", "\n").strip()
    if s == "":
        return None
    if s == NA:
        return NA
    if s.startswith(TODO_PREFIX):
        return parse_pending_text(s)
    return s


def cell_text(v) -> str:
    if isinstance(v, Pending):
        return v.cell()
    return "" if v is None else str(v)


def text_of(v) -> str:
    """参与字数/条数校验的文字：内容本身，或待补的暂定文字。"""
    if isinstance(v, Pending):
        return v.draft
    if isinstance(v, str) and v != NA:
        return v
    return ""


def char_count(s: str) -> int:
    return len(re.sub(r"\s", "", s))


def line_count(v) -> int:
    if isinstance(v, Pending) and not v.draft:
        return 1
    return sum(1 for ln in text_of(v).split("\n") if ln.strip())


# ---------------------------------------------------------------------------
# 版式定义：加载与校验
# ---------------------------------------------------------------------------


def template_from_dict(d: dict) -> Template:
    limits = {}
    for k, v in (d.get("limits") or {}).items():
        if v is None or v == NA:
            continue
        limits[k] = int(v)
    return Template(
        id=str(d.get("id", "")).strip(), name=str(d.get("name", "")).strip(),
        page_type=str(d.get("page_type", "")).strip(),
        looks_like=d.get("looks_like", ""), use_when=d.get("use_when", ""),
        required=list(d.get("required") or []), optional=list(d.get("optional") or []),
        max_points=int(d.get("max_points", 0) or 0), limits=limits,
        content_form=d.get("content_form", ""), rhythm=d.get("rhythm", ""),
        source=d.get("source", ""), declared_slots=d.get("slots"))


def validate_templates(tpls, rep: Report):
    seen_id, seen_disp = set(), set()
    for t in tpls:
        where = f"版式 {t.display}"
        if not t.id or not ID_RE.match(t.id):
            rep.err(f"{where}：模板 ID 只能用英文、数字、- 和 _，且不能为空")
        if not t.name:
            rep.err(f"{where}：缺中文名（禁止只用英文 ID）")
        if not t.page_type:
            rep.err(f"{where}：缺页型")
        if t.id in seen_id:
            rep.err(f"{where}：模板 ID 重复")
        if t.display in seen_disp:
            rep.err(f"{where}：下拉显示值重复")
        seen_id.add(t.id)
        seen_disp.add(t.display)
        for f in t.required + t.optional:
            if f not in TEMPLATE_FIELDS:
                rep.err(f"{where}：未知字段「{f}」，可用字段：{'、'.join(TEMPLATE_FIELDS)}")
        both = set(t.required) & set(t.optional)
        if both:
            rep.err(f"{where}：字段同时出现在必填和可选：{'、'.join(both)}")
        used_body = [b for b in BODY if b in t.required or b in t.optional]
        if used_body != BODY[:len(used_body)]:
            rep.err(f"{where}：正文块必须从正文块1 起连续使用")
        if t.declared_slots not in (None, "", NA) and int(t.declared_slots) != t.slots:
            rep.err(f"{where}：声明槽位数 {t.declared_slots} 与实际使用的正文块数 {t.slots} 不一致")
        for k in t.limits:
            if k not in LIMIT_KEYS:
                rep.err(f"{where}：字数上限只能设在 主标题 / 副标题 / 正文块，收到「{k}」")
        for f in ("主标题", "副标题"):
            if t.status(f) != "na" and f not in t.limits:
                rep.err(f"{where}：用到了{f}，必须给出字数上限")
        if t.slots and "正文块" not in t.limits:
            rep.err(f"{where}：有正文槽位，必须给出正文块字数上限")
        if t.slots and t.max_points < t.slots:
            rep.err(f"{where}：并列点数上限 {t.max_points} 小于槽位数 {t.slots}")
        if not t.slots and t.max_points:
            rep.err(f"{where}：没有正文槽位，并列点数上限应为 0")
        if ("配图描述" in t.required) != ("配图URL文件" in t.required):
            rep.err(f"{where}：配图描述与配图URL文件的必填性应一致")


# ---------------------------------------------------------------------------
# 页面：规整与校验（build 与 check 共用）
# ---------------------------------------------------------------------------


def pages_from_json(raw_pages, tmap, rep: Report):
    pages = []
    for i, rp in enumerate(raw_pages, 1):
        pno = rp.get("页码", i)
        where = f"第 {pno} 页"
        tid = rp.get("模板ID")
        if not tid and rp.get("推荐模板"):
            m = DISPLAY_RE.match(str(rp["推荐模板"]))
            tid = m.group(2) if m else None
        t = tmap.get(tid)
        if not t:
            rep.err(f"{where}：模板「{tid}」不在模板目录里；新版式要先在约束表登记再使用")
            continue
        vals = {}
        for f in FIELDS:
            try:
                v = norm_value(rp.get(f))
            except ValueError as e:
                rep.err(f"{where} {f}：{e}")
                v = NA
            st = t.status(f)
            if v is None:
                if st == "required":
                    rep.err(f"{where} {f}：必填却为空。写内容，或写成 {{\"todo\": \"缺什么\"}} 标待补")
                v = NA
            vals[f] = v
        extra = set(rp) - set(FIELDS) - {"页码", "页型", "模板ID", "推荐模板", "制作备注", "待补项"}
        if extra:
            rep.warn(f"{where}：忽略未知键 {'、'.join(sorted(extra))}")
        note = norm_value(rp.get("制作备注"))
        pages.append(Page(page=pno, page_type=str(rp.get("页型") or t.page_type),
                          template_id=t.id, template_display=t.display, fields=vals,
                          note=note if isinstance(note, str) else NA))
    return pages


def validate_pages(pages, tmap, rep: Report):
    # 页码连续
    nums = [p.page for p in pages]
    expect = list(range(1, len(pages) + 1))
    if nums != expect:
        rep.err(f"页码必须从 1 开始连续递增，当前为 {nums}")

    for p in pages:
        where = f"第 {p.page} 页"
        t = tmap.get(p.template_id)
        if not t:
            rep.err(f"{where}：模板「{p.template_id}」不在模板目录里")
            continue
        if p.template_display != t.display:
            rep.warn(f"{where}：推荐模板写的是「{p.template_display}」，目录里该 ID 是「{t.display}」")
        if p.page_type != t.page_type:
            rep.err(f"{where}：页型「{p.page_type}」与模板「{t.display}」的页型「{t.page_type}」不符")
        points = 0
        for f in FIELDS:
            v = p.fields.get(f)
            st = t.status(f)
            if v is None:
                rep.err(f"{where} {f}：空单元格有歧义。不适用填「/」，缺素材标【待补】")
                continue
            if st == "na" and v != NA:
                rep.err(f"{where} {f}：「{t.display}」没有这个字段，应为「/」。"
                        f"内容放不下就拆页或换版式")
            if st == "required" and v == NA:
                rep.err(f"{where} {f}：「{t.display}」必填，不能是「/」；缺素材请标【待补】")
            if isinstance(v, Pending):
                rep.pendings.append((p.page, f, v.desc))
            lim = t.limit_for(f)
            txt = text_of(v)
            if lim and txt and char_count(txt) > lim:
                rep.err(f"{where} {f}：{char_count(txt)} 字，超过上限 {lim}。"
                        f"→ 拆页或换容量更大的版式，不要压缩硬塞")
            if f in BODY and v != NA:
                points += line_count(v)
        if t.slots and points > t.max_points:
            rep.err(f"{where}：正文共 {points} 个并列点，超过「{t.display}」上限 {t.max_points}。"
                    f"→ 拆页或换版式")
        img_d, img_f = p.fields.get("配图描述"), p.fields.get("配图URL文件")
        if img_d not in (None, NA) and img_f == NA:
            rep.err(f"{where}：写了配图描述却把配图URL文件标成「/」；没有素材请标【待补】，不要编造")
        if img_f not in (None, NA) and img_d == NA:
            rep.warn(f"{where}：有配图文件但没有配图描述，出片时无法核对图是否放对")

    rhythm_checks(pages, tmap, rep)


def rhythm_checks(pages, tmap, rep: Report):
    n = len(pages)
    if not n:
        rep.err("工单没有任何页面")
        return
    for a, b in zip(pages, pages[1:]):
        if a.template_id == b.template_id:
            rep.warn(f"第 {a.page}、{b.page} 页连续使用「{a.template_display}」，"
                     f"考虑换版式或在中间插入节奏页")
    counts = {}
    for p in pages:
        counts[p.template_id] = counts.get(p.template_id, 0) + 1
    cap = max(1, math.ceil(n * 0.15))
    for tid, c in counts.items():
        t = tmap.get(tid)
        if t and t.accent and c > cap:
            rep.warn(f"「{t.display}」是节奏点版式，用了 {c} 次，{n} 页建议不超过 {cap} 次")
    types = {t.page_type for t in tmap.values()}
    if "封面" in types and pages[0].page_type != "封面":
        rep.warn("第 1 页不是封面")
    if "结束页" in types and pages[-1].page_type != "结束页":
        rep.warn("最后一页不是结束页")
    for pt in ("封面", "结束页"):
        k = sum(1 for p in pages if p.page_type == pt)
        if k > 1:
            rep.warn(f"「{pt}」出现了 {k} 次，通常只用一次")
    rep.infos.append(f"共 {n} 页；已用版式 {len(counts)}/{len(tmap)} 种：" +
                     "、".join(f"{tmap[t].name}×{c}" for t, c in counts.items() if t in tmap))


def globals_from_json(raw: dict, rep: Report):
    out = []
    raw = dict(raw or {})
    for key, hint in GLOBAL_KEYS:
        try:
            v = norm_value(raw.pop(key, None))
        except ValueError as e:
            rep.err(f"全局设置 {key}：{e}")
            v = None
        if v is None:
            v = Pending(f"未提供{key}")
        out.append((key, v, hint))
    for key, v in raw.items():
        try:
            nv = norm_value(v)
        except ValueError as e:
            rep.err(f"全局设置 {key}：{e}")
            continue
        out.append((key, nv if nv is not None else Pending(f"未提供{key}"), "自定义项"))
    for key, v, _ in out:
        if isinstance(v, Pending):
            rep.pendings.append((None, f"全局设置·{key}", v.desc))
    return out


# ---------------------------------------------------------------------------
# 写工作簿
# ---------------------------------------------------------------------------

FONT = "微软雅黑"
THIN = Side(style="thin", color="D1D5DB")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="1F2937")
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY_FONT = Font(name=FONT, size=10)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(wrap_text=True, vertical="top", horizontal="center")

PAGE_WIDTHS = {"页码": 6, "页型": 10, "推荐模板": 21, "主标题": 24, "副标题": 24,
               "正文块1": 30, "正文块2": 30, "正文块3": 30, "配图描述": 24,
               "配图URL文件": 22, "演讲者备注": 36, "待补项": 30, "制作备注": 26}


def _header(ws, cols, widths=None):
    for c, name in enumerate(cols, 1):
        cell = ws.cell(row=1, column=c, value=name)
        cell.fill, cell.font, cell.border = HEAD_FILL, HEAD_FONT, BORDER
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(c)].width = (widths or {}).get(name, 14)
    ws.row_dimensions[1].height = 24


def _cell(ws, r, c, v, align=WRAP, font=BODY_FONT):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font, cell.alignment, cell.border = font, align, BORDER
    return cell


def _pending_cf(ws, rng, top_left):
    ws.conditional_formatting.add(rng, FormulaRule(
        formula=[f'LEFT({top_left},{len(TODO_PREFIX)})="{TODO_PREFIX}"'],
        fill=PatternFill("solid", fgColor=PENDING_FILL, bgColor=PENDING_FILL)))


def _na_cf(ws, rng, top_left):
    ws.conditional_formatting.add(rng, FormulaRule(
        formula=[f'{top_left}="{NA}"'], font=Font(color="9CA3AF")))


def pending_summary(p: Page) -> str:
    items = [f"{f}：{v.desc}" for f, v in p.fields.items() if isinstance(v, Pending)]
    return "；\n".join(items) if items else NA


def write_workbook(path, title, tpls, pages, globals_):
    wb = Workbook()
    n = len(pages)
    last = n + 51  # 预留 50 行，用户追加页面时样式、下拉照样生效

    # ---- 页面工单 ----
    ws = wb.active
    ws.title = SHEET_PAGES
    _header(ws, PAGE_COLUMNS, PAGE_WIDTHS)
    col = {name: i for i, name in enumerate(PAGE_COLUMNS, 1)}
    for r, p in enumerate(pages, 2):
        _cell(ws, r, col["页码"], p.page, CENTER)
        _cell(ws, r, col["页型"], p.page_type, CENTER)
        _cell(ws, r, col["推荐模板"], p.template_display)
        for f in FIELDS:
            _cell(ws, r, col[f], cell_text(p.fields[f]))
        _cell(ws, r, col["待补项"], pending_summary(p),
              font=Font(name=FONT, size=10, color="B91C1C"))
        _cell(ws, r, col["制作备注"], p.note or NA)
    for r in range(n + 2, last + 1):  # 预留行只带边框
        for c in range(1, len(PAGE_COLUMNS) + 1):
            ws.cell(row=r, column=c).border = BORDER
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(PAGE_COLUMNS))}{n + 1}"
    first_f, last_f = get_column_letter(col["主标题"]), get_column_letter(col["演讲者备注"])
    _pending_cf(ws, f"{first_f}2:{last_f}{last}", f"{first_f}2")
    _na_cf(ws, f"{first_f}2:{get_column_letter(len(PAGE_COLUMNS))}{last}", f"{first_f}2")

    page_types = []
    for t in tpls:
        if t.page_type not in page_types:
            page_types.append(t.page_type)
    type_list = ",".join(page_types)
    if len(type_list) <= 250:
        dv_type = DataValidation(type="list", formula1=f'"{type_list}"', allow_blank=True)
        dv_type.error, dv_type.errorTitle = "请从下拉选择页型", "页型不在模板目录中"
        ws.add_data_validation(dv_type)
        dv_type.add(f"B2:B{last}")
    dv_tpl = DataValidation(type="list", allow_blank=True,
                            formula1=f"'{SHEET_TPLS}'!$A$2:$A${len(tpls) + 1}")
    dv_tpl.error = "请从下拉选择，格式为「中文名（ID）」；新版式要先在模板目录登记"
    dv_tpl.errorTitle = "模板不在模板目录中"
    ws.add_data_validation(dv_tpl)
    dv_tpl.add(f"C2:C{last}")

    # ---- 模板目录 ----
    wt = wb.create_sheet(SHEET_TPLS)
    _header(wt, TPL_COLUMNS, {"模板（下拉值）": 18, "长什么样": 36, "适合什么时候用": 28,
                              "必填字段": 24, "可选字段": 24, "内容形态": 16, "来源": 16})
    tcol = {name: i for i, name in enumerate(TPL_COLUMNS, 1)}
    page_rng = f"'{SHEET_PAGES}'!$C$2:$C${last}"
    count_rng = f"'{SHEET_PAGES}'!$A$2:$A${last}"
    for r, t in enumerate(tpls, 2):
        row = {
            "模板（下拉值）": t.display, "模板ID": t.id, "中文名": t.name, "页型": t.page_type,
            "长什么样": t.looks_like or NA, "适合什么时候用": t.use_when or NA,
            "必填字段": "、".join(t.required) or NA, "可选字段": "、".join(t.optional) or NA,
            "正文槽位数": t.slots, "并列点数上限": t.max_points,
            "内容形态": t.content_form or NA, "配图需求": t.image_need,
            "节奏定位": t.rhythm or NA, "来源": t.source or NA,
        }
        for k, colname in LIMIT_KEYS.items():
            row[colname] = t.limits.get(k, NA)
        for name, v in row.items():
            align = CENTER if isinstance(v, int) or v == NA else WRAP
            _cell(wt, r, tcol[name], v, align)
        cnt = get_column_letter(tcol["本套使用次数"])
        _cell(wt, r, tcol["本套使用次数"], f"=COUNTIF({page_rng},A{r})", CENTER)
        c = _cell(wt, r, tcol["占比"],
                  f"=IF(COUNTA({count_rng})=0,0,{cnt}{r}/COUNTA({count_rng}))", CENTER)
        c.number_format = "0%"
    end = len(tpls) + 1
    cnt = get_column_letter(tcol["本套使用次数"])
    bold = Font(name=FONT, size=10, bold=True)
    _cell(wt, end + 2, 1, "本套总页数", font=bold)
    _cell(wt, end + 2, 2, f"=COUNTA({count_rng})", CENTER)
    _cell(wt, end + 3, 1, "已用版式数", font=bold)
    _cell(wt, end + 3, 2, f'=COUNTIF({cnt}2:{cnt}{end},">0")&" / {len(tpls)}"', CENTER)
    _cell(wt, end + 4, 1, "未用版式", font=bold)
    wt.cell(row=end + 4, column=2,
            value="本套使用次数为 0 的行；节奏点版式（金句、卡片）全套少量使用即可").font = BODY_FONT
    wt.conditional_formatting.add(f"A2:{get_column_letter(len(TPL_COLUMNS))}{end}", FormulaRule(
        formula=[f"${cnt}2=0"], font=Font(color="9CA3AF")))
    wt.freeze_panes = "C2"

    # ---- 全局设置 ----
    wg = wb.create_sheet(SHEET_GLOBAL)
    _header(wg, GLOBAL_COLUMNS, {"设置项": 14, "值": 36, "用在哪里 / 填写说明": 40})
    for r, (k, v, hint) in enumerate(globals_, 2):
        _cell(wg, r, 1, k, font=bold)
        _cell(wg, r, 2, cell_text(v))
        _cell(wg, r, 3, hint)
    gend = len(globals_) + 1
    _pending_cf(wg, f"B2:B{gend}", "B2")
    _na_cf(wg, f"B2:B{gend}", "B2")
    for i, line in enumerate(LEGEND):
        r = gend + 2 + i
        wg.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
        c = wg.cell(row=r, column=1, value=line)
        c.font = bold if i == 0 else BODY_FONT
        c.alignment = WRAP
        if i == 1:
            c.fill = PatternFill("solid", fgColor=PENDING_FILL)
    if title:
        wg.cell(row=gend + 2 + len(LEGEND) + 1, column=1, value=f"工单：{title}").font = bold

    wb.properties.title = title or "PPT 工单"
    wb.save(path)


# ---------------------------------------------------------------------------
# 回读工作簿
# ---------------------------------------------------------------------------


def _header_map(ws, expected, rep, sheet):
    heads = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    hmap = {h: i + 1 for i, h in enumerate(heads) if h}
    missing = [h for h in expected if h not in hmap]
    if missing:
        rep.err(f"「{sheet}」缺少列：{'、'.join(missing)}")
    return hmap


def _int_or_none(v):
    if v in (None, "", NA):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def read_workbook(path, rep: Report):
    wb = load_workbook(path)
    for s in (SHEET_PAGES, SHEET_TPLS, SHEET_GLOBAL):
        if s not in wb.sheetnames:
            rep.err(f"缺少工作表「{s}」")
    if rep.errors:
        return [], [], []

    # 模板目录
    wt = wb[SHEET_TPLS]
    h = _header_map(wt, TPL_COLUMNS[:17], rep, SHEET_TPLS)
    tpls = []
    r = 2
    while wt.cell(row=r, column=h.get("模板ID", 2)).value not in (None, ""):
        g = lambda name: wt.cell(row=r, column=h[name]).value if name in h else None  # noqa: E731
        split = lambda s: [] if s in (None, "", NA) else [x.strip() for x in re.split(r"[、,，]", str(s)) if x.strip()]  # noqa: E731
        limits = {k: _int_or_none(g(col)) for k, col in LIMIT_KEYS.items()}
        tpls.append(Template(
            id=str(g("模板ID")).strip(), name=str(g("中文名") or "").strip(),
            page_type=str(g("页型") or "").strip(), looks_like=g("长什么样") or "",
            use_when=g("适合什么时候用") or "", required=split(g("必填字段")),
            optional=split(g("可选字段")), max_points=_int_or_none(g("并列点数上限")) or 0,
            limits={k: v for k, v in limits.items() if v is not None},
            content_form=g("内容形态") or "", rhythm=g("节奏定位") or "",
            source=g("来源") or "", declared_slots=_int_or_none(g("正文槽位数"))))
        r += 1

    # 页面工单
    ws = wb[SHEET_PAGES]
    h = _header_map(ws, PAGE_COLUMNS, rep, SHEET_PAGES)
    if rep.errors:
        return tpls, [], []
    pages = []
    r = 2
    while True:
        rowvals = {name: ws.cell(row=r, column=c).value for name, c in h.items()}
        if all(v in (None, "") for v in rowvals.values()):
            break
        where = f"工单第 {r} 行"
        pno = _int_or_none(rowvals.get("页码"))
        if pno is None:
            rep.err(f"{where}：页码为空或不是数字")
        disp = str(rowvals.get("推荐模板") or "").strip()
        m = DISPLAY_RE.match(disp)
        if not m:
            rep.err(f"{where}：推荐模板「{disp}」不是「中文名（ID）」格式")
        vals = {}
        for f in FIELDS:
            try:
                vals[f] = norm_value(rowvals.get(f))
            except ValueError as e:
                rep.err(f"{where} {f}：{e}")
                vals[f] = NA
        note = norm_value(rowvals.get("制作备注"))
        pages.append(Page(page=pno if pno is not None else f"?{r}",
                          page_type=str(rowvals.get("页型") or "").strip(),
                          template_id=m.group(2) if m else "", template_display=disp,
                          fields=vals, note=note if isinstance(note, str) else NA))
        r += 1

    # 全局设置
    wg = wb[SHEET_GLOBAL]
    globals_ = []
    r = 2
    while wg.cell(row=r, column=1).value not in (None, ""):
        k = str(wg.cell(row=r, column=1).value).strip()
        v = norm_value(wg.cell(row=r, column=2).value)
        if v is None:
            rep.err(f"全局设置 {k}：值为空。不需要请填「/」，缺失请标【待补】")
            v = NA
        if isinstance(v, Pending):
            rep.pendings.append((None, f"全局设置·{k}", v.desc))
        globals_.append((k, v, wg.cell(row=r, column=3).value or ""))
        r += 1
    return tpls, pages, globals_


# ---------------------------------------------------------------------------
# 成品比对
# ---------------------------------------------------------------------------


def _squash(s: str) -> str:
    return re.sub(r"\s", "", s or "")


def verify_pptx(pages, path, rep: Report):
    try:
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        from pptx.shapes.picture import Picture
    except ImportError:
        rep.err("比对成品需要 python-pptx：pip install python-pptx")
        return
    prs = Presentation(path)
    slides = list(prs.slides)
    if len(slides) != len(pages):
        rep.err(f"成品 {len(slides)} 页，工单 {len(pages)} 页，页数不一致")

    def walk(shapes):
        for sh in shapes:
            if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                yield from walk(sh.shapes)
            else:
                yield sh

    for i, (slide, p) in enumerate(zip(slides, pages), 1):
        texts, has_pic = [], False
        for sh in walk(slide.shapes):
            if isinstance(sh, Picture):  # 含占位符里的图片
                has_pic = True
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                t = sh.text_frame.text
                texts.append(t)
                if sh.is_placeholder and not t.strip():
                    rep.warn(f"成品第 {i} 页：有空占位符「{sh.name}」，放映时可能显示提示文字")
            if getattr(sh, "has_table", False) and sh.has_table:
                texts += [c.text for row in sh.table.rows for c in row.cells]
        joined = _squash("".join(texts))
        if not joined and not has_pic:
            rep.err(f"成品第 {i} 页是空白页")
        title = p.fields.get("主标题")
        if isinstance(title, str) and title != NA and _squash(title) not in joined:
            rep.err(f"成品第 {i} 页没找到工单主标题「{title}」：页序错位或措辞被改写")
        if TODO_PREFIX in joined:
            rep.warn(f"成品第 {i} 页仍有【待补】占位")
        notes = p.fields.get("演讲者备注")
        if isinstance(notes, str) and notes != NA:
            got = _squash(slide.notes_slide.notes_text_frame.text) if slide.has_notes_slide else ""
            if _squash(notes)[:12] not in got:
                rep.warn(f"成品第 {i} 页演讲者备注未写入或与工单不一致")


# ---------------------------------------------------------------------------
# 导出逐页 JSON（出片时的唯一内容依据）
# ---------------------------------------------------------------------------


def export_json(path, tpls, pages, globals_):
    def jv(v):
        if isinstance(v, Pending):
            return v.to_json()
        return None if v == NA else v

    tmap = {t.id: t for t in tpls}
    data = {
        "global": {k: jv(v) for k, v, _ in globals_},
        "pages": [{
            "页码": p.page, "页型": p.page_type, "模板ID": p.template_id,
            "模板": p.template_display,
            "模板来源": tmap[p.template_id].source if p.template_id in tmap else None,
            **{f: jv(p.fields.get(f)) for f in FIELDS},
            "制作备注": None if p.note == NA else p.note,
        } for p in pages],
        "说明": "null = 本页不适用（工单里的「/」）；{todo} = 仍待补，出片时保留可见占位，禁止编造",
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 子命令
# ---------------------------------------------------------------------------


def load_order(data: dict, rep: Report):
    tpl_dicts = data.get("templates") or DEFAULT_TEMPLATES
    tpls = [template_from_dict(d) for d in tpl_dicts]
    validate_templates(tpls, rep)
    tmap = {t.id: t for t in tpls}
    pages = pages_from_json(data.get("pages") or [], tmap, rep)
    validate_pages(pages, tmap, rep)
    globals_ = globals_from_json(data.get("global"), rep)
    return tpls, pages, globals_


def cmd_build(json_path, out, quiet=False):
    with open(json_path, encoding="utf-8") as fh:
        data = json.load(fh)
    rep = Report()
    tpls, pages, globals_ = load_order(data, rep)
    if not quiet:
        rep.print()
    if rep.errors:
        if not quiet:
            print("未生成工单：先修正以上错误（超容量请拆页或换版式）。", file=sys.stderr)
        return 1, rep
    write_workbook(out, data.get("title", ""), tpls, pages, globals_)
    if not quiet:
        print(f"已生成：{out}")
    return 0, rep


def cmd_check(xlsx, strict=False, out=None, pptx=None, quiet=False):
    rep = Report()
    tpls, pages, globals_ = read_workbook(xlsx, rep)
    if tpls:
        validate_templates(tpls, rep)
    if pages:
        validate_pages(pages, {t.id: t for t in tpls}, rep)
    if pptx and pages:
        verify_pptx(pages, pptx, rep)
    if out and not rep.errors:
        export_json(out, tpls, pages, globals_)
    if not quiet:
        rep.print()
        if out and not rep.errors:
            print(f"已导出逐页数据：{out}")
    if rep.errors:
        return 1, rep
    if strict and rep.pendings:
        if not quiet:
            print("仍有待补项：补齐，或由用户明确同意保留占位后再出片。", file=sys.stderr)
        return 2, rep
    return 0, rep


# ---------------------------------------------------------------------------
# 示例数据与自测
# ---------------------------------------------------------------------------

DEMO = {
    "title": "用 WorkBuddy 把个人经验变成可复用的数字资产（示例）",
    "global": {
        "讲师姓名": {"todo": "讲师姓名"},
        "讲师头衔": {"todo": "讲师头衔（≤24 字）"},
        "活动名称": {"todo": "活动正式名称", "draft": "WorkBuddy 线下沙龙"},
        "活动日期": {"todo": "活动日期"},
        "品牌主色": "#1F6FEB",
        "品牌辅色": "#F3F4F6",
        "字体": "思源黑体",
        "Logo文件": "/",
    },
    "pages": [
        {"页码": 1, "模板ID": "cover", "主标题": "把经验存下来，让 AI 越用越懂你",
         "副标题": "用 WorkBuddy 把个人经验变成可复用的数字资产",
         "正文块1": {"todo": "讲师姓名、活动日期", "draft": "讲师｜WorkBuddy 线下沙龙｜日期"},
         "演讲者备注": "开场先问：用 AI 是不是每次都要从头交代？"},
        {"页码": 2, "模板ID": "speaker", "主标题": {"todo": "讲师姓名"},
         "副标题": {"todo": "讲师头衔"}, "正文块1": {"todo": "3 条履历要点，每条 ≤24 字"},
         "配图描述": "讲师半身照，浅色背景", "配图URL文件": {"todo": "讲师照片文件"}},
        {"页码": 3, "模板ID": "viewpoint", "主标题": "AI 回答的多半是正确的废话",
         "副标题": "缺的不是能力，是你的经验",
         "正文块1": "每次都要从头交代背景\n用了半年，它还是不了解你\n换个对话，之前教的全忘了",
         "演讲者备注": "停顿，让台下举手：谁有同感？"},
        {"页码": 4, "模板ID": "two-col", "主标题": "资料柜 vs 操作手册",
         "正文块1": "知识库：存事实\n管 AI 知道什么\n适合产品资料、FAQ",
         "正文块2": "Skill：存做法\n管 AI 怎么干活\n适合反复要交代的流程"},
        {"页码": 5, "模板ID": "quote", "主标题": "同样的要求说到第二遍，就该做成 Skill"},
        {"页码": 6, "模板ID": "section", "主标题": "经验为什么很难变成资产",
         "副标题": "四个常见卡点"},
        {"页码": 7, "模板ID": "three-card", "主标题": "前三个卡点",
         "正文块1": "会做≠说得出：判断已经变成直觉",
         "正文块2": "看不出重复：每次都觉得这次不一样",
         "正文块3": "第一版不好用：要像带徒弟一样改几轮",
         "制作备注": "原有 4 个并列点，超出三卡片容量：拆为本页 + 第 8 页观点页"},
        {"页码": 8, "模板ID": "viewpoint", "主标题": "别从零写，先拿现成的再改成自己的",
         "副标题": "第四个卡点：几百行的官方 Skill 把人吓住了",
         "正文块1": "找一个现成的 Skill 先用起来\n记下每次都得手动改的地方\n把这几处判断写进去"},
        {"页码": 9, "模板ID": "img-text", "主标题": "现场演示：20 份客户聊天记录",
         "正文块1": "放入聊天记录\n一句话生成 Skill\n加入我的判断再跑一次\n对比依据原话和下一句话术",
         "配图描述": "Skill 改造前后两次运行结果的对比截图",
         "配图URL文件": {"todo": "演示截图（提前录屏后截取）"},
         "演讲者备注": "演示视频提前录好备份，现场网络不稳就切视频"},
        {"页码": 10, "模板ID": "quote", "主标题": "资产不是那个文件，是你沉淀的那几条判断"},
        {"页码": 11, "模板ID": "ending", "主标题": "回家做第一个 Skill",
         "副标题": "扫码领取 Skill 改造包",
         "正文块1": "作业：找一件你说过两遍的事，改成你自己的 Skill",
         "配图描述": "个人微信二维码", "配图URL文件": {"todo": "真实二维码图片，禁止用示意图代替"},
         "演讲者备注": "二维码在答疑期间一直保留在屏幕上"},
    ],
}


def cmd_demo(outdir):
    os.makedirs(outdir, exist_ok=True)
    jp = os.path.join(outdir, "demo_order.json")
    xp = os.path.join(outdir, "示例工单.xlsx")
    with open(jp, "w", encoding="utf-8") as fh:
        json.dump(DEMO, fh, ensure_ascii=False, indent=2)
    code, _ = cmd_build(jp, xp)
    print(f"示例输入：{jp}")
    return code


def selftest():
    import copy
    tmp = tempfile.mkdtemp(prefix="ppt_order_selftest_")
    results = []

    def case(name, ok, detail=""):
        results.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail and not ok else ''}")

    def build(data, name):
        jp = os.path.join(tmp, name + ".json")
        xp = os.path.join(tmp, name + ".xlsx")
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
        code, rep = cmd_build(jp, xp, quiet=True)
        return code, rep, xp

    try:
        # 1. 默认版式自洽
        rep = Report()
        validate_templates([template_from_dict(d) for d in DEFAULT_TEMPLATES], rep)
        case("默认 9 种版式定义自洽", not rep.errors and len(DEFAULT_TEMPLATES) == 9,
             "; ".join(rep.errors))

        # 2. 正例：生成工单
        code, rep, xp = build(DEMO, "ok")
        case("示例工单生成成功", code == 0 and os.path.exists(xp), "; ".join(rep.errors))
        case("示例工单无节奏提醒", not rep.warnings, "; ".join(rep.warnings))
        wb = load_workbook(xp)
        case("三个 sheet 名称正确", wb.sheetnames == [SHEET_PAGES, SHEET_TPLS, SHEET_GLOBAL],
             str(wb.sheetnames))
        ws = wb[SHEET_PAGES]
        heads = [ws.cell(row=1, column=c).value for c in range(1, len(PAGE_COLUMNS) + 1)]
        case("页面工单列与规范一致", heads == PAGE_COLUMNS, str(heads))
        rows = [[ws.cell(row=r, column=c).value for c in range(1, len(PAGE_COLUMNS) + 1)]
                for r in range(2, len(DEMO["pages"]) + 2)]
        case("一页一行", len(rows) == len(DEMO["pages"]) and ws.cell(
            row=len(DEMO["pages"]) + 2, column=1).value is None)
        empty = [(r[0], PAGE_COLUMNS[i]) for r in rows for i, v in enumerate(r) if v in (None, "")]
        case("无空单元格（不适用一律为 /）", not empty, str(empty[:5]))
        case("推荐模板为「中文名（ID）」", all(DISPLAY_RE.match(r[2]) for r in rows))
        p2 = rows[1]
        case("待补格以【待补】开头", str(p2[3]).startswith(TODO_PREFIX))
        case("待补项列写明缺什么", "配图URL文件：讲师照片文件" in p2[11], p2[11])
        case("无待补的页待补项为 /", rows[2][11] == NA)
        case("不适用字段为 /", rows[3][4] == NA and rows[4][5] == NA)
        cf_ranges = [str(r.sqref) for r in ws.conditional_formatting]
        case("待补浅红底条件格式存在", any("D2:K" in s for s in cf_ranges), str(cf_ranges))
        case("页型/模板下拉存在", len(ws.data_validations.dataValidation) == 2)
        wt = wb[SHEET_TPLS]
        th = [wt.cell(row=1, column=c).value for c in range(1, len(TPL_COLUMNS) + 1)]
        f = wt.cell(row=2, column=th.index("本套使用次数") + 1).value
        case("模板目录含使用次数公式", isinstance(f, str) and f.startswith("=COUNTIF("), str(f))

        # 3. 回读往返
        code, rep = cmd_check(xp, quiet=True)
        case("回读校验无错误", code == 0 and not rep.errors, "; ".join(rep.errors))
        expect_pending = sum(1 for p in DEMO["pages"] for v in p.values()
                             if isinstance(v, dict)) + \
            sum(1 for v in DEMO["global"].values() if isinstance(v, dict))
        case("待补项数量一致", len(rep.pendings) == expect_pending,
             f"{len(rep.pendings)} vs {expect_pending}")
        code, _ = cmd_check(xp, strict=True, quiet=True)
        case("strict 模式有待补时退出码 2", code == 2)

        # 4. 用户补齐后通过 strict，并能导出 JSON
        wb = load_workbook(xp)
        for sh in (wb[SHEET_PAGES], wb[SHEET_GLOBAL]):
            for row in sh.iter_rows(min_row=2):
                for c in row:
                    if isinstance(c.value, str) and c.value.startswith(TODO_PREFIX):
                        c.value = "示例补齐" if c.column_letter != "J" else "photo.png"
        filled = os.path.join(tmp, "filled.xlsx")
        wb.save(filled)
        out_json = os.path.join(tmp, "pages.json")
        code, rep = cmd_check(filled, strict=True, out=out_json, quiet=True)
        case("补齐后 strict 通过并导出", code == 0 and os.path.exists(out_json),
             "; ".join(rep.errors + [d for _, _, d in rep.pendings]))
        with open(out_json, encoding="utf-8") as fh:
            exported = json.load(fh)
        case("导出 JSON 页序与工单一致",
             [p["页码"] for p in exported["pages"]] == list(range(1, len(DEMO["pages"]) + 1)))

        # 5. 用户在表里写超了，也能被 check 拦下
        wb = load_workbook(filled)
        wb[SHEET_PAGES]["D6"] = "这是一个故意写得非常非常长的金句页标题，用来测试回读时的字数上限检查"
        bad = os.path.join(tmp, "bad_edit.xlsx")
        wb.save(bad)
        code, rep = cmd_check(bad, quiet=True)
        case("回读拦截超字数", code == 1 and any("超过上限" in e for e in rep.errors))

        # 6. 反例：build 拒绝出文件
        def neg(name, mutate, keyword):
            d = copy.deepcopy(DEMO)
            mutate(d)
            code, rep, xp = build(d, f"neg_{len(results)}")
            ok = code == 1 and not os.path.exists(xp) and any(keyword in e for e in rep.errors)
            case(f"反例：{name}", ok, "; ".join(rep.errors) or "未报错")

        neg("并列点超容量", lambda d: d["pages"][3].update(
            {"正文块1": "一\n二\n三\n四", "正文块2": "五\n六\n七"}), "并列点")
        neg("单块超字数", lambda d: d["pages"][6].update(
            {"正文块1": "这是一个很长很长的卡片说明，远远超过三卡片版式每块三十六个字的上限，必须拆页"}),
            "超过上限")
        neg("不适用字段有内容", lambda d: d["pages"][4].update({"正文块1": "金句页不该有正文"}),
            "应为「/」")
        neg("必填为空", lambda d: d["pages"][3].pop("正文块2"), "必填却为空")
        neg("未登记的版式", lambda d: d["pages"][3].update({"模板ID": "four-card"}), "不在模板目录")
        neg("有配图描述却标 /", lambda d: d["pages"][8].update({"配图URL文件": "/"}), "不要编造")
        neg("页码不连续", lambda d: d["pages"][2].update({"页码": 9}), "连续递增")

        # 7. 节奏提醒
        d = copy.deepcopy(DEMO)
        d["pages"][4] = {"页码": 5, "模板ID": "two-col", "主标题": "再来一页双栏",
                         "正文块1": "甲", "正文块2": "乙"}
        code, rep, _ = build(d, "rhythm")
        case("连续同版式给出提醒", code == 0 and any("连续使用" in w for w in rep.warnings))

        # 8. 成品比对
        try:
            from pptx import Presentation
            from pptx.util import Inches
        except ImportError:
            print("[SKIP] 未安装 python-pptx，跳过成品比对")
        else:
            prs = Presentation()
            for p in exported["pages"]:
                s = prs.slides.add_slide(prs.slide_layouts[5])
                s.shapes.title.text = p["主标题"]
                tb = s.shapes.add_textbox(Inches(1), Inches(2), Inches(6), Inches(2))
                tb.text_frame.text = p.get("正文块1") or ""
                if p.get("演讲者备注"):
                    s.notes_slide.notes_text_frame.text = p["演讲者备注"]
            good = os.path.join(tmp, "deck.pptx")
            prs.save(good)
            code, rep = cmd_check(filled, pptx=good, quiet=True)
            case("成品页数页序一致时通过", code == 0, "; ".join(rep.errors))
            # 交换两页 → 页序错位
            ids = prs.slides._sldIdLst
            el = ids[2]
            ids.remove(el)
            ids.insert(4, el)
            swapped = os.path.join(tmp, "deck_swapped.pptx")
            prs.save(swapped)
            code, rep = cmd_check(filled, pptx=swapped, quiet=True)
            case("成品页序错位被发现", code == 1 and any("页序" in e for e in rep.errors))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    passed = sum(results)
    print(f"—— {passed}/{len(results)} 通过")
    return 0 if passed == len(results) else 1


# ---------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description="工单驱动 PPT 生产：工单生成与校验",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("用法", 1)[1].split("依赖", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="由 JSON 生成工单 xlsx")
    b.add_argument("json")
    b.add_argument("-o", "--out", required=True)
    c = sub.add_parser("check", help="回读校验工单 xlsx")
    c.add_argument("xlsx")
    c.add_argument("--strict", action="store_true", help="仍有待补项时退出码 2")
    c.add_argument("--out", help="导出逐页 JSON（出片依据）")
    c.add_argument("--pptx", help="比对成品 PPTX 的页数、页序、空白页")
    d = sub.add_parser("demo", help="生成示例 JSON 与示例工单")
    d.add_argument("--outdir", default="ppt-order-demo")
    sub.add_parser("selftest", help="运行自测")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        return cmd_build(a.json, a.out)[0]
    if a.cmd == "check":
        return cmd_check(a.xlsx, a.strict, a.out, a.pptx)[0]
    if a.cmd == "demo":
        return cmd_demo(a.outdir)
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
