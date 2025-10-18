# -*- coding: utf-8 -*-
"""情感智能引擎"""
from typing import Dict, List
from datetime import datetime

class EmotionalIntelligenceEngine:
    """
    情感智能引擎
    
    实现细粒度情感识别和情感状态管理
    """
    
    def __init__(self):
        self.emotion_history = []
        self.current_emotion_state = {
            'primary': 'neutral',
            'secondary': [],
            'intensity': 0.5,
            'valence': 0.0  # -1(负面) 到 +1(正面)
        }
        
        # 情感维度模型
        self.emotion_dimensions = {
            'joy': {'valence': 0.8, 'arousal': 0.7, 'dominance': 0.6},
            'sadness': {'valence': -0.7, 'arousal': -0.4, 'dominance': -0.5},
            'anger': {'valence': -0.6, 'arousal': 0.8, 'dominance': 0.7},
            'fear': {'valence': -0.8, 'arousal': 0.6, 'dominance': -0.6},
            'surprise': {'valence': 0.2, 'arousal': 0.8, 'dominance': 0.0},
            'disgust': {'valence': -0.7, 'arousal': 0.5, 'dominance': 0.3},
            'trust': {'valence': 0.6, 'arousal': 0.3, 'dominance': 0.4},
            'anticipation': {'valence': 0.4, 'arousal': 0.5, 'dominance': 0.3},
            'frustration': {'valence': -0.5, 'arousal': 0.6, 'dominance': 0.2},
            'contentment': {'valence': 0.7, 'arousal': 0.2, 'dominance': 0.4},
            'anxiety': {'valence': -0.6, 'arousal': 0.7, 'dominance': -0.4},
            'excitement': {'valence': 0.8, 'arousal': 0.9, 'dominance': 0.5}
        }
        
        # 情感关键词
        self.emotion_keywords = {
            'joy': ['happy', 'glad', 'joyful', '开心', '高兴', '快乐', '😊', '😄'],
            'sadness': ['sad', 'unhappy', 'depressed', '难过', '伤心', '沮丧', '😢', '😭'],
            'anger': ['angry', 'mad', 'furious', '生气', '愤怒', '恼火', '😠', '😡'],
            'fear': ['scared', 'afraid', 'fearful', '害怕', '恐惧', '担心', '😨', '😰'],
            'surprise': ['surprised', 'shocked', 'amazed', '惊讶', '震惊', '吃惊', '😲', '😮'],
            'frustration': ['frustrated', 'annoyed', '烦躁', '郁闷', '烦恼'],
            'contentment': ['content', 'satisfied', '满意', '满足', '惬意'],
            'anxiety': ['anxious', 'worried', 'nervous', '焦虑', '紧张', '不安'],
            'excitement': ['excited', 'thrilled', '兴奋', '激动', '🎉']
        }
    
    def analyze_emotion(self, message: str, context: Dict) -> Dict:
        """
        分析消息中的情感
        
        Args:
            message: 用户消息
            context: 对话上下文
            
        Returns:
            Dict: 情感分析结果
        """
        # 1. 检测情感
        detected_emotions = self._detect_emotions(message)
        
        # 2. 计算情感强度
        intensity = self._calculate_intensity(message, detected_emotions)
        
        # 3. 确定主要和次要情感
        primary_emotion, secondary_emotions = self._prioritize_emotions(detected_emotions)
        
        # 4. 计算情感效价
        valence = self._calculate_valence(primary_emotion, secondary_emotions)
        
        # 5. 分析情感趋势
        trend = self._analyze_trend(primary_emotion)
        
        # 6. 更新状态
        emotion_state = {
            'primary': primary_emotion,
            'secondary': secondary_emotions,
            'intensity': intensity,
            'valence': valence,
            'arousal': self.emotion_dimensions.get(primary_emotion, {}).get('arousal', 0.5),
            'dominance': self.emotion_dimensions.get(primary_emotion, {}).get('dominance', 0.0),
            'trend': trend,
            'detected_words': detected_emotions.get('words', [])
        }
        
        self.current_emotion_state = emotion_state
        self.emotion_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': emotion_state
        })
        
        # 保持历史记录在合理范围
        if len(self.emotion_history) > 20:
            self.emotion_history = self.emotion_history[-20:]
        
        return emotion_state
    
    def _detect_emotions(self, message: str) -> Dict:
        """检测消息中的情感"""
        message_lower = message.lower()
        detected = {}
        detected_words = []
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
                    detected_words.append(keyword)
            
            if score > 0:
                detected[emotion] = score
        
        return {'emotions': detected, 'words': detected_words}
    
    def _calculate_intensity(self, message: str, detected_emotions: Dict) -> float:
        """计算情感强度"""
        base_intensity = 0.5
        
        # 基于检测到的情感数量
        emotion_count = sum(detected_emotions.get('emotions', {}).values())
        if emotion_count > 0:
            base_intensity = min(0.3 + emotion_count * 0.15, 1.0)
        
        # 强化词检测
        intensifiers = ['很', '非常', '特别', '超', '太', 'very', 'so', 'extremely']
        for intensifier in intensifiers:
            if intensifier in message.lower():
                base_intensity = min(base_intensity + 0.15, 1.0)
        
        # 标点符号
        if '!' in message or '！' in message:
            base_intensity = min(base_intensity + 0.1, 1.0)
        
        return round(base_intensity, 2)
    
    def _prioritize_emotions(self, detected_emotions: Dict) -> tuple:
        """确定主要和次要情感"""
        emotions = detected_emotions.get('emotions', {})
        
        if not emotions:
            return 'neutral', []
        
        # 按分数排序
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_emotions[0][0]
        secondary = [e[0] for e in sorted_emotions[1:3]]
        
        return primary, secondary
    
    def _calculate_valence(self, primary_emotion: str, secondary_emotions: List[str]) -> float:
        """计算情感效价"""
        primary_valence = self.emotion_dimensions.get(primary_emotion, {}).get('valence', 0.0)
        
        # 考虑次要情感的影响
        secondary_valence = 0.0
        if secondary_emotions:
            secondary_values = [
                self.emotion_dimensions.get(e, {}).get('valence', 0.0)
                for e in secondary_emotions
            ]
            if secondary_values:
                secondary_valence = sum(secondary_values) / len(secondary_values) * 0.3
        
        return round(primary_valence * 0.7 + secondary_valence, 2)
    
    def _analyze_trend(self, current_emotion: str) -> str:
        """分析情感趋势"""
        if len(self.emotion_history) < 2:
            return 'stable'
        
        recent_emotions = [h['state']['primary'] for h in self.emotion_history[-3:]]
        recent_valences = [
            self.emotion_dimensions.get(e, {}).get('valence', 0.0)
            for e in recent_emotions
        ]
        
        if len(recent_valences) < 2:
            return 'stable'
        
        # 计算趋势
        trend_value = recent_valences[-1] - recent_valences[0]
        
        if trend_value > 0.3:
            return 'improving'
        elif trend_value < -0.3:
            return 'declining'
        else:
            return 'stable'
    
    def get_response_guidance(self, emotion_state: Dict) -> Dict:
        """
        根据情感状态提供回复指导
        
        Args:
            emotion_state: 情感状态
            
        Returns:
            Dict: 回复指导
        """
        primary = emotion_state['primary']
        intensity = emotion_state['intensity']
        valence = emotion_state['valence']
        
        guidance = {
            'tone': 'neutral',
            'approach': 'balanced',
            'empathy_level': 0.5,
            'suggestions': []
        }
        
        # 基于主要情感的指导
        if primary in ['sadness', 'anxiety', 'fear']:
            guidance['tone'] = 'gentle'
            guidance['approach'] = 'supportive'
            guidance['empathy_level'] = 0.9
            guidance['suggestions'] = [
                '表达理解和共情',
                '提供情感支持',
                '避免说教或立即给建议',
                '语气温和安慰'
            ]
        elif primary in ['anger', 'frustration']:
            guidance['tone'] = 'calm'
            guidance['approach'] = 'validating'
            guidance['empathy_level'] = 0.8
            guidance['suggestions'] = [
                '承认对方的感受',
                '保持冷静和理解',
                '不要争辩或反驳',
                '给予空间表达'
            ]
        elif primary in ['joy', 'excitement', 'contentment']:
            guidance['tone'] = 'warm'
            guidance['approach'] = 'celebratory'
            guidance['empathy_level'] = 0.7
            guidance['suggestions'] = [
                '分享对方的喜悦',
                '表达真诚的高兴',
                '可以适当活泼',
                '避免泼冷水'
            ]
        elif primary == 'surprise':
            guidance['tone'] = 'engaged'
            guidance['approach'] = 'curious'
            guidance['empathy_level'] = 0.6
            guidance['suggestions'] = [
                '表现出兴趣',
                '询问更多细节',
                '分享相关经历'
            ]
        
        # 根据强度调整
        if intensity > 0.7:
            guidance['empathy_level'] = min(guidance['empathy_level'] + 0.2, 1.0)
            guidance['suggestions'].append('情感强度高,给予更多关注')
        
        return guidance
