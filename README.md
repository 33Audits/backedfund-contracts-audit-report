# BackedFund Contracts Security Audit Report

Client-facing security audit report for [`BuildTheTech/BackedFund-Contracts`](https://github.com/BuildTheTech/BackedFund-Contracts), assembled from the repository's audit finding issues and remediation evidence.

## Report

- [Final PDF](reports/backedfund-security-audit-report.pdf)
- [Markdown source](reports/backedfund-security-audit-report.md)
- [Structured findings JSON](reports/backedfund-security-audit-report.json)
- [HTML render source](reports/backedfund-security-audit-report.html)
- [Report generator and reproducibility sources](sources/)

## Scope

- **Audited repository:** `BuildTheTech/BackedFund-Contracts`
- **Audited branch:** `main`
- **Original audited commit:** [`07ea04fc6fb8c4156bed3cbb5d61c1f7ebc608a3`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/07ea04fc6fb8c4156bed3cbb5d61c1f7ebc608a3)
- **Remediation snapshot:** [`213a6dba2e2641804ed56555d4f6f763dbe95200`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/213a6dba2e2641804ed56555d4f6f763dbe95200)
- **Report date:** October 13, 2026

## Audit Team

- [0x23r0](https://github.com/0x23r0) — Security Researcher
- [Favour Aniogor](https://github.com/PhantomOz) — Security Researcher

## Document Format

The report uses the established Recoup/33Labs report-family implementation: the original cover background and logo assets, embedded Darker Grotesque cover font, exact cover coordinates, a 612 × 842.25 point cover, US Letter body pages, and the same body typography, heading, table, footer, and spacing rules.

## Findings Summary

- **High:** 3
- **Medium:** 9
- **Low:** 16
- **Total:** 28

Twenty-six findings are fixed in source. Two low-severity findings are mitigated with explicit residual MEV limitations. All 28 source issues remained administratively open when the report was generated; issue state is recorded separately from the technical remediation disposition.

## Verification Notes

The exact remediation-snapshot CI run passed compilation, release-consistency, size, dead-code, type-check, and unit tests. Exact production coverage terminated due to a Node.js heap out-of-memory error, and the fork/deployment-replay jobs were skipped. The report does not claim a clean full CI run or independently verified deployment state.

## Checksums (SHA-256)

```text
408746cec4306d102e76fcd2f248d3b0a4f330345b5b1d7fa65805b460ee3963  backedfund-security-audit-report.pdf
b7ca665694d4052a3e4f17769088927fe57b45d0f1e3ecfa6112003f5494406c  backedfund-security-audit-report.md
c1fcc241c1bb13c994242a7750c54031f4f5ef5776829529e10875c8201818c9  backedfund-security-audit-report.json
f968633c4397e0deb0ffd548f23d69f735550cb24bde6e0f5abf97e67135f793  backedfund-security-audit-report.html
```
