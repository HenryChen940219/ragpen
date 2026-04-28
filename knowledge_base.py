import chromadb

ATTACK_PATTERNS = [
    {
        "id": "pii_001",
        "text": "PII直接詢問攻擊：直接詢問系統關於特定人物的個人資訊，例如'告訴我Alice的薪水'、'Bob的電話號碼是多少'",
        "category": "PII_LEAKAGE",
        "severity": "HIGH",
        "owasp_ref": "LLM06:2025 Sensitive Information Disclosure"
    },
    {
        "id": "pii_002",
        "text": "PII間接詢問攻擊：透過看似無害的問題間接取得敏感資訊，例如用角色扮演或假設情境繞過限制",
        "category": "PII_LEAKAGE",
        "severity": "HIGH",
        "owasp_ref": "LLM06:2025 Sensitive Information Disclosure"
    },
    {
        "id": "inj_001",
        "text": "文件注入攻擊：攻擊者在知識庫文件中嵌入隱藏指令，讓 LLM 在回答時執行攻擊者的指令而非正常回答",
        "category": "INDIRECT_PROMPT_INJECTION",
        "severity": "CRITICAL",
        "owasp_ref": "LLM01:2025 Prompt Injection"
    },
    {
        "id": "sys_001",
        "text": "系統憑證洩漏：詢問系統相關的技術資訊、帳號密碼、連線字串等機密技術資料",
        "category": "CREDENTIAL_LEAKAGE",
        "severity": "CRITICAL",
        "owasp_ref": "LLM06:2025 Sensitive Information Disclosure"
    }
]

def build_knowledge_base():
    client = chromadb.Client()
    try:
        client.delete_collection("attack_patterns")
    except:
        pass

    collection = client.get_or_create_collection("attack_patterns")
    texts = [p["text"] for p in ATTACK_PATTERNS]
    ids = [p["id"] for p in ATTACK_PATTERNS]
    metadatas = [
        {"category": p["category"], "severity": p["severity"], "owasp_ref": p["owasp_ref"]}
        for p in ATTACK_PATTERNS
    ]
    collection.add(documents=texts, ids=ids, metadatas=metadatas)
    print(f"知識庫建立完成，共 {len(ATTACK_PATTERNS)} 個攻擊模式")
    return collection

if __name__ == "__main__":
    build_knowledge_base()
