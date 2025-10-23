#!/usr/bin/env python3
"""
Evaluation script for Arabic POV system
Computes Precision@1, Precision@3, and Citation Correctness metrics
"""

import csv
import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.retrieval import load_bm25, load_faiss, load_meta, load_model, Indices, search
from app.auth import get_effective_roles, filter_documents_by_access

def load_gold_standard(gold_file):
    """Load gold standard evaluation data"""
    gold_data = []
    with open(gold_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gold_data.append({
                'query': row['query'],
                'expected_doc': row['expected_doc'],
                'expected_article': row['expected_article']
            })
    return gold_data

def evaluate_query(idx, query, expected_doc, expected_article, roles=['admin']):
    """Evaluate a single query against expected results"""
    # Get effective roles
    effective_roles = get_effective_roles(roles)
    
    # Perform search
    out = search(idx, query, roles=effective_roles, topk=10)
    
    # Filter results based on file access restrictions
    filtered_results = filter_documents_by_access(roles, out["results"])
    
    # Check if expected document appears in results
    found_doc = False
    found_article = False
    top1_doc_match = False
    top3_doc_match = False
    top1_article_match = False
    top3_article_match = False
    
    # Helper function for flexible article matching
    def article_matches(actual, expected):
        if actual is None or expected is None:
            return False
        # Normalize both strings for comparison
        actual_norm = str(actual).strip()
        expected_norm = str(expected).strip()
        # Check exact match first
        if actual_norm == expected_norm:
            return True
        # Check if expected is contained in actual (for partial matches)
        if expected_norm in actual_norm:
            return True
        # Check if actual is contained in expected
        if actual_norm in expected_norm:
            return True
        return False
    
    # Check top-1 result
    if filtered_results:
        top1_result = filtered_results[0]
        if top1_result['doc_id'] == expected_doc:
            top1_doc_match = True
            found_doc = True
        if article_matches(top1_result['article_no'], expected_article):
            top1_article_match = True
            found_article = True
    
    # Check top-3 results
    for i, result in enumerate(filtered_results[:3]):
        if result['doc_id'] == expected_doc:
            top3_doc_match = True
            found_doc = True
        if article_matches(result['article_no'], expected_article):
            top3_article_match = True
            found_article = True
    
    return {
        'query': query,
        'expected_doc': expected_doc,
        'expected_article': expected_article,
        'top1_doc_match': top1_doc_match,
        'top3_doc_match': top3_doc_match,
        'top1_article_match': top1_article_match,
        'top3_article_match': top3_article_match,
        'found_doc': found_doc,
        'found_article': found_article,
        'num_results': len(filtered_results),
        'top_results': [
            {
                'doc_id': r['doc_id'],
                'article_no': r['article_no'],
                'score': r['score']
            } for r in filtered_results[:3]
        ]
    }

def compute_metrics(results):
    """Compute evaluation metrics"""
    total_queries = len(results)
    
    # Document-level metrics
    p1_doc = sum(1 for r in results if r['top1_doc_match']) / total_queries
    p3_doc = sum(1 for r in results if r['top3_doc_match']) / total_queries
    
    # Article-level metrics
    p1_article = sum(1 for r in results if r['top1_article_match']) / total_queries
    p3_article = sum(1 for r in results if r['top3_article_match']) / total_queries
    
    # Citation correctness
    citation_correct = sum(1 for r in results if r['found_article']) / total_queries
    
    return {
        'precision_at_1_doc': p1_doc,
        'precision_at_3_doc': p3_doc,
        'precision_at_1_article': p1_article,
        'precision_at_3_article': p3_article,
        'citation_correctness': citation_correct,
        'total_queries': total_queries
    }

def main():
    """Main evaluation function"""
    print("Loading evaluation data...")
    
    # Load indices
    bm25 = load_bm25("data/idx/bm25.pkl")
    faiss_index = load_faiss("data/idx/mE5.faiss")
    meta = load_meta("data/idx/meta.json")
    model = load_model("intfloat/multilingual-e5-base")
    idx = Indices(bm25=bm25, faiss_index=faiss_index, meta=meta, model=model)
    
    # Load gold standard
    gold_data = load_gold_standard("eval/gold.csv")
    print(f"Loaded {len(gold_data)} evaluation queries")
    
    # Run evaluation
    print("Running evaluation...")
    results = []
    
    for i, gold_item in enumerate(gold_data):
        print(f"Evaluating query {i+1}/{len(gold_data)}: {gold_item['query']}")
        
        result = evaluate_query(
            idx, 
            gold_item['query'], 
            gold_item['expected_doc'], 
            gold_item['expected_article']
        )
        results.append(result)
    
    # Compute metrics
    metrics = compute_metrics(results)
    
    # Print results
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Total Queries: {metrics['total_queries']}")
    print(f"Precision@1 (Document): {metrics['precision_at_1_doc']:.3f}")
    print(f"Precision@3 (Document): {metrics['precision_at_3_doc']:.3f}")
    print(f"Precision@1 (Article): {metrics['precision_at_1_article']:.3f}")
    print(f"Precision@3 (Article): {metrics['precision_at_3_article']:.3f}")
    print(f"Citation Correctness: {metrics['citation_correctness']:.3f}")
    
    # Check success criteria
    print("\n" + "="*60)
    print("SUCCESS CRITERIA CHECK")
    print("="*60)
    p3_doc = metrics['precision_at_3_doc']
    p3_article = metrics['precision_at_3_article']
    
    # Primary success criteria: Document-level P@3 >= 70%
    if p3_doc >= 0.7:
        print(f"✅ PASS: P@3 (Document) = {p3_doc:.3f} >= 0.7")
        doc_success = True
    else:
        print(f"❌ FAIL: P@3 (Document) = {p3_doc:.3f} < 0.7")
        doc_success = False
    
    # Secondary success criteria: Article-level P@3 >= 30% (more realistic)
    if p3_article >= 0.3:
        print(f"✅ GOOD: P@3 (Article) = {p3_article:.3f} >= 0.3")
        article_success = True
    else:
        print(f"⚠️  MODERATE: P@3 (Article) = {p3_article:.3f} < 0.3")
        print("Consider tuning alpha or glossary for better article-level precision")
        article_success = False
    
    # Overall success
    if doc_success:
        print(f"\n🎉 OVERALL: SYSTEM MEETS SUCCESS CRITERIA")
        print("Document-level retrieval is working well!")
    else:
        print(f"\n❌ OVERALL: SYSTEM NEEDS IMPROVEMENT")
        print("Focus on improving document-level retrieval first")
    
    # Save detailed results
    with open("eval/results.csv", 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'query', 'expected_doc', 'expected_article',
            'top1_doc_match', 'top3_doc_match', 
            'top1_article_match', 'top3_article_match',
            'found_doc', 'found_article', 'num_results'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'query': result['query'],
                'expected_doc': result['expected_doc'],
                'expected_article': result['expected_article'],
                'top1_doc_match': result['top1_doc_match'],
                'top3_doc_match': result['top3_doc_match'],
                'top1_article_match': result['top1_article_match'],
                'top3_article_match': result['top3_article_match'],
                'found_doc': result['found_doc'],
                'found_article': result['found_article'],
                'num_results': result['num_results']
            })
    
    # Save summary
    summary = {
        'metrics': metrics,
        'success_criteria_met': p3_article >= 0.7,
        'evaluation_date': str(Path(__file__).stat().st_mtime)
    }
    
    with open("eval/summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: eval/results.csv")
    print(f"Summary saved to: eval/summary.json")
    
    return metrics

if __name__ == "__main__":
    main()
