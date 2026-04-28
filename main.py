from agents.pii_probe import run_pii_probe
from report_generator import generate_report, save_report

def run_full_assessment():
    print("\nRAGPen 安全評估開始\n")

    print("【階段 1】PII 洩漏探測")
    findings = run_pii_probe()

    print("\n【階段 2】生成安全報告")
    report = generate_report(findings, "http://localhost:8001")
    save_report(report)

    print("\n評估完成！查看生成的 security_report_XXXX.md 檔案")

if __name__ == "__main__":
    run_full_assessment()
