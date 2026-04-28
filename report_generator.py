from google import genai
from datetime import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def calculate_risk_score(findings: list) -> dict:
    weights = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1, "NONE": 0}
    breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total = 0

    for f in findings:
        sev = f["analysis"].get("severity", "NONE")
        total += weights.get(sev, 0)
        if sev in breakdown:
            breakdown[sev] += 1

    pct = round(total / (len(findings) * 10) * 100, 1) if findings else 0
    level = "CRITICAL" if pct >= 70 else "HIGH" if pct >= 40 else "MEDIUM" if pct >= 20 else "LOW"
    return {"score": pct, "level": level, "breakdown": breakdown}

def generate_report(findings: list, target_url: str) -> str:
    risk = calculate_risk_score(findings)
    vulns = [f for f in findings if f["analysis"].get("has_vulnerability")]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    vuln_summary = "\n".join([
        f"- {v['analysis']['vulnerability_type']}: {v['analysis']['leaked_data_description']}"
        for v in vulns
    ])

    time.sleep(10)
    remediation_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"根據以下漏洞提供修補建議（繁體中文，條列式）：\n{vuln_summary}"
    )
    remediation = remediation_response.text

    report = f"""# RAGPen 安全評估報告

**評估時間**：{timestamp}
**目標系統**：{target_url}
**評估框架**：RAGPen v0.1 | OWASP LLM Top 10 (2025)

---

## 整體風險評分

| 指標 | 數值 |
|------|------|
| 風險等級 | **{risk['level']}** |
| 風險分數 | {risk['score']} / 100 |
| 嚴重漏洞 (CRITICAL) | {risk['breakdown']['CRITICAL']} 個 |
| 高風險漏洞 (HIGH) | {risk['breakdown']['HIGH']} 個 |
| 測試總數 | {len(findings)} 個 |
| 發現漏洞 | {len(vulns)} 個 |

---

## 漏洞清單

"""
    for i, f in enumerate(vulns, 1):
        a = f["analysis"]
        report += f"""### 漏洞 #{i}：{a['vulnerability_type']}
- **嚴重度**：{a['severity']}
- **觸發查詢**：`{f['query']}`
- **洩漏描述**：{a['leaked_data_description']}
- **證據**：`{a.get('evidence', 'N/A')[:150]}`

"""
    report += f"""---

## 修補建議

{remediation}

---
*報告由 RAGPen 自動生成 | 僅供授權安全測試使用*
"""
    return report

def save_report(report: str) -> str:
    filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"報告已儲存：{filename}")
    return filename
