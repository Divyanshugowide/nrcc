#!/usr/bin/env python3
"""
Prepare Fine-tuning Dataset for Arabic Q→Citation Pairs
Phase 10 - Next Sprint Hooks
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple
import random
from datetime import datetime

class FineTuningDatasetPreparer:
    """
    Prepare 60-120 Arabic Q→Citation pairs for fine-tuning
    """
    
    def __init__(self, chunks_path: str = "data/processed/chunks.jsonl"):
        self.chunks_path = chunks_path
        self.chunks = []
        self.question_templates = [
            "ما هو {concept}؟",
            "ما هي {concept}؟", 
            "كيف يتم {action}؟",
            "ما هي متطلبات {requirement}؟",
            "ما هو دور {entity} في {context}؟",
            "ما هي أحكام {legal_concept}؟",
            "كيف يتم تطبيق {procedure}؟",
            "ما هي شروط {condition}؟",
            "ما هو تعريف {term}؟",
            "ما هي إجراءات {process}؟"
        ]
        
        # Arabic legal and nuclear concepts
        self.concepts = [
            "المسؤولية المدنية", "الضرر النووي", "المشغل", "المنشأة النووية",
            "الوقود النووي", "المواد النووية", "المواد المشعة", "النفايات المشعة",
            "التعرض الإشعاعي", "الترخيص", "الرقابة النووية", "الهيئة",
            "الضمان المالي", "التعويض", "التقادم", "المطالبة",
            "اتفاقية فيينا", "الضمانات النووية", "الأمان النووي", "الأمن النووي"
        ]
        
        self.actions = [
            "تطبيق النظام", "إصدار الترخيص", "مراقبة المنشآت", "تقييم المخاطر",
            "إدارة النفايات", "حماية البيئة", "ضمان الأمان", "مراقبة الإشعاع",
            "تقييم الأضرار", "دفع التعويضات", "إجراء الفحوصات", "تطبيق الإجراءات"
        ]
        
        self.requirements = [
            "الترخيص", "الضمان المالي", "التدريب", "المؤهلات",
            "الفحوصات الطبية", "التأمين", "التوثيق", "التقارير",
            "المراقبة", "الامتثال", "التقييم", "المراجعة"
        ]
        
        self.entities = [
            "الهيئة", "المشغل", "الحكومة", "المحكمة", "الخبراء",
            "المقيمون", "المفتشون", "المستشارون", "المراقبون"
        ]
        
        self.contexts = [
            "الرقابة النووية", "إدارة النفايات", "حماية البيئة", "ضمان الأمان",
            "التعويض عن الأضرار", "إصدار التراخيص", "مراقبة المنشآت"
        ]
        
        self.legal_concepts = [
            "النظام", "اللائحة", "التعويض", "المسؤولية", "التقادم",
            "المطالبة", "الضمان", "الترخيص", "الرقابة", "العقوبة"
        ]
        
        self.procedures = [
            "إصدار الترخيص", "تقييم المخاطر", "مراقبة المنشآت", "إدارة النفايات",
            "تقييم الأضرار", "دفع التعويضات", "إجراء الفحوصات", "تطبيق الإجراءات"
        ]
        
        self.conditions = [
            "الترخيص", "الضمان المالي", "التدريب", "المؤهلات",
            "الفحوصات الطبية", "التأمين", "التوثيق", "التقارير"
        ]
        
        self.terms = [
            "المشغل", "المنشأة النووية", "الوقود النووي", "المواد النووية",
            "المواد المشعة", "النفايات المشعة", "التعرض الإشعاعي", "الترخيص",
            "الرقابة النووية", "الهيئة", "الضمان المالي", "التعويض"
        ]
        
        self.processes = [
            "إصدار الترخيص", "تقييم المخاطر", "مراقبة المنشآت", "إدارة النفايات",
            "تقييم الأضرار", "دفع التعويضات", "إجراء الفحوصات", "تطبيق الإجراءات"
        ]
    
    def load_chunks(self):
        """Load processed chunks"""
        print("Loading chunks...")
        with open(self.chunks_path, 'r', encoding='utf-8') as f:
            for line in f:
                chunk = json.loads(line)
                self.chunks.append(chunk)
        print(f"Loaded {len(self.chunks)} chunks")
    
    def generate_question(self, template: str, chunk: Dict[str, Any]) -> str:
        """Generate a question based on template and chunk content"""
        # Extract key terms from chunk
        text = chunk.get('text', '')
        doc_id = chunk.get('doc_id', '')
        article_no = chunk.get('article_no', '')
        
        # Simple keyword extraction
        keywords = self._extract_keywords(text)
        
        # Fill template based on type
        if "{concept}" in template:
            concept = random.choice(self.concepts)
            return template.format(concept=concept)
        elif "{action}" in template:
            action = random.choice(self.actions)
            return template.format(action=action)
        elif "{requirement}" in template:
            requirement = random.choice(self.requirements)
            return template.format(requirement=requirement)
        elif "{entity}" in template and "{context}" in template:
            entity = random.choice(self.entities)
            context = random.choice(self.contexts)
            return template.format(entity=entity, context=context)
        elif "{legal_concept}" in template:
            legal_concept = random.choice(self.legal_concepts)
            return template.format(legal_concept=legal_concept)
        elif "{procedure}" in template:
            procedure = random.choice(self.procedures)
            return template.format(procedure=procedure)
        elif "{condition}" in template:
            condition = random.choice(self.conditions)
            return template.format(condition=condition)
        elif "{term}" in template:
            term = random.choice(self.terms)
            return template.format(term=term)
        elif "{process}" in template:
            process = random.choice(self.processes)
            return template.format(process=process)
        else:
            return template
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - can be enhanced
        words = text.split()
        # Filter for Arabic words and common legal terms
        keywords = [word for word in words if len(word) > 3 and any(ord(c) >= 0x0600 for c in word)]
        return keywords[:10]  # Top 10 keywords
    
    def create_qa_pairs(self, num_pairs: int = 100) -> List[Dict[str, Any]]:
        """Create Q&A pairs for fine-tuning"""
        if not self.chunks:
            self.load_chunks()
        
        qa_pairs = []
        
        # Ensure we have enough chunks
        if len(self.chunks) < num_pairs:
            print(f"Warning: Only {len(self.chunks)} chunks available, creating {len(self.chunks)} pairs")
            num_pairs = len(self.chunks)
        
        # Select random chunks
        selected_chunks = random.sample(self.chunks, num_pairs)
        
        for i, chunk in enumerate(selected_chunks):
            # Generate question
            template = random.choice(self.question_templates)
            question = self.generate_question(template, chunk)
            
            # Create answer with citation
            answer = {
                "text": chunk.get('text', '')[:500],  # Truncate for readability
                "doc_id": chunk.get('doc_id', ''),
                "article_no": chunk.get('article_no', ''),
                "page_start": chunk.get('page_start', 0),
                "page_end": chunk.get('page_end', 0)
            }
            
            qa_pair = {
                "id": f"qa_{i+1:03d}",
                "question": question,
                "answer": answer,
                "metadata": {
                    "template_used": template,
                    "chunk_id": chunk.get('id', ''),
                    "created_at": datetime.now().isoformat()
                }
            }
            
            qa_pairs.append(qa_pair)
        
        return qa_pairs
    
    def save_dataset(self, qa_pairs: List[Dict[str, Any]], 
                    output_path: str = "data/finetuning_dataset.json"):
        """Save dataset to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
        
        print(f"Dataset saved to: {output_file}")
        print(f"Total Q&A pairs: {len(qa_pairs)}")
    
    def save_csv_format(self, qa_pairs: List[Dict[str, Any]], 
                        output_path: str = "data/finetuning_dataset.csv"):
        """Save dataset in CSV format for easy viewing"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'question', 'answer_text', 'doc_id', 'article_no', 'page_start', 'page_end'])
            
            for pair in qa_pairs:
                writer.writerow([
                    pair['id'],
                    pair['question'],
                    pair['answer']['text'],
                    pair['answer']['doc_id'],
                    pair['answer']['article_no'],
                    pair['answer']['page_start'],
                    pair['answer']['page_end']
                ])
        
        print(f"CSV dataset saved to: {output_file}")

def main():
    """Main function"""
    print("Preparing fine-tuning dataset...")
    
    # Initialize preparer
    preparer = FineTuningDatasetPreparer()
    
    # Create Q&A pairs (60-120 as requested)
    num_pairs = 100  # Middle of the range
    qa_pairs = preparer.create_qa_pairs(num_pairs)
    
    # Save in multiple formats
    preparer.save_dataset(qa_pairs, "data/finetuning_dataset.json")
    preparer.save_csv_format(qa_pairs, "data/finetuning_dataset.csv")
    
    # Print sample
    print("\nSample Q&A pairs:")
    for i, pair in enumerate(qa_pairs[:3]):
        print(f"\n{i+1}. Q: {pair['question']}")
        print(f"   A: {pair['answer']['text'][:100]}...")
        print(f"   Citation: {pair['answer']['doc_id']} - {pair['answer']['article_no']}")
    
    print(f"\nDataset preparation complete!")
    print(f"Total pairs created: {len(qa_pairs)}")
    print(f"Files created:")
    print(f"  - data/finetuning_dataset.json")
    print(f"  - data/finetuning_dataset.csv")

if __name__ == "__main__":
    main()
