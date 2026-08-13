#!/usr/bin/env python3
"""Build a link-only catalog of CUMCM excellent-paper references.

The script fixes every GitHub record to an immutable commit, removes obvious
non-paper PDFs and duplicate Git blobs, and cross-checks recent showcase codes
against the CUMCM paper display hosted by China Education Online.  It does not
download or redistribute any paper PDF.
"""

from __future__ import annotations

import csv
import html
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path


PRIMARY_REPOSITORY = "Xiaocold-B216/cumcm-modeling-Award-Collection"
PRIMARY_COMMIT = "a042ecf898feaba6fc81d543a10e0188db8b2b12"
GITHUB_TREE_API = (
    f"https://api.github.com/repos/{PRIMARY_REPOSITORY}/git/trees/"
    f"{PRIMARY_COMMIT}?recursive=1"
)
GITHUB_REPOSITORY_URL = f"https://github.com/{PRIMARY_REPOSITORY}"

OFFICIAL_ENTRY = (
    "https://www.mcm.edu.cn/html_cn/block/"
    "018500ec1a6bd8c7e9997133def2b590.html"
)
OFFICIAL_SHOWCASE_INDEX = (
    "https://dxs.moe.gov.cn/zx/hd/sxjm/sxjmlw/"
    "qkt_sxjm_lw_lwzs.shtml"
)
OFFICIAL_BASE = "https://dxs.moe.gov.cn"

HERE = Path(__file__).resolve().parent
TRAINING = HERE.parent
JSON_OUTPUT = TRAINING / "cumcm_high_score_papers_catalog.json"
CSV_OUTPUT = TRAINING / "cumcm_high_score_papers_catalog.csv"
REPORT_OUTPUT = TRAINING / "cumcm_high_score_papers_catalog.md"

USER_AGENT = "mathmodel2026-reference-audit/1.0"

# Only filename or terminal path components are tested.  Parent directories
# such as “真题+优秀论文” legitimately contain both problems and papers.
NON_PAPER_NAME = re.compile(
    r"(国赛赛题|竞赛赛题|赛题(?:及|与)?附件|^\d{4}年?赛题|"
    r"参赛规则|竞赛规则|论文格式(?:规范)?|通知|章程|报名|"
    r"附件|支撑材料|源程序|计算结果|"
    r"优秀论文全集|论文合集|论文汇编|论文集(?:上|下)?册)",
    re.IGNORECASE,
)
COMMENTARY_NAME = re.compile(
    r"(评述|评注|评阅|点评|"
    r"命题与评阅|问题及有关情况|解题思路)",
    re.IGNORECASE,
)
PAPER_CONTEXT = re.compile(r"(优秀论文|展示论文|一等奖论文|获奖论文)")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json, text/html;q=0.9, */*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def fetch_text(url: str) -> str:
    return fetch(url).decode("utf-8", errors="replace")


def norm_showcase_code(code: str) -> str:
    match = re.fullmatch(r"([A-Fa-f])0*(\d+)", code.strip())
    if not match:
        return code.upper()
    return f"{match.group(1).upper()}{int(match.group(2))}"


def extract_year(value: str) -> int | None:
    match = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", value)
    return int(match.group(1)) if match else None


def extract_problem(value: str) -> str | None:
    stem = Path(value).stem
    patterns = (
        r"(?:19|20)\d{2}年?\s*([A-Fa-f])(?:题|[:：_\-]|\d)",
        r"(?:19|20)\d{2}([A-Fa-f])(?=\D|$)",
        r"^\s*([A-Fa-f])(?:题|[:：_\-]|\d{2,4})",
        r"[（(]([A-Fa-f])\d{2,4}[）)]",
    )
    for pattern in patterns:
        match = re.search(pattern, stem)
        if match:
            return match.group(1).upper()
    return None


def extract_showcase_code(filename: str) -> str | None:
    stem = Path(filename).stem
    candidates = re.findall(r"(?<![A-Za-z])([A-Fa-f]0*\d{2,4})(?!\d)", stem)
    return norm_showcase_code(candidates[-1]) if candidates else None


def clean_title(filename: str) -> str:
    stem = unicodedata.normalize("NFKC", Path(filename).stem).strip()
    stem = re.sub(
        r"^(?:19|20)\d{2}年?(?:高教社杯)?(?:全国大学生数学建模竞赛)?",
        "",
        stem,
    )
    stem = re.sub(
        r"^[A-Fa-f](?:题)?(?:优秀论文)?(?:[①②③④⑤⑥⑦⑧⑨⑩]|\d{2,4})?\s*",
        "",
        stem,
    )
    stem = re.sub(r"^(?:一等奖)?优秀论文\s*", "", stem)
    return stem.lstrip(" :：_-—") or Path(filename).stem


def official_showcase_records() -> tuple[dict[tuple[int, str], str], list[str]]:
    """Return {(year, normalized code): official detail URL}."""
    index_html = fetch_text(OFFICIAL_SHOWCASE_INDEX)
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', index_html, flags=re.I)
    annual_urls: dict[int, str] = {}
    for href in hrefs:
        decoded = html.unescape(href)
        match = re.search(r"/(20(?:1[2-9]|2[0-5]))qgdxssxjmjslwzs/", decoded)
        if not match:
            continue
        year = int(match.group(1))
        annual_urls.setdefault(year, urllib.parse.urljoin(OFFICIAL_BASE, decoded))

    records: dict[tuple[int, str], str] = {}
    successfully_read: list[str] = []
    for year, annual_url in sorted(annual_urls.items()):
        try:
            page = fetch_text(annual_url)
        except Exception:
            continue
        successfully_read.append(annual_url)
        # A visible code can be in a sibling tag, so associate each code with the
        # nearest preceding href inside a short bounded window.  Unbounded DOTALL
        # matching can accidentally bind a code to a stylesheet or favicon.
        for code_match in re.finditer(
            r"(?:（|\()([A-Fa-f]0*\d{2,4})(?:）|\))", page
        ):
            window = page[max(0, code_match.start() - 1800) : code_match.start()]
            href_candidates = re.findall(r'href=["\']([^"\']+)["\']', window, re.I)
            detail_url = annual_url
            for href in reversed(href_candidates):
                candidate = urllib.parse.urljoin(OFFICIAL_BASE, html.unescape(href))
                if "/zx/a/hd_sxjm_sxjmlw_" in candidate and candidate.endswith(".shtml"):
                    detail_url = candidate
                    break
            records[(year, norm_showcase_code(code_match.group(1)))] = detail_url
    return records, successfully_read


def github_papers() -> tuple[list[dict], dict]:
    payload = json.loads(fetch(GITHUB_TREE_API))
    if payload.get("truncated"):
        raise RuntimeError("GitHub recursive tree was truncated; catalog would be incomplete")

    all_pdfs = [
        item
        for item in payload["tree"]
        if item.get("type") == "blob" and item["path"].lower().endswith(".pdf")
    ]
    accepted: list[dict] = []
    rejection_reasons: Counter[str] = Counter()
    seen_blob: set[str] = set()

    for item in sorted(all_pdfs, key=lambda value: value["path"]):
        path = unicodedata.normalize("NFKC", item["path"])
        filename = path.rsplit("/", 1)[-1]
        parent = path.rsplit("/", 2)[-2] if "/" in path else ""
        year = extract_year(path)
        if item["sha"] in seen_blob:
            rejection_reasons["duplicate_git_blob"] += 1
            continue
        if year is None:
            rejection_reasons["year_not_detected"] += 1
            continue
        if not PAPER_CONTEXT.search(path):
            rejection_reasons["no_paper_collection_context"] += 1
            continue
        if "国赛赛题" in parent and not PAPER_CONTEXT.search(parent):
            rejection_reasons["problem_statement_parent"] += 1
            continue
        if NON_PAPER_NAME.search(filename) or NON_PAPER_NAME.search(parent):
            rejection_reasons["problem_rule_attachment_or_collection"] += 1
            continue
        if COMMENTARY_NAME.search(filename):
            rejection_reasons["review_or_commentary"] += 1
            continue
        if int(item.get("size") or 0) < 90_000:
            rejection_reasons["too_small_for_paper_pdf"] += 1
            continue
        seen_blob.add(item["sha"])
        quoted_path = urllib.parse.quote(item["path"], safe="/")
        accepted.append(
            {
                "year": year,
                "problem": extract_problem(path),
                "showcase_code": extract_showcase_code(filename),
                "title": clean_title(filename),
                "authors": None,
                "doi": None,
                "bytes": int(item.get("size") or 0),
                "git_blob_sha1": item["sha"],
                "repository_path": item["path"],
                "source_url": (
                    f"{GITHUB_REPOSITORY_URL}/blob/{PRIMARY_COMMIT}/{quoted_path}"
                ),
            }
        )

    diagnostics = {
        "github_tree_items": len(payload["tree"]),
        "github_pdf_files": len(all_pdfs),
        "accepted_unique_paper_records": len(accepted),
        "rejected": dict(sorted(rejection_reasons.items())),
    }
    return accepted, diagnostics


def build_catalog() -> dict:
    papers, diagnostics = github_papers()
    official, annual_urls = official_showcase_records()

    for paper in papers:
        key = (paper["year"], paper["showcase_code"] or "")
        official_url = official.get(key)
        if official_url:
            paper["verification_status"] = "official_showcase_match"
            paper["evidence_grade"] = "S"
            paper["quality_claim"] = "selected for the official CUMCM paper showcase"
            paper["official_showcase_url"] = official_url
        else:
            paper["verification_status"] = "repository_collection_claim"
            paper["evidence_grade"] = "B"
            paper["quality_claim"] = (
                "the fixed repository path labels this item as an excellent paper"
            )
            paper["official_showcase_url"] = None
        paper["contest"] = "CUMCM / 全国大学生数学建模竞赛"
        paper["award"] = None
        paper["rights_status"] = (
            "link-and-metadata only; source repository has no declared license and "
            "underlying paper rights were not assumed"
        )

    papers.sort(key=lambda p: (p["year"], p["problem"] or "Z", p["title"]))
    for index, paper in enumerate(papers, 1):
        paper["id"] = f"CUMCM-REF-{index:04d}"

    by_year = Counter(str(p["year"]) for p in papers)
    by_problem = Counter(p["problem"] or "unknown" for p in papers)
    by_verification = Counter(p["verification_status"] for p in papers)
    return {
        "schema_version": "2.0",
        "generated_at": date.today().isoformat(),
        "scope": (
            "paper-level, link-only references for studying CUMCM modeling and "
            "paper-writing practice; not a mirrored training corpus"
        ),
        "primary_source": {
            "repository": PRIMARY_REPOSITORY,
            "url": GITHUB_REPOSITORY_URL,
            "commit": PRIMARY_COMMIT,
            "license": "NOASSERTION / no repository license detected",
        },
        "official_verification_sources": {
            "cumcm_entry": OFFICIAL_ENTRY,
            "china_education_online_showcase_index": OFFICIAL_SHOWCASE_INDEX,
            "annual_pages_read": annual_urls,
            "notice": (
                "Official showcase pages state that reproduction requires written "
                "permission; this catalog stores links and metadata only."
            ),
        },
        "selection_policy": {
            "included": (
                "unique PDF blobs inside paths labeled excellent/showcase/award paper, "
                "with a detected year and a minimum size of 90 KB"
            ),
            "excluded": (
                "problem statements, rules, attachments, source programs, result files, "
                "anthologies, reviews/commentaries, duplicate blobs and undersized files"
            ),
            "evidence_grades": {
                "S": "year and showcase code matched to an official display page",
                "B": "fixed repository path claims excellent-paper status; official item match pending",
            },
            "important_limit": (
                "Official showcase selection or an excellent-paper label is not the same "
                "as a specific national first-prize award. Award remains null unless "
                "independently verified."
            ),
        },
        "summary": {
            **diagnostics,
            "years": dict(sorted(by_year.items())),
            "problems": dict(sorted(by_problem.items())),
            "verification": dict(sorted(by_verification.items())),
        },
        "papers": papers,
    }


def write_outputs(catalog: dict) -> None:
    JSON_OUTPUT.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    fields = [
        "id",
        "year",
        "problem",
        "showcase_code",
        "title",
        "verification_status",
        "evidence_grade",
        "award",
        "authors",
        "doi",
        "bytes",
        "git_blob_sha1",
        "source_url",
        "official_showcase_url",
        "repository_path",
        "rights_status",
    ]
    with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(catalog["papers"])

    summary = catalog["summary"]
    year_rows = "\n".join(
        f"| {year} | {count} |" for year, count in summary["years"].items()
    )
    verified = summary["verification"].get("official_showcase_match", 0)
    repo_only = summary["verification"].get("repository_collection_claim", 0)
    report = f"""# CUMCM 高分/优秀论文参考目录（论文级索引）

生成日期：{catalog['generated_at']}

## 结论

本目录收录 **{len(catalog['papers'])} 篇**去重后的单篇论文级参考记录，超过 200 篇目标。它们来自固定到 commit `{PRIMARY_COMMIT}` 的 [GitHub 成熟整理库]({GITHUB_REPOSITORY_URL})。其中 **{verified} 篇**已用“年份 + 展示编号”匹配到中国大学生在线的官方论文展示，**{repo_only} 篇**目前仅由固定仓库的“优秀论文”目录或文件名支持，仍待逐项官方核验。

这里的“论文展示/优秀论文”不自动等同于“全国一等奖”。未取得官方奖项名单证据时，`award` 一律留空，避免把优秀论文候选夸大成国一论文。

## 来源与版权边界

- 赛事官网入口：[全国大学生数学建模竞赛历年论文展示]({OFFICIAL_ENTRY})。
- 权威展示索引：[中国大学生在线全国大学生数学建模竞赛论文展示]({OFFICIAL_SHOWCASE_INDEX})。
- GitHub 总库：[{PRIMARY_REPOSITORY}]({GITHUB_REPOSITORY_URL})，固定 commit `{PRIMARY_COMMIT}`。
- 总库未声明许可证；官方展示页还明确提示未经组委会书面许可不得转载。因此本项目只保存元数据、固定链接、Git blob 哈希与原创分析，不复制 PDF、正文、图片或附件。

## 清洗结果

- GitHub 递归树：{summary['github_tree_items']} 项。
- 原始 PDF：{summary['github_pdf_files']} 个。
- 清洗、去重后论文记录：{summary['accepted_unique_paper_records']} 篇。
- 证据等级 S（官方展示匹配）：{verified} 篇。
- 证据等级 B（仓库优秀论文标注）：{repo_only} 篇。

排除了赛题、规则、附件、程序、计算结果、整年合集、评述/评注、重复 blob 和小于 90 KB 的可疑文件。完整排除计数与每条记录见 `cumcm_high_score_papers_catalog.json`；Excel 友好的扁平表见 `cumcm_high_score_papers_catalog.csv`。

## 年份分布

| 年份 | 篇数 |
|---:|---:|
{year_rows}

## 使用方法

1. 先按 `problem`、`year` 与题型筛选；同题优先阅读 3–5 篇，不按篇数堆砌。
2. 只把 S 级用于“官方展示论文”的事实陈述；B 级只能称“整理库标注的优秀论文候选”。
3. 从结构、建模链、验证设计、图表语法和摘要压缩方式提炼原创方法卡，不复制原文或图表。
4. 若要声称“全国一等奖”，必须另行匹配组委会获奖名单；本目录没有把展示论文等价成某个奖级。

## 可复现

运行：

```powershell
python training/scripts/build_cumcm_reference_catalog.py
```

脚本重新读取固定 commit，并重建 JSON、CSV 和本报告；若上游官方网页暂时不可用，S 级匹配数会下降，脚本不会把未核验条目自动升级。
"""
    REPORT_OUTPUT.write_text(report, encoding="utf-8")


def main() -> int:
    catalog = build_catalog()
    write_outputs(catalog)
    count = len(catalog["papers"])
    if count < 200:
        raise RuntimeError(f"catalog has only {count} papers; target is at least 200")
    print(json.dumps(catalog["summary"], ensure_ascii=False, indent=2))
    print(JSON_OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
