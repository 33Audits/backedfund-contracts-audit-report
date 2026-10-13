# BackedFund Contracts Security Audit Report

Client-facing security audit report for [`BuildTheTech/BackedFund-Contracts`](https://github.com/BuildTheTech/BackedFund-Contracts), assembled from the repository's audit finding issues and remediation evidence.

## Report

- [Final PDF](reports/backedfund-security-audit-report.pdf)
- [Markdown source](reports/backedfund-security-audit-report.md)
- [Structured findings JSON](reports/backedfund-security-audit-report.json)

## Scope

- **Audited repository:** `BuildTheTech/BackedFund-Contracts`
- **Audited branch:** `main`
- **Original audited commit:** [`07ea04fc6fb8c4156bed3cbb5d61c1f7ebc608a3`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/07ea04fc6fb8c4156bed3cbb5d61c1f7ebc608a3)
- **Remediation snapshot:** [`213a6dba2e2641804ed56555d4f6f763dbe95200`](https://github.com/BuildTheTech/BackedFund-Contracts/commit/213a6dba2e2641804ed56555d4f6f763dbe95200)
- **Report date:** October 13, 2026

## Audit Team

- [Favour Aniogor](https://github.com/PhantomOz) — Security Researcher

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
625ce5fce309f703c5557a3a8fcad9a630c8224d4bcf82cd71db0121a44964f6  backedfund-security-audit-report.pdf
8c2bb8de07220d8c522f3b3bdaf5c69a31c359b7e77b56e66096f32cb64e475d  backedfund-security-audit-report.md
f3bc07aedd137db43bee1ce3521ceee16a787688994e31fd044049c7be89e1a6  backedfund-security-audit-report.json
```
