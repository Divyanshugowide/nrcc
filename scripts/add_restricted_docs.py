#!/usr/bin/env python3
"""
Script to add test restricted documents to demonstrate RBAC functionality
"""
import json
import os
from pathlib import Path

def add_restricted_documents():
    """Add some test documents with 'restricted' in their names"""
    
    # Read existing chunks
    chunks_file = "data/processed/chunks.jsonl"
    meta_file = "data/idx/meta.json"
    
    if not os.path.exists(chunks_file):
        print(f"Chunks file {chunks_file} not found. Please run the pipeline first.")
        return
    
    # Read existing chunks
    chunks = []
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line.strip()))
    
    # Add some restricted test documents
    restricted_docs = [
        {
            "id": "Restricted Nuclear Safety Protocol::art1",
            "doc_id": "Restricted Nuclear Safety Protocol",
            "article_no": "1",
            "pages": [1],
            "text": "المادة الأولى - بروتوكول الأمان النووي المقيد\nهذا المستند يحتوي على معلومات حساسة حول بروتوكولات الأمان النووي المتقدمة. هذه المعلومات مقيدة للوصول من قبل المستشارين القانونيين ومديري النظام فقط.\n\nتشمل هذه البروتوكولات:\n- إجراءات الطوارئ المتقدمة\n- معايير الأمان السرية\n- بروتوكولات التفتيش الداخلية",
            "norm_text": "المادة الاولي - بروتوكول الامان النووي المقيد\nهذا المستند يحتوي علي معلومات حساسة حول بروتوكولات الامان النووي المتقدمة. هذه المعلومات مقيدة للوصول من قبل المستشارين القانونيين ومديري النظام فقط.\n\nتشمل هذه البروتوكولات:\n- اجراءات الطوارئ المتقدمة\n- معايير الامان السرية\n- بروتوكولات التفتيش الداخلية",
            "roles": ["legal", "admin"],  # Only legal and admin can access
            "tokens": ["المادة", "الاولي", "بروتوكول", "الامان", "النووي", "المقيد", "مستند", "يحتوي", "معلومات", "حساسة", "حول", "بروتوكولات", "متقدمة", "هذه", "مقيدة", "الوصول", "المستشارين", "القانونيين", "مديري", "النظام", "فقط", "تشمل", "اجراءات", "الطوارئ", "معايير", "السرية", "التفتيش", "الداخلية"]
        },
        {
            "id": "Confidential Restricted Nuclear Waste Management::art1", 
            "doc_id": "Confidential Restricted Nuclear Waste Management",
            "article_no": "1",
            "pages": [1],
            "text": "المادة الأولى - إدارة النفايات النووية المقيدة السري\nهذا المستند سري ومقيد ويحتوي على معلومات حساسة حول إدارة النفايات النووية عالية الخطورة. الوصول مقيد للمستشارين القانونيين ومديري النظام فقط.\n\nالمحتويات تشمل:\n- مواقع التخزين السرية\n- بروتوكولات النقل المحمية\n- إجراءات التخلص الآمن",
            "norm_text": "المادة الاولي - ادارة النفايات النووية المقيدة السري\nهذا المستند سري ومقيد ويحتوي علي معلومات حساسة حول ادارة النفايات النووية عالية الخطورة. الوصول مقيد للمستشارين القانونيين ومديري النظام فقط.\n\nالمحتويات تشمل:\n- مواقع التخزين السرية\n- بروتوكولات النقل المحمية\n- اجراءات التخلص الامن",
            "roles": ["legal", "admin"],  # Only legal and admin can access
            "tokens": ["المادة", "الاولي", "ادارة", "النفايات", "النووية", "المقيدة", "السري", "مستند", "سري", "مقيد", "يحتوي", "معلومات", "حساسة", "حول", "عالية", "الخطورة", "الوصول", "مقيد", "المستشارين", "القانونيين", "مديري", "النظام", "فقط", "المحتويات", "تشمل", "مواقع", "التخزين", "السرية", "بروتوكولات", "النقل", "المحمية", "اجراءات", "التخلص", "الامن"]
        },
        {
            "id": "Public Nuclear Energy Policy::art1",
            "doc_id": "Public Nuclear Energy Policy", 
            "article_no": "1",
            "pages": [1],
            "text": "المادة الأولى - السياسة العامة للطاقة النووية\nهذا المستند عام ومتاح لجميع المستخدمين. يحتوي على معلومات عامة حول سياسة الطاقة النووية في المملكة.\n\nتشمل السياسة:\n- الأهداف العامة للطاقة النووية\n- المعايير العامة للأمان\n- الإطار التنظيمي العام",
            "norm_text": "المادة الاولي - السياسة العامة للطاقة النووية\nهذا المستند عام ومتاح لجميع المستخدمين. يحتوي علي معلومات عامة حول سياسة الطاقة النووية في المملكة.\n\nتشمل السياسة:\n- الاهداف العامة للطاقة النووية\n- المعايير العامة للامان\n- الاطار التنظيمي العام",
            "roles": ["staff", "legal", "admin"],  # All roles can access
            "tokens": ["المادة", "الاولي", "السياسة", "العامة", "للطاقة", "النووية", "مستند", "عام", "ومتاح", "لجميع", "المستخدمين", "يحتوي", "معلومات", "عامة", "حول", "في", "المملكة", "تشمل", "الاهداف", "المعايير", "للامان", "الاطار", "التنظيمي"]
        }
    ]
    
    # Add restricted documents to chunks
    chunks.extend(restricted_docs)
    
    # Write updated chunks
    with open(chunks_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
    
    print(f"Added {len(restricted_docs)} test documents to {chunks_file}")
    
    # Update meta.json if it exists
    if os.path.exists(meta_file):
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # Add metadata for restricted documents
        for doc in restricted_docs:
            meta.append({
                "id": doc["id"],
                "doc_id": doc["doc_id"],
                "article_no": doc["article_no"],
                "pages": doc["pages"],
                "text": doc["text"],
                "norm_text": doc["norm_text"],
                "roles": doc["roles"],
                "tokens": doc["tokens"]
            })
        
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        print(f"Updated {meta_file} with restricted document metadata")
    
    print("\nTest documents added:")
    print("1. Restricted Nuclear Safety Protocol (legal, admin only)")
    print("2. Confidential Restricted Nuclear Waste Management (legal, admin only)")  
    print("3. Public Nuclear Energy Policy (all roles)")
    print("\nYou can now test the RBAC system by:")
    print("- Logging in as 'staff' - should only see public documents")
    print("- Logging in as 'legal' - should see all documents including restricted ones")
    print("- Logging in as 'admin' - should see all documents")

if __name__ == "__main__":
    add_restricted_documents()
