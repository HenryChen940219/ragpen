import argparse
import os
from agents.pii_probe import run_pii_probe
from agents.credential_probe import run_credential_probe
from agents.indirect_pi_probe import run_indirect_pi_probe
from report_generator import generate_report, save_report

DEFAULT_TARGET = "http://localhost:8001/ask"
DEFAULT_PII_QUERIES = os.path.join("queries", "chinese_hr.json")
DEFAULT_CRED_QUERIES = os.path.join("queries", "credential_chinese.json")


def parse_args():
    parser = argparse.ArgumentParser(
        description="RAGPen - 自動化 RAG 應用安全測試框架"
    )
    parser.add_argument(
        "--target",
        default=DEFAULT_TARGET,
        help=f"目標 RAG API 的完整 URL（預設：{DEFAULT_TARGET}）"
    )
    parser.add_argument(
        "--question-field",
        default="question",
        help="目標 API 接收問題的 JSON 欄位名稱（預設：question）"
    )
    parser.add_argument(
        "--answer-field",
        default="answer",
        help="目標 API 回傳答案的 JSON 欄位名稱（預設：answer）"
    )
    parser.add_argument(
        "--pii-queries",
        default=DEFAULT_PII_QUERIES,
        help=f"PII 探測查詢集 JSON 路徑（預設：{DEFAULT_PII_QUERIES}）"
    )
    parser.add_argument(
        "--cred-queries",
        default=DEFAULT_CRED_QUERIES,
        help=f"憑證探測查詢集 JSON 路徑（預設：{DEFAULT_CRED_QUERIES}）"
    )
    parser.add_argument(
        "--skip-pii",
        action="store_true",
        help="略過 PII 個資洩漏探測"
    )
    parser.add_argument(
        "--skip-cred",
        action="store_true",
        help="略過系統憑證洩漏探測"
    )
    parser.add_argument(
        "--skip-ipi",
        action="store_true",
        help="略過間接 Prompt Injection 探測（目標需支援 /inject 端點）"
    )
    return parser.parse_args()


def run_full_assessment(
    target_url: str,
    question_field: str,
    answer_field: str,
    pii_queries_file: str,
    cred_queries_file: str,
    skip_pii: bool = False,
    skip_cred: bool = False,
    skip_ipi: bool = False
):
    print("\n" + "=" * 60)
    print("RAGPen 自動化 RAG 安全評估")
    print(f"目標系統：{target_url}")
    print("=" * 60)

    all_findings = []

    if not skip_pii:
        print("\n【階段 1】PII 個資洩漏探測")
        pii_findings = run_pii_probe(
            target_url=target_url,
            question_field=question_field,
            answer_field=answer_field,
            queries_file=pii_queries_file
        )
        all_findings.extend(pii_findings)
    else:
        print("\n【階段 1】略過（--skip-pii）")

    if not skip_cred:
        print("\n【階段 2】系統憑證洩漏探測")
        cred_findings = run_credential_probe(
            target_url=target_url,
            question_field=question_field,
            answer_field=answer_field,
            queries_file=cred_queries_file
        )
        all_findings.extend(cred_findings)
    else:
        print("\n【階段 2】略過（--skip-cred）")

    if not skip_ipi:
        print("\n【階段 3】間接 Prompt Injection 探測")
        ipi_findings = run_indirect_pi_probe(
            target_url=target_url,
            question_field=question_field,
            answer_field=answer_field
        )
        all_findings.extend(ipi_findings)
    else:
        print("\n【階段 3】略過（--skip-ipi）")

    print("\n【階段 4】生成安全報告")
    report = generate_report(all_findings, target_url)
    filename = save_report(report)

    total_vulns = sum(
        1 for f in all_findings
        if f["analysis"].get("has_vulnerability") or f["analysis"].get("injection_successful")
    )
    print(f"\n評估完成！共測試 {len(all_findings)} 個查詢，發現 {total_vulns} 個漏洞")
    print(f"報告已儲存：{filename}")


if __name__ == "__main__":
    args = parse_args()
    run_full_assessment(
        target_url=args.target,
        question_field=args.question_field,
        answer_field=args.answer_field,
        pii_queries_file=args.pii_queries,
        cred_queries_file=args.cred_queries,
        skip_pii=args.skip_pii,
        skip_cred=args.skip_cred,
        skip_ipi=args.skip_ipi
    )
