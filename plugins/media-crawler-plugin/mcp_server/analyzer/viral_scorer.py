"""
Viral Score Calculator & Content Structure Analyzer.
"""
from typing import Dict, Any, List
import re

class ViralScorer:
    @staticmethod
    def calculate_score(comments: int = 0, likes: int = 0, shares: int = 0, collects: int = 0) -> float:
        """
        Calculate viral heat index:
        - Comments: 5.0x weight (community resonance and debate)
        - Shares/Reposts: 3.5x weight (viral spread)
        - Collects: 2.0x weight (practical value/bookmarking)
        - Likes: 1.0x weight (general impression)
        """
        score = (comments * 5.0) + (shares * 3.5) + (collects * 2.0) + (likes * 1.0)
        return round(score, 2)

    @staticmethod
    def analyze_structure(title: str, content: str) -> Dict[str, Any]:
        """
        Extract golden hook, emotional triggers, and structural segments.
        """
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
        hook = paragraphs[0] if paragraphs else title

        # Emotion trigger pattern keywords
        emotion_keywords = {
            "conflict": ["没想到", "翻脸", "争吵", "隐瞒", "拒绝", "断绝", "怒斥", "反悔"],
            "suspense": ["其实", "秘密", "真相", "居然", "竟然", "万万没想到", "谁料"],
            "resonance": ["心酸", "委屈", "不容易", "扎心", "泪目", "感动", "现实"],
            "benefits": ["建议", "干货", "收藏", "避坑", "诀窍", "方法", "省钱", "单价"]
        }

        detected_triggers = []
        for trigger_type, kws in emotion_keywords.items():
            matched = [kw for kw in kws if kw in content or kw in title]
            if matched:
                detected_triggers.append({
                    "type": trigger_type,
                    "matched_keywords": matched[:3]
                })

        # Estimate reading time (average 300 words/min)
        word_count = len(content)
        reading_time_min = round(word_count / 300.0, 1)

        return {
            "title": title,
            "word_count": word_count,
            "estimated_reading_minutes": reading_time_min,
            "golden_hook": hook[:150],
            "detected_emotional_triggers": detected_triggers,
            "has_cta_ending": any(q in (paragraphs[-1] if paragraphs else "") for q in ["？", "?", "你怎么看", "留言", "评论区", "觉得呢"]),
            "paragraph_count": len(paragraphs)
        }
