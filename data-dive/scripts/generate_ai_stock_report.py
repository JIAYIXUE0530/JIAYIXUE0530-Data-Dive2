#!/usr/bin/env python3
"""
AI Stock Picker Report Generator
Generates daily stock picking reports for the dashboard
"""

import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIVE_DIR = Path(__file__).parent.parent
AI_STOCK_PICKER_DIR = BASE_DIR / '.trae' / 'skills' / 'ai-stock-picker'
DATA_DIR = AI_STOCK_PICKER_DIR / 'data'
OUTPUT_DIR = DATA_DIVE_DIR / 'public' / 'outputs' / 'ai-stock-reports'

def load_recommendations():
    """Load recommendations from AI stock picker data"""
    recommendations_file = DATA_DIR / 'recommendations.json'
    
    if not recommendations_file.exists():
        return []
    
    with open(recommendations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('recommendations', [])

def load_performance():
    """Load performance tracking data"""
    performance_file = DATA_DIR / 'performance.json'
    
    if not performance_file.exists():
        return {}
    
    with open(performance_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_report(recommendation_data):
    """Generate a dashboard report from recommendation data"""
    
    date = recommendation_data['date']
    report_id = f"ai-stock-{date}"
    
    bullish_recs = recommendation_data['recommendations']['bullish']
    bearish_recs = recommendation_data['recommendations']['bearish']
    
    conclusions = []
    
    for idx, rec in enumerate(bearish_recs, 1):
        conclusions.append({
            "id": idx,
            "title": f"🔴 看空: {rec['sector']} ({rec['etf']})",
            "description": f"置信度: {rec['confidence']}/10\n\n" + "\n".join([f"• {r}" for r in rec['reasons']]),
            "data_support": f"风险因素: {', '.join(rec.get('risks', []))}",
            "importance": "high" if rec['confidence'] >= 8 else "medium",
            "chart_type": "bar",
            "chart_data": {
                "labels": ["置信度"],
                "datasets": [{
                    "label": rec['sector'],
                    "data": [rec['confidence']],
                    "backgroundColor": "rgba(239, 68, 68, 0.8)"
                }]
            },
            "metadata": {
                "direction": "bearish",
                "etf": rec['etf'],
                "confidence": rec['confidence'],
                "key_levels": rec.get('key_levels', {})
            }
        })
    
    for idx, rec in enumerate(bullish_recs, len(conclusions) + 1):
        conclusions.append({
            "id": idx,
            "title": f"🟢 看好: {rec['sector']} ({rec['etf']})",
            "description": f"置信度: {rec['confidence']}/10\n\n" + "\n".join([f"• {r}" for r in rec['reasons']]),
            "data_support": f"风险因素: {', '.join(rec.get('risks', []))}",
            "importance": "high" if rec['confidence'] >= 8 else "medium",
            "chart_type": "bar",
            "chart_data": {
                "labels": ["置信度"],
                "datasets": [{
                    "label": rec['sector'],
                    "data": [rec['confidence']],
                    "backgroundColor": "rgba(34, 197, 94, 0.8)"
                }]
            },
            "metadata": {
                "direction": "bullish",
                "etf": rec['etf'],
                "confidence": rec['confidence'],
                "key_levels": rec.get('key_levels', {})
            }
        })
    
    report = {
        "meta": {
            "title": f"AI选股日报 - {date}",
            "generated_at": recommendation_data['timestamp'],
            "version": "1.0",
            "report_type": "ai-stock-picker"
        },
        "summary": {
            "overall": recommendation_data['market_summary'],
            "total_conclusions": len(conclusions),
            "high_importance_count": len([c for c in conclusions if c['importance'] == 'high']),
            "source_files": [],
            "market_condition": recommendation_data['market_condition'],
            "vix": recommendation_data['market_indicators']['vix'],
            "bullish_count": len(bullish_recs),
            "bearish_count": len(bearish_recs),
            "avg_confidence": sum([r['confidence'] for r in bullish_recs + bearish_recs]) / len(bullish_recs + bearish_recs)
        },
        "conclusions": conclusions,
        "market_indicators": recommendation_data['market_indicators'],
        "key_risks": recommendation_data.get('key_risks', []),
        "strategy_suggestions": recommendation_data.get('strategy_suggestions', []),
        "next_focus": recommendation_data.get('next_focus', [])
    }
    
    return report_id, report

def save_report(report_id, report):
    """Save report to output directory"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    report_file = OUTPUT_DIR / f"{report_id}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Report saved: {report_file}")
    return report_file

def update_index(report_id, report):
    """Update the reports index"""
    index_file = OUTPUT_DIR / 'reports-index.json'
    
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = {"reports": []}
    
    existing_ids = [r['id'] for r in index_data['reports']]
    
    if report_id not in existing_ids:
        index_entry = {
            "id": report_id,
            "title": report['meta']['title'],
            "created_at": report['meta']['generated_at'],
            "report_type": "ai-stock-picker",
            "market_condition": report['summary']['market_condition'],
            "vix": report['summary']['vix'],
            "total_recommendations": report['summary']['total_conclusions'],
            "high_confidence_count": report['summary']['high_importance_count'],
            "bullish_count": report['summary']['bullish_count'],
            "bearish_count": report['summary']['bearish_count']
        }
        
        index_data['reports'].insert(0, index_entry)
        
        index_data['reports'] = sorted(
            index_data['reports'],
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Index updated: {len(index_data['reports'])} reports")

def main():
    """Main function to generate AI stock picker reports"""
    print("🤖 AI Stock Picker Report Generator")
    print("=" * 50)
    
    recommendations = load_recommendations()
    
    if not recommendations:
        print("⚠️  No recommendations found")
        return
    
    print(f"📊 Found {len(recommendations)} recommendation(s)")
    
    for rec in recommendations:
        report_id, report = generate_report(rec)
        save_report(report_id, report)
        update_index(report_id, report)
    
    performance = load_performance()
    if performance:
        print(f"\n📈 Performance Tracking:")
        print(f"   Total Predictions: {performance['performance_metrics']['total_predictions']}")
        print(f"   Average Confidence: {performance['performance_metrics']['avg_confidence']:.1f}")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    main()
