#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path

import markdown
import pymupdf
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "backedfund-security-audit-report.template.md"
ISSUES_PATH = ROOT / "issues-full.json"
COMMENTS_PATH = ROOT / "issue-comments.json"
OUT_MD = ROOT / "backedfund-security-audit-report.md"
OUT_HTML = ROOT / "backedfund-security-audit-report.html"
OUT_PDF = ROOT / "backedfund-security-audit-report.pdf"
OUT_JSON = ROOT / "backedfund-security-audit-report.json"
AUDITED_SHA = "07ea04fc6fb8c4156bed3cbb5d61c1f7ebc608a3"
REMEDIATION_SHA = "213a6dba2e2641804ed56555d4f6f763dbe95200"
CI_URL = "https://github.com/BuildTheTech/BackedFund-Contracts/actions/runs/38331787165"
REPO_URL = "https://github.com/BuildTheTech/BackedFund-Contracts"
REPORT_DATE = "13 October 2026"

issues = json.loads(ISSUES_PATH.read_text())
comments = json.loads(COMMENTS_PATH.read_text())
assert len(issues) == 28
issues_by_number = {int(i["number"]): i for i in issues}
assert len(issues_by_number) == 28


def first_paragraph(text: str) -> str:
    text = text.replace("\r", "").strip()
    paragraph = re.split(r"\n\s*\n", text, maxsplit=1)[0]
    paragraph = re.sub(r"\s+", " ", paragraph)
    paragraph = re.sub(r"^#+\s*", "", paragraph)
    if len(paragraph) > 850:
        paragraph = paragraph[:847].rstrip() + "…"
    return paragraph


def finding_meta(issue: dict) -> dict:
    number = int(issue["number"])
    match = re.match(r"\[([HML])-([0-9]{2})\]\s*(.*)", issue["title"])
    assert match, f"Missing finding ID in issue #{number}"
    letter, sequence, clean_title = match.groups()
    severity = {"H": "High", "M": "Medium", "L": "Low"}[letter]
    source_id = f"{letter}-{sequence}"
    if number == 14:
        status = "Mitigated / residual MEV acknowledged"
    elif number == 23:
        status = "Mitigated / bounded by fork replay"
    else:
        status = "Fixed in source"
    evidence = comments[str(number)]
    assert evidence, f"No remediation evidence for issue #{number}"
    latest = evidence[-1]
    evidence_summary = first_paragraph(latest.get("body") or "")
    return {
        "source_issue": number,
        "source_finding_id": source_id,
        "id": source_id,
        "title": clean_title,
        "severity": severity,
        "status": status,
        "issue_state": str(issue["state"]).lower(),
        "issue_url": issue["url"],
        "audited_sha": AUDITED_SHA,
        "remediation_sha": REMEDIATION_SHA,
        "issue_body_sha256": hashlib.sha256((issue.get("body") or "").encode()).hexdigest(),
        "latest_evidence": {
            "author": latest["user"]["login"],
            "created_at": latest["created_at"],
            "url": latest["html_url"],
            "summary": evidence_summary,
        },
        "evidence_comments": [
            {
                "author": c["user"]["login"],
                "created_at": c["created_at"],
                "url": c["html_url"],
                "body": c.get("body") or "",
            }
            for c in evidence
        ],
        "notes": (
            "Finding #14 is hardened in source; the source discussion explicitly acknowledges residual MEV and does not guarantee every sandwich is unprofitable."
            if number == 14
            else "Finding #23 is classified as mitigated because its Base-fork replay covered sampled scenarios and explicitly did not guarantee protection against every sandwich; ProtocolAuthority can widen the relevant setting."
            if number == 23
            else "Status reflects live source-remediation evidence in the issue ledger; it is not a deployment attestation."
        ),
    }


findings = [finding_meta(i) for i in issues]
severity_rank = {"High": 0, "Medium": 1, "Low": 2}
findings.sort(key=lambda f: (severity_rank[f["severity"]], int(f["id"].split("-")[1])))
assert Counter(f["severity"] for f in findings) == Counter({"Low": 16, "Medium": 9, "High": 3})
assert Counter(f["status"] for f in findings) == Counter({
    "Fixed in source": 26,
    "Mitigated / residual MEV acknowledged": 1,
    "Mitigated / bounded by fork replay": 1,
})
assert all(f["issue_state"] == "open" for f in findings)

front = f"""# BackedFund Security Audit Report

## Introduction

33Labs performed a focused security review of the **BackedFund** smart contracts. The review examined launch creation and lifecycle, contribution and refund paths, finalization, claims and vesting, fee routing, Uniswap V3/V4 integration, treasury and settlement flows, project-bond custody, pooled-yield accounting, project support, buy/burn execution, protocol authority, and emergency controls.

The review identified **28 findings**: **3 High**, **9 Medium**, and **16 Low**. At the remediation snapshot, 26 findings are classified as **Fixed in source** and two as **Mitigated** with explicit residual MEV limitations.

## Audit Team

| Auditor | Role |
|---|---|
| [0x23r0 ↗](https://github.com/0x23r0) | Security Researcher |
| [Favour Aniogor ↗](https://github.com/PhantomOz) | Security Researcher |

## Disclaimer

A smart contract security review cannot prove the complete absence of vulnerabilities. This assessment was bounded by the agreed scope, available documentation, GitHub issue ledger, and referenced repository snapshots. Additional review, deployment verification, monitoring, and a public bug bounty are recommended before production use. This report is not financial, legal, or investment advice.

## About 33Labs

33Labs is an independent smart contract security research and development group with six years of experience and over 40 completed audits. We specialize in building and auditing Solidity, Rust, Move, and DeFi systems. Learn more at [33labs.ai](https://33labs.ai) or follow us on X [@33labs_](https://x.com/33labs_).

## About BackedFund

BackedFund is a smart-contract system for permissionless launches, protocol-managed liquidity, treasury and project-bond flows, yield accounting, project support, and buy/burn execution. The reviewed repository integrates Base WETH/USDC, Uniswap V3/V4 components, DexFi/Bernard contracts, PLAZM, ESHARE, and approved Built-on-Asset tokens and routes.

## Audit Scope

- **Repository:** [BuildTheTech/BackedFund-Contracts]({REPO_URL})
- **Audited branch:** `main`
- **Original audited commit:** [`{AUDITED_SHA}`]({REPO_URL}/commit/{AUDITED_SHA})
- **Audited snapshot date:** September 16, 2026
- **Scope authority:** `docs/AUDIT_SCOPE.md` at the audited snapshot
- **In scope:** launch creation and lifecycle; contribution, finalization, refund, claim, and vesting paths; success-fee routing and affiliate ETH custody; V4 hook and pool creation; locked LP positions and fee custody; Standard, Bond Treasury, Built-on-Plazm, and Built-on-Asset settlement; project-bond custody and pooled-yield accounting; project support and buy/burn; `ProtocolAuthority`; and emergency-pause surfaces
- **Out of deployable production scope:** mocks under `contracts/mocks` and ABI/type declarations under `contracts/interfaces`, while still reviewed when relevant to tests and integration assumptions

## Remediation Review

- **Reviewed branch:** `main`
- **Remediation snapshot:** [`{REMEDIATION_SHA}`]({REPO_URL}/commit/{REMEDIATION_SHA})
- **Report date:** {REPORT_DATE}
- **Principal remediation commits:** [`eeb556e`]({REPO_URL}/commit/eeb556e9584ef6ba658595da9bc136286f5fe473) and [`c03961a`]({REPO_URL}/commit/c03961aaca1dc6b118710e031bd5b56c12460622)
- **Execution evidence:** [Contracts CI run 38331787165]({CI_URL}) on the remediation snapshot. Unit tests passed. Exact production coverage failed with exit code 134 after a Node.js heap out-of-memory error; deployment replay and fork jobs were skipped
- **Status method:** issue bodies supplied the vulnerability analysis; issue comments, referenced commits, and CI supplied remediation evidence. Open/closed issue state was not used as a substitute for technical disposition

“Fixed in source” means that source-level remediation evidence was available; it does not attest that a change is deployed. All 28 GitHub issues remained administratively open when this report was generated.

## Methodology

The audit combined manual adversarial review, invariant analysis, code-path tracing, executable proof-of-concept tests, and review of remediation comments and regression evidence. Each finding retains its source issue link and original severity. Remediation status is scoped to source evidence and the explicitly observed CI result.

## Severity Classification

- **High:** exploitation can cause major loss, permanent protocol failure, or a critical integrity violation under realistic conditions.
- **Medium:** exploitation can cause material loss, denial of service, or invariant failure but requires stronger preconditions or has a narrower blast radius.
- **Low:** limited-impact, edge-case, hardening, or liveness issue that should still be corrected or explicitly accepted.

"""

md = TEMPLATE.read_text()
start = md.index("## Findings Summary")
md = front + md[start:]
assert md.count("| | |\n|---|---|") == 28
md = md.replace("| | |\n|---|---|", "| Attribute | Value |\n|---|---|")

# Match the Recoup summary convention: retain a separate source column so the
# summary is traceable without relying only on linked finding titles.
summary_start = md.index("## Findings Summary")
summary_end = md.index("\n## ", summary_start + 3)
summary = md[summary_start:summary_end]
summary = summary.replace(
    "| ID | Severity | Title | Status |\n|---|---|---|---|",
    "| ID | Finding | Severity | Status | Source |\n|---|---|---|---|---|",
)
summary = re.sub(
    r"^\| (#\d+) \| (High|Medium|Low) \| (.*?) \| (Fixed|Mitigated) \|$",
    lambda m: f"| {m.group(1)} | {m.group(3)} | {m.group(2)} | {m.group(4)} | [Issue {m.group(1)}]({REPO_URL}/issues/{m.group(1)[1:]}) |",
    summary,
    flags=re.M,
)
md = md[:summary_start] + summary + md[summary_end:]

# Correct the summary table and detailed status labels.
md = re.sub(r"(\| #14 \| .*? \| Low \| .*?\| )Fixed( \|)", r"\1Mitigated\2", md)
md = re.sub(r"(\| #23 \| .*? \| Low \| .*?\| )Fixed( \|)", r"\1Mitigated\2", md)

by_number = {f["source_issue"]: f for f in findings}
sections = re.split(r"(?=^### \[[HML]-\d{2}\] )", md, flags=re.M)
prefix, detail_sections = sections[0], sections[1:]
assert len(detail_sections) == 28
rebuilt = [prefix]
for section in detail_sections:
    issue_match = re.search(r"GitHub issue:\*\* \[#(\d+)\]", section)
    assert issue_match, section[:200]
    number = int(issue_match.group(1))
    f = by_number[number]
    section = re.sub(
        r"\*\*Status:\*\* Fixed \(client-confirmed\)",
        f"**Status:** {f['status']}",
        section,
        count=1,
    )
    latest = f["latest_evidence"]
    date = latest["created_at"][:10]
    status_block = (
        "**Status**\n\n"
        f"**{f['status']}.** Latest source evidence: [{latest['author']} on {date}]({latest['url']}) — "
        f"{latest['summary']}\n\n"
        f"The disposition was evaluated against remediation snapshot `{REMEDIATION_SHA}`. The exact-head unit-test stage passed in "
        f"[Contracts CI]({CI_URL}), while the coverage stage failed from Node.js heap exhaustion and the fork/deployment-replay jobs were skipped. "
        "This status is a source-remediation assessment, not a deployment attestation or a claim of clean full CI."
    )
    section, count = re.subn(
        r"\*\*Status\*\*\n\nThe client has confirmed that this finding has been fixed\. Independent commit-level and regression-test evidence was not available in the current GitHub repository state\.",
        status_block,
        section,
        count=1,
    )
    assert count == 1, f"Could not replace status block for #{number}"
    rebuilt.append(section)
md = "".join(rebuilt).rstrip() + "\n\n## Conclusion\n\nThe audit recorded 28 findings: 3 High, 9 Medium, and 16 Low. At remediation snapshot `" + REMEDIATION_SHA + "`, 26 findings are Fixed in source and 2 are Mitigated with explicit residual MEV limitations. No finding is represented as deployed solely from repository evidence.\n\nBefore production release, the team should rerun the exact production-coverage gate with sufficient Node.js heap, execute the skipped fork and deployment-replay jobs, confirm production addresses and role assignments, and close or otherwise reconcile the GitHub issues with their final dispositions.\n"

assert "client-confirmed" not in md
assert "client confirmation" not in md.lower()
assert md.count("**Status:**") == 28
assert md.count("**Status**\n") == 28
assert len(re.findall(r"^### \[[HML]-\d{2}\]", md, flags=re.M)) == 28
for f in findings:
    assert f["issue_url"] in md
OUT_MD.write_text(md)

structured = {
    "report": {
        "title": "BackedFund Security Audit Report",
        "organization": "33Labs",
        "report_date": "2026-10-13",
        "repository": REPO_URL,
        "branch": "main",
        "audited_sha": AUDITED_SHA,
        "remediation_sha": REMEDIATION_SHA,
        "ci": {
            "url": CI_URL,
            "conclusion": "failure",
            "passed_stages": ["compile", "release-consistency", "size", "dead-code", "typecheck", "unit-tests"],
            "failed_stage": "exact production coverage",
            "failure_reason": "Node.js heap out of memory; exit code 134",
            "skipped_stages": ["deployment replay", "base-plazm-fork", "base-protocol-e2e"],
        },
        "totals": {
            "findings": 28,
            "severity": {"High": 3, "Medium": 9, "Low": 16},
            "disposition": {"Fixed in source": 26, "Mitigated": 2},
            "open_github_issues": 28,
        },
        "authors": [
            {
                "name": "0x23r0",
                "role": "Security Researcher",
                "url": "https://github.com/0x23r0",
            },
            {
                "name": "Favour Aniogor",
                "role": "Security Researcher",
                "url": "https://github.com/PhantomOz",
            },
        ],
    },
    "findings": findings,
}
OUT_JSON.write_text(json.dumps(structured, indent=2, ensure_ascii=False) + "\n")

body = markdown.markdown(md, extensions=["fenced_code", "tables", "toc", "sane_lists"])
css = r"""
@page { size: Letter; margin: .72in .65in .68in; @bottom-center { content: "33Labs • BackedFund Security Audit"; color:#7b8794; font-size:8px; } @bottom-right { content: counter(page); color:#7b8794; font-size:8px; } }
@page cover { margin:0; @bottom-center { content:none } @bottom-right { content:none } }
* { box-sizing:border-box; }
body { margin:0; font-family: Inter, Arial, sans-serif; color:#172033; font-size:9.2pt; line-height:1.46; }
.cover { page:cover; page-break-after:always; height:10.98in; width:8.5in; margin:0; padding:.9in; background:linear-gradient(145deg,#08172b 0%,#153558 58%,#0a7a97 100%); color:white; position:relative; overflow:hidden; }
.cover:before { content:""; position:absolute; left:-1.6in; bottom:-2.2in; width:5.8in; height:5.8in; border:1px solid rgba(119,226,230,.25); transform:rotate(32deg); box-shadow:0 0 0 .45in rgba(119,226,230,.035),0 0 0 .9in rgba(119,226,230,.025); }
.cover:after { content:""; position:absolute; width:5.3in; height:5.3in; border:1px solid rgba(103,210,242,.34); border-radius:50%; right:-1.9in; top:-1.45in; box-shadow:0 0 0 .48in rgba(103,210,242,.05),0 0 0 .96in rgba(103,210,242,.035); }
.brand { font-size:18pt; font-weight:800; letter-spacing:.03em; }
.cover-main { margin-top:2.05in; max-width:6.3in; position:relative; z-index:2; }
.kicker { text-transform:uppercase; letter-spacing:.18em; color:#9be8ef; font-size:10pt; font-weight:700; }
.cover h1 { font-size:39pt; line-height:1.02; margin:.25in 0 .18in; color:white; border:0; page-break-before:auto; }
.cover h2 { font-size:18pt; color:#c8f2f4; margin:0; font-weight:500; }
.cover-meta { position:absolute; left:.9in; bottom:1.05in; z-index:2; font-size:11pt; color:#daf3f5; }
h1 { color:#0c2f55; font-size:23pt; page-break-before:always; border-bottom:3px solid #1aa6b7; padding-bottom:8px; }
h2 { color:#0d426f; font-size:15pt; margin-top:24px; page-break-after:avoid; }
h3 { color:#0f6a7f; font-size:11.5pt; margin-top:18px; page-break-after:avoid; }
h4 { color:#274c67; font-size:10pt; page-break-after:avoid; }
a { color:#145fc0; text-decoration:underline; }
table { width:100%; border-collapse:collapse; margin:12px 0 18px; font-size:8.15pt; }
thead { display:table-header-group; }
tr { break-inside:avoid; page-break-inside:avoid; }
th { background:#e5e7eb; color:#1f2937; padding:7px; text-align:left; border:1px solid #cbd5e1; }
td { padding:7px; border:1px solid #d8e0e8; vertical-align:top; }
tr:nth-child(even) td { background:#f8fafc; }
#findings-summary + table { width:100%; table-layout:fixed; font-size:7.5pt; }
#findings-summary + table th:nth-child(1), #findings-summary + table td:nth-child(1) { width: 7%; white-space: nowrap; overflow-wrap: normal; }
#findings-summary + table th:nth-child(2), #findings-summary + table td:nth-child(2) { width: 51%; }
#findings-summary + table th:nth-child(3), #findings-summary + table td:nth-child(3) { width: 10%; white-space: nowrap; overflow-wrap: normal; }
#findings-summary + table th:nth-child(4), #findings-summary + table td:nth-child(4) { width: 15%; }
#findings-summary + table th:nth-child(5), #findings-summary + table td:nth-child(5) { width: 17%; white-space: nowrap; overflow-wrap: normal; }
pre { background:#0b1627; color:#e5edf8; border-radius:6px; padding:10px; font-size:7.1pt; line-height:1.34; white-space:pre-wrap; overflow-wrap:anywhere; break-inside:auto; box-decoration-break:clone; }
code { font-family:"DejaVu Sans Mono",monospace; font-size:.88em; }
p code, li code { background:#eef3f7; color:#17324b; padding:1px 3px; border-radius:3px; }
blockquote { border-left:3px solid #1aa6b7; margin-left:0; padding-left:12px; color:#42566a; }
hr { border:0; border-top:1px solid #cbd5e1; margin:22px 0; }
"""
cover = '''<section class="cover"><div class="brand">33Labs</div><div class="cover-main"><div class="kicker">Smart Contract Security Review</div><h1>BackedFund</h1><h2>Security Audit Report</h2></div><div class="cover-meta">Audited snapshot: September 16, 2026<br>Report date: October 13, 2026<br><br>33labs.ai</div></section>'''
html_doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>BackedFund Security Audit Report</title><style>{css}</style></head><body>{cover}{body}</body></html>"""
OUT_HTML.write_text(html_doc)
HTML(string=html_doc, base_url=str(ROOT)).write_pdf(OUT_PDF)

# Replace the synthetic first page with the established 33Labs report-family cover.
cover_path = ROOT / "assets" / "backedfund-cover.pdf"
generated = pymupdf.open(OUT_PDF)
approved_cover = pymupdf.open(cover_path)
merged = pymupdf.open()
merged.insert_pdf(approved_cover, from_page=0, to_page=0, links=True, annots=True)
merged.insert_pdf(generated, from_page=1, to_page=generated.page_count - 1, links=True, annots=True)
merged.set_metadata({
    **generated.metadata,
    "title": "BackedFund Security Audit Report",
    "author": "0x23r0; Favour Aniogor; 33Labs",
    "subject": "Smart contract security review",
})
tmp_pdf = ROOT / "backedfund-security-audit-report.merged.pdf"
merged.save(tmp_pdf, garbage=4, deflate=True)
merged.close()
approved_cover.close()
generated.close()
tmp_pdf.replace(OUT_PDF)

# Semantic and annotation verification.
doc = pymupdf.open(OUT_PDF)
pdf_text = "\n".join(page.get_text() for page in doc)
pdf_links = {link.get("uri") for page in doc for link in page.get_links() if link.get("uri")}
assert doc[0].rect == pymupdf.Rect(0, 0, 612, 842.25)
assert doc[0].get_text().strip().splitlines() == ["BackedFund", "Security Audit Report"]
assert all(doc[i].rect == pymupdf.Rect(0, 0, 612, 792) for i in range(1, doc.page_count))
assert "BackedFund Security Audit Report" in pdf_text[:5000]
assert "V3 capacity guards stop at the next initialized tick" in pdf_text
assert "Conclusion" in pdf_text
assert AUDITED_SHA in pdf_text
assert REMEDIATION_SHA in pdf_text
assert "26 findings are Fixed in source" in pdf_text
assert "0x23r0" in pdf_text
assert "Favour Aniogor" in pdf_text
assert re.search(r"over\s+40\s+completed audits", pdf_text)
for uri in ["https://github.com/0x23r0", "https://github.com/PhantomOz", "https://33labs.ai", "https://x.com/33labs_"]:
    assert uri in pdf_links, f"Missing PDF link annotation: {uri}"
missing_links = [f["issue_url"] for f in findings if f["issue_url"] not in pdf_links]
assert not missing_links, f"Missing issue link annotations: {missing_links}"
assert doc.page_count > 20

manifest = {}
for path in [OUT_MD, OUT_HTML, OUT_PDF, OUT_JSON]:
    payload = path.read_bytes()
    manifest[path.name] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
(ROOT / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"pages": doc.page_count, "links": len(pdf_links), "artifacts": manifest}, indent=2))
