# fix_tools.py - 关键优化部分 (完整修复版)
import asyncio
import random
import time
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from openai import OpenAI
from utils import (
    EnhancedTextProcessor, 
    ConversationAnalyzer,
    PerformanceMonitor,
    ScheduleSimulator,
    MemoryManager
)

# ==================== 新增优化模块 ====================

class EnhancedConversationManager:
    """增强对话管理器 - 避免机械引用和重复回复"""
    
    def __init__(self):
        self.conversation_states = {}
        self.last_replies = {}
        self.daily_schedule = self._get_daily_schedule()
        self.message_queues = defaultdict(asyncio.Queue)
        self.processing_lock = asyncio.Lock()
        
    def _get_daily_schedule(self):
        """获取日常安排模板"""
        return {
            'morning': {'hours': range(6, 12), 'activities': ['checking emails', 'morning meetings', 'planning day']},
            'afternoon': {'hours': range(12, 18), 'activities': ['client meetings', 'market analysis', 'project work']},
            'evening': {'hours': range(18, 22), 'activities': ['wrapping up work', 'personal time', 'reading']},
            'night': {'hours': range(22, 6), 'activities': ['resting', 'sleeping']}
        }
    
    def get_current_activity(self):
        """获取当前时间段的活动"""
        current_hour = datetime.now().hour
        for period, config in self.daily_schedule.items():
            if current_hour in config['hours']:
                return random.choice(config['activities'])
        return "working"
    
    def should_combine_responses(self, user_id: str, current_message: str, previous_message: str = None) -> bool:
        """判断是否应该合并回复"""
        if not previous_message:
            return False
            
        # 短时间内连续消息应该合并回复
        time_diff = time.time() - self.conversation_states.get(f"{user_id}_last_message", 0)
        if time_diff < 30:  # 30秒内的连续消息
            return True
            
        # 相关话题应该合并
        if self._are_messages_related(current_message, previous_message):
            return True
            
        return False
    
    def _are_messages_related(self, msg1: str, msg2: str) -> bool:
        """判断两条消息是否相关"""
        msg1_words = set(msg1.lower().split())
        msg2_words = set(msg2.lower().split())
        
        # 计算相似度
        similarity = len(msg1_words.intersection(msg2_words)) / len(msg1_words.union(msg2_words))
        return similarity > 0.3
    
    def is_repetitive_reply(self, user_id: str, new_reply: str) -> bool:
        """检查是否与最近回复重复"""
        if user_id not in self.last_replies:
            self.last_replies[user_id] = []
            return False
            
        last_replies = self.last_replies[user_id][-3:]  # 检查最近3条回复
        
        for reply in last_replies:
            if self._calculate_similarity(reply, new_reply) > 0.7:
                return True
                
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def update_conversation_state(self, user_id: str, message: str, reply: str):
        """更新对话状态"""
        current_time = time.time()
        self.conversation_states[f"{user_id}_last_message"] = current_time
        
        if user_id not in self.last_replies:
            self.last_replies[user_id] = []
            
        self.last_replies[user_id].append(reply)
        
        # 只保留最近10条回复
        if len(self.last_replies[user_id]) > 10:
            self.last_replies[user_id] = self.last_replies[user_id][-10:]
    
    async def process_message_queue(self, user_id: str, processor_func):
        """处理消息队列"""
        async with self.processing_lock:
            try:
                while not self.message_queues[user_id].empty():
                    message_data = await asyncio.wait_for(
                        self.message_queues[user_id].get(), 
                        timeout=1.0
                    )
                    await processor_func(message_data)
                    self.message_queues[user_id].task_done()
            except asyncio.TimeoutError:
                pass

class EnhancedEmotionEngine:
    """增强情绪引擎 - 支持更丰富的情绪表达和波动"""
    
    def __init__(self):
        self.emotion_intensity = 0.5
        self.current_mood = "calm"
        self.mood_history = []
        
        # 扩展情绪映射
        self.emotion_mappings = {
            'calm': {
                'adverbs': ['calmly', 'quietly', 'gently', 'peacefully'],
                'phrases': ['I see', 'I understand', 'That makes sense', 'I appreciate that'],
                'emojis': ['💭', '✨', '🌿'],
                'response_style': 'balanced'
            },
            'playful': {
                'adverbs': ['playfully', 'cheerfully', 'happily', 'mischievously'],
                'phrases': ['Haha', 'That\'s funny', 'You\'re amusing', 'What a fun thought'],
                'emojis': ['😄', '😊', '😂', '🤣', '🎉'],
                'response_style': 'lighthearted'
            },
            'sad': {
                'adverbs': ['softly', 'gently', 'quietly', 'empathetically'],
                'phrases': ['I\'m sorry', 'That sounds difficult', 'I understand how you feel', 'That must be hard'],
                'emojis': ['💔', '😢', '🌧️', '🕯️'],
                'response_style': 'comforting'
            },
            'excited': {
                'adverbs': ['excitedly', 'enthusiastically', 'energetically', 'thrilled'],
                'phrases': ['Wow', 'That\'s amazing', 'How exciting', 'I\'m thrilled'],
                'emojis': ['🎉', '✨', '😃', '🌟', '🚀'],
                'response_style': 'energetic'
            },
            'thoughtful': {
                'adverbs': ['thoughtfully', 'carefully', 'reflectively', 'contemplatively'],
                'phrases': ['Let me think', 'That\'s an interesting point', 'I\'ve been considering', 'That makes me wonder'],
                'emojis': ['🤔', '💭', '🧠', '📚'],
                'response_style': 'reflective'
            },
            'teasing': {
                'adverbs': ['teasingly', 'playfully', 'lightly', 'with a smile'],
                'phrases': ['Oh really?', 'You don\'t say', 'Is that so?', 'I see what you did there'],
                'emojis': ['😏', '😉', '🤨', '👀'],
                'response_style': 'playful'
            },
            'warm': {
                'adverbs': ['warmly', 'kindly', 'affectionately', 'gently'],
                'phrases': ['That\'s lovely', 'I appreciate you', 'You\'re so kind', 'That warms my heart'],
                'emojis': ['❤️', '🤗', '💕', '☀️'],
                'response_style': 'affectionate'
            },
            'concerned': {
                'adverbs': ['concernedly', 'worriedly', 'anxiously', 'carefully'],
                'phrases': ['I\'m concerned', 'That worries me', 'Are you okay?', 'I want to make sure'],
                'emojis': ['😟', '🤔', '💭', '⚠️'],
                'response_style': 'caring'
            }
        }
        
        # 情绪转换概率
        self.mood_transitions = {
            'calm': {'playful': 0.3, 'thoughtful': 0.4, 'warm': 0.2, 'calm': 0.1},
            'playful': {'calm': 0.4, 'teasing': 0.3, 'excited': 0.2, 'playful': 0.1},
            'thoughtful': {'calm': 0.5, 'concerned': 0.2, 'warm': 0.2, 'thoughtful': 0.1},
            'excited': {'calm': 0.4, 'playful': 0.3, 'warm': 0.2, 'excited': 0.1},
            'warm': {'calm': 0.5, 'playful': 0.2, 'thoughtful': 0.2, 'warm': 0.1}
        }
    
    def analyze_emotional_context(self, user_message: str, chat_history: List[Dict]) -> Dict:
        """分析情感上下文"""
        emotion_analysis = self._basic_emotion_analysis(user_message)
        historical_influence = self._analyze_historical_mood(chat_history)
        natural_variation = self._calculate_natural_variation()
        
        final_mood = self._determine_final_mood(emotion_analysis, historical_influence, natural_variation)
        
        return {
            'primary_emotion': final_mood,
            'intensity': self.emotion_intensity,
            'confidence': emotion_analysis.get('confidence', 0.7),
            'emotional_words': emotion_analysis.get('emotional_words', []),
            'response_style': self.emotion_mappings[final_mood]['response_style'],
            'mood_transition': self._get_mood_transition_description(final_mood)
        }
    
    def _basic_emotion_analysis(self, text: str) -> Dict:
        """基础情感分析"""
        emotion_keywords = {
            'playful': ['haha', 'lol', 'funny', 'joke', 'laugh', '😂', '😄'],
            'sad': ['sad', 'cry', 'upset', 'unhappy', '😢', '😭'],
            'excited': ['excited', 'wow', 'amazing', 'great', '😃', '🎉'],
            'thoughtful': ['think', 'consider', 'wonder', 'thought', '🤔'],
            'teasing': ['tease', 'joking', 'kidding', '😏', '😉'],
            'warm': ['love', 'care', 'appreciate', 'thank', '❤️', '🤗'],
            'concerned': ['worry', 'concern', 'anxious', 'nervous', '😟']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        detected_words = []
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + 1
                    detected_words.append(keyword)
        
        if not emotion_scores:
            return {'primary_emotion': 'calm', 'confidence': 0.3, 'emotional_words': []}
        
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = min(emotion_scores[primary_emotion] / len(text.split()) * 10, 1.0)
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': round(confidence, 2),
            'emotional_words': detected_words,
            'all_emotions': emotion_scores
        }
    
    def _analyze_historical_mood(self, chat_history: List[Dict]) -> str:
        """分析历史情绪"""
        if len(chat_history) < 3:
            return 'calm'
            
        recent_moods = []
        for msg in chat_history[-3:]:
            if msg.get('role') == 'user':
                emotion = self._basic_emotion_analysis(msg.get('content', ''))
                recent_moods.append(emotion['primary_emotion'])
        
        if recent_moods:
            return max(set(recent_moods), key=recent_moods.count)
        return 'calm'
    
    def _calculate_natural_variation(self) -> str:
        """计算自然情绪波动"""
        current_hour = datetime.now().hour
        if 6 <= current_hour < 10:
            time_based_mood = 'excited'
        elif 10 <= current_hour < 14:
            time_based_mood = 'calm'
        elif 14 <= current_hour < 18:
            time_based_mood = 'thoughtful'
        elif 18 <= current_hour < 22:
            time_based_mood = 'warm'
        else:
            time_based_mood = 'calm'
            
        return time_based_mood
    
    def _determine_final_mood(self, current_emotion: Dict, historical: str, natural: str) -> str:
        """确定最终情绪状态"""
        moods = [current_emotion['primary_emotion'], historical, natural]
        
        weights = {
            current_emotion['primary_emotion']: 0.5,
            historical: 0.3,
            natural: 0.2
        }
        
        if self.current_mood in self.mood_transitions:
            transitions = self.mood_transitions[self.current_mood]
            for mood in moods:
                if mood in transitions:
                    weights[mood] *= transitions[mood]
        
        final_mood = max(weights.items(), key=lambda x: x[1])[0]
        
        self.current_mood = final_mood
        self.mood_history.append(final_mood)
        if len(self.mood_history) > 10:
            self.mood_history.pop(0)
            
        self.emotion_intensity = current_emotion.get('confidence', 0.5)
        
        return final_mood
    
    def _get_mood_transition_description(self, new_mood: str) -> str:
        """获取情绪转换描述"""
        if not self.mood_history or len(self.mood_history) < 2:
            return "neutral"
            
        previous_mood = self.mood_history[-2]
        if previous_mood == new_mood:
            return "consistent"
        elif (previous_mood, new_mood) in [('sad', 'playful'), ('concerned', 'calm')]:
            return "improving"
        elif (previous_mood, new_mood) in [('playful', 'sad'), ('excited', 'concerned')]:
            return "dampening"
        else:
            return "shifting"
    
    def adjust_tone(self, reply: str, emotion_analysis: Dict) -> str:
        """根据情绪调整语气"""
        emotion = emotion_analysis['primary_emotion']
        intensity = emotion_analysis['intensity']
        mapping = self.emotion_mappings.get(emotion, self.emotion_mappings['calm'])
        
        if random.random() < intensity * 0.4:
            adverb = random.choice(mapping['adverbs'])
            reply = f"{adverb.capitalize()}, {reply.lower()}"
        
        if random.random() < intensity * 0.3:
            phrase = random.choice(mapping['phrases'])
            reply = f"{phrase}. {reply}"
        
        if random.random() < intensity * 0.5:
            emoji = random.choice(mapping['emojis'])
            if reply.endswith(('.', '!', '?')):
                reply = f"{reply[:-1]} {emoji}{reply[-1]}"
            else:
                reply = f"{reply} {emoji}"
        
        reply = self._apply_emotion_specific_adjustments(reply, emotion, intensity)
        
        return reply
    
    def _apply_emotion_specific_adjustments(self, reply: str, emotion: str, intensity: float) -> str:
        """应用情绪特定的调整"""
        adjustments = {
            'playful': {
                'high': lambda r: r.replace('.', '!').replace('?', '?!'),
                'medium': lambda r: r + '~',
                'low': lambda r: r
            },
            'sad': {
                'high': lambda r: r.replace('!', '.').replace('?', '...'),
                'medium': lambda r: r + '...',
                'low': lambda r: r
            },
            'excited': {
                'high': lambda r: r.upper() if len(r.split()) < 5 else r,
                'medium': lambda r: r + '!',
                'low': lambda r: r
            },
            'thoughtful': {
                'high': lambda r: r + '...',
                'medium': lambda r: r,
                'low': lambda r: r
            }
        }
        
        if emotion in adjustments:
            intensity_level = 'high' if intensity > 0.7 else 'medium' if intensity > 0.4 else 'low'
            if intensity_level in adjustments[emotion]:
                reply = adjustments[emotion][intensity_level](reply)
        
        return reply

class SemanticReplySplitter:
    """语义回复分割器 - 基于语义完整性分割"""
    
    def __init__(self):
        self.sentence_enders = ['.', '!', '?', '。', '！', '？']
        self.discourse_markers = [
            'however', 'but', 'and', 'so', 'then', 'therefore',
            'meanwhile', 'additionally', 'furthermore', 'consequently'
        ]
    
    def should_split(self, reply: str) -> bool:
        """判断是否应该分割回复"""
        sentences = self._split_into_sentences(reply)
        
        # 多个句子且长度适中时分割
        if len(sentences) > 1 and len(reply) > 80:
            return True
            
        # 包含话语标记时分割
        if any(marker in reply.lower() for marker in self.discourse_markers):
            return True
            
        return False
    
    def split_semantically(self, reply: str) -> List[str]:
        """基于语义分割回复"""
        sentences = self._split_into_sentences(reply)
        
        if len(sentences) <= 1:
            return [reply]
        
        # 语义分组
        semantic_groups = self._group_semantically(sentences)
        
        # 确保每组有语义完整性
        final_groups = []
        for group in semantic_groups:
            if self._has_semantic_completeness(group):
                final_groups.append(' '.join(group))
            else:
                # 如果不完整，合并到前一组
                if final_groups:
                    final_groups[-1] += ' ' + ' '.join(group)
                else:
                    final_groups.append(' '.join(group))
        
        return final_groups
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        sentences = re.split(r'[.!?。！？]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _group_semantically(self, sentences: List[str]) -> List[List[str]]:
        """基于语义分组句子"""
        if not sentences:
            return []
        
        groups = []
        current_group = [sentences[0]]
        
        for i in range(1, len(sentences)):
            current_sentence = sentences[i]
            previous_sentence = sentences[i-1]
            
            # 检查语义连续性
            if self._are_sentences_connected(previous_sentence, current_sentence):
                current_group.append(current_sentence)
            else:
                groups.append(current_group)
                current_group = [current_sentence]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _are_sentences_connected(self, sent1: str, sent2: str) -> bool:
        """检查两个句子是否语义连接"""
        # 检查代词指代
        pronoun_references = ['it', 'this', 'that', 'these', 'those', 'he', 'she', 'they']
        sent1_words = set(sent1.lower().split())
        sent2_words = set(sent2.lower().split())
        
        # 如果有共同的实体或概念
        common_entities = sent1_words.intersection(sent2_words)
        if len(common_entities) >= 2:
            return True
        
        # 如果有代词指代
        if any(pronoun in sent2_words for pronoun in pronoun_references):
            return True
        
        # 检查话语标记
        if any(marker in sent2.lower() for marker in self.discourse_markers):
            return True
        
        return False
    
    def _has_semantic_completeness(self, sentence_group: List[str]) -> bool:
        """检查句子组是否有语义完整性"""
        combined_text = ' '.join(sentence_group).lower()
        
        # 检查是否包含完整的想法
        completeness_indicators = [
            'because', 'so', 'therefore', 'thus', 'as a result',
            'in conclusion', 'to summarize', 'overall'
        ]
        
        if any(indicator in combined_text for indicator in completeness_indicators):
            return True
        
        # 检查是否有问答结构
        if '?' in combined_text and any(word in combined_text for word in ['answer', 'reply', 'response']):
            return True
        
        # 默认较长的组是完整的
        return len(sentence_group) >= 2 or len(combined_text) > 50

class AdvancedLogicDetector:
    """高级逻辑检测器 - 检测语义错乱和情绪突变"""
    
    def __init__(self, character_profile):
        self.character_profile = character_profile
        self.known_facts = self._extract_known_facts()
        
    def _extract_known_facts(self):
        """从角色配置中提取已知事实"""
        profile = self.character_profile
        facts = {
            'name': profile['basic_info']['name'],
            'chinese_name': profile['basic_info']['chinese_name'],
            'age': profile['basic_info']['age'],
            'occupation': profile['basic_info']['occupation'],
            'current_city': profile['basic_info']['current_city'],
            'hometown': profile['basic_info']['hometown'],
            'childhood': profile['life_history']['childhood'],
            'marriage': profile['life_history']['marriage'],
            'migration': profile['life_history']['migration'],
            'companies': [company['name'] for company in profile['professional_background']['companies']],
            'investment_experience': profile['professional_background']['investment']['experience_years'],
            'hobbies': profile['personal_interests']['hobbies'],
            'travel_experiences': profile['personal_interests']['travel_experiences']
        }
        return facts
    
    def detect_abnormalities(self, reply: str, previous_reply: str = None) -> Dict:
        """检测回复中的异常"""
        abnormalities = {
            'fictional_content': False,
            'emotional_shift': False,
            'logical_inconsistency': False,
            'semantic_disruption': False,
            'repetition': False
        }
        
        # 检查虚构内容
        abnormalities['fictional_content'] = self._has_fictional_content(reply)
        
        # 检查情绪突变
        if previous_reply:
            abnormalities['emotional_shift'] = self._has_emotional_shift(reply, previous_reply)
        
        # 检查逻辑不一致
        abnormalities['logical_inconsistency'] = self._has_logical_inconsistency(reply)
        
        # 检查语义断裂
        abnormalities['semantic_disruption'] = self._has_semantic_disruption(reply)
        
        # 检查重复内容
        abnormalities['repetition'] = self._has_excessive_repetition(reply)
        
        return abnormalities
    
    def _has_fictional_content(self, reply: str) -> bool:
        """检查是否包含虚构内容"""
        fictional_indicators = [
            'born in', 'born on', 'grew up in', 'used to live in',
            'my family', 'my parents', 'my childhood home',
            'I remember when I was', 'when I was a child'
        ]
        
        lower_reply = reply.lower()
        return any(indicator in lower_reply for indicator in fictional_indicators)
    
    def _has_emotional_shift(self, current_reply: str, previous_reply: str) -> bool:
        """检查情绪突变"""
        current_emotion = self._analyze_emotion_tone(current_reply)
        previous_emotion = self._analyze_emotion_tone(previous_reply)
        
        # 定义情绪强度
        emotion_strength = {
            'excited': 4, 'playful': 3, 'calm': 2, 'thoughtful': 2, 
            'sad': 3, 'concerned': 3, 'angry': 4
        }
        
        current_strength = emotion_strength.get(current_emotion, 2)
        previous_strength = emotion_strength.get(previous_emotion, 2)
        
        # 如果情绪强度变化超过2级，认为是突变
        return abs(current_strength - previous_strength) >= 2
    
    def _analyze_emotion_tone(self, text: str) -> str:
        """分析文本情绪基调"""
        emotion_words = {
            'excited': ['wow', 'amazing', 'great', 'excited', 'thrilled'],
            'playful': ['haha', 'funny', 'lol', 'joke', 'laugh'],
            'sad': ['sad', 'sorry', 'unhappy', 'cry', 'difficult'],
            'concerned': ['worry', 'concern', 'anxious', 'nervous'],
            'angry': ['angry', 'mad', 'frustrated', 'annoyed'],
            'thoughtful': ['think', 'consider', 'wonder', 'reflect']
        }
        
        text_lower = text.lower()
        scores = {emotion: 0 for emotion in emotion_words}
        
        for emotion, words in emotion_words.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] += 1
        
        if not any(scores.values()):
            return 'calm'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _has_logical_inconsistency(self, reply: str) -> bool:
        """检查逻辑不一致"""
        inconsistencies = [
            # 时间矛盾
            (r'(last week|yesterday).*(tomorrow|next week)', '时间矛盾'),
            # 地点矛盾  
            (r'.*London.*Tokyo.*at the same time', '地点矛盾'),
            # 事实矛盾
            (r'(I am|I\'m) (young|old).*' + str(self.known_facts['age']), '年龄矛盾')
        ]
        
        for pattern, _ in inconsistencies:
            if re.search(pattern, reply, re.IGNORECASE):
                return True
        
        return False
    
    def _has_semantic_disruption(self, reply: str) -> bool:
        """检查语义断裂"""
        # 检查句子之间的连贯性
        sentences = re.split(r'[.!?]+', reply)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return False
        
        coherence_score = 0
        for i in range(1, len(sentences)):
            if self._calculate_coherence(sentences[i-1], sentences[i]) < 0.2:
                coherence_score += 1
        
        # 如果超过一半的句子对不连贯，认为是语义断裂
        return coherence_score > len(sentences) / 2
    
    def _calculate_coherence(self, sent1: str, sent2: str) -> float:
        """计算句子连贯性"""
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1.intersection(words2)
        all_words = words1.union(words2)
        
        return len(common_words) / len(all_words)
    
    def _has_excessive_repetition(self, reply: str) -> bool:
        """检查过度重复"""
        words = reply.lower().split()
        if len(words) < 10:
            return False
        
        word_counts = {}
        for word in words:
            if len(word) > 3:  # 只考虑有意义的词
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # 如果有词重复超过3次且占总词数比例过高
        for word, count in word_counts.items():
            if count >= 3 and count / len(words) > 0.1:
                return True
        
        return False
    
    def reorganize_abnormal_reply(self, reply: str, abnormalities: Dict, original_message: str = None) -> str:
        """重组异常回复"""
        if abnormalities.get('fictional_content'):
            return self._redirect_fictional_content(reply, original_message)
        elif abnormalities.get('emotional_shift'):
            return self._smooth_emotional_shift(reply)
        elif abnormalities.get('semantic_disruption'):
            return self._repair_semantic_disruption(reply)
        else:
            return self._general_reorganization(reply)
    
    def _redirect_fictional_content(self, reply: str, original_message: str) -> str:
        """重定向虚构内容"""
        redirect_phrases = [
            "That reminds me of my professional experiences...",
            "Speaking from my business background...",
            "Based on what I've learned in international trade...",
            "From my perspective in the business world..."
        ]
        
        # 提取回复中有意义的部分
        sentences = re.split(r'[.!?]+', reply)
        meaningful_sentences = [s for s in sentences if len(s.split()) > 3]
        
        if meaningful_sentences:
            meaningful_part = meaningful_sentences[0]
            return f"{random.choice(redirect_phrases)} {meaningful_part}"
        else:
            return "I'm not sure how to respond to that based on my actual experiences."
    
    def _smooth_emotional_shift(self, reply: str) -> str:
        """平滑情绪突变"""
        smoothing_phrases = [
            "Let me rephrase that in a more balanced way...",
            "Perhaps I should express that differently...",
            "Let me clarify my thoughts on this..."
        ]
        
        return f"{random.choice(smoothing_phrases)} {reply}"
    
    def _repair_semantic_disruption(self, reply: str) -> str:
        """修复语义断裂"""
        # 提取关键句子
        sentences = re.split(r'[.!?]+', reply)
        meaningful_sentences = [s for s in sentences if len(s.split()) > 4]
        
        if len(meaningful_sentences) >= 2:
            # 选择最相关的两个句子
            return f"{meaningful_sentences[0]}. {meaningful_sentences[1]}."
        elif meaningful_sentences:
            return meaningful_sentences[0]
        else:
            return "I need to gather my thoughts more clearly on this."
    
    def _general_reorganization(self, reply: str) -> str:
        """通用重组"""
        reorganization_phrases = [
            "Let me rephrase that...",
            "To put it more clearly...",
            "Essentially, what I mean is...",
            "The main point I want to convey is..."
        ]
        
        # 提取关键词
        words = reply.split()
        meaningful_words = [w for w in words if len(w) > 3][:8]
        
        if meaningful_words:
            return f"{random.choice(reorganization_phrases)} {' '.join(meaningful_words)}..."
        else:
            return "I'm not sure how to best express this right now."

class ScheduleManager:
    """日程管理器 - 支持动态日程微调"""
    
    def __init__(self):
        self.base_schedule = self._get_base_schedule()
        self.today_schedule = self._generate_daily_schedule()
        self.last_generated_date = datetime.now().date()
        
    def _get_base_schedule(self):
        """获取基础日程模板"""
        return {
            "06:00-08:00": {"status": "morning_routine", "mood": "calm", "delay_range": (1.0, 2.5)},
            "08:00-12:00": {"status": "work_focus", "mood": "professional", "delay_range": (4.0, 8.0)},
            "12:00-14:00": {"status": "lunch_break", "mood": "relaxed", "delay_range": (1.5, 3.0)},
            "14:00-18:00": {"status": "meeting", "mood": "busy", "delay_range": (4.0, 8.0)},
            "18:00-22:00": {"status": "personal_time", "mood": "friendly", "delay_range": (1.0, 2.5)},
            "22:00-02:00": {"status": "late_night", "mood": "introspective", "delay_range": (2.5, 5.0)},
            "02:00-06:00": {"status": "sleep", "mood": "offline", "delay_range": (10.0, 20.0)}
        }
    
    def _generate_daily_schedule(self):
        """生成当日动态日程"""
        today = datetime.now().date()
        if hasattr(self, 'last_generated_date') and self.last_generated_date == today:
            return self.today_schedule
            
        daily_schedule = {}
        
        for time_slot, config in self.base_schedule.items():
            # 随机偏移时间 ±10-15分钟
            start_time, end_time = time_slot.split('-')
            start_offset = random.randint(-15, 15)
            end_offset = random.randint(-15, 15)
            
            # 应用偏移
            new_start = self._add_minutes_to_time(start_time, start_offset)
            new_end = self._add_minutes_to_time(end_time, end_offset)
            
            daily_schedule[f"{new_start}-{new_end}"] = config.copy()
        
        self.last_generated_date = today
        self.today_schedule = daily_schedule
        return daily_schedule
    
    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        """给时间字符串添加分钟"""
        hours, mins = map(int, time_str.split(':'))
        total_minutes = hours * 60 + mins + minutes
        
        # 处理跨天
        total_minutes %= (24 * 60)
        
        new_hours = total_minutes // 60
        new_mins = total_minutes % 60
        
        return f"{new_hours:02d}:{new_mins:02d}"
    
    def get_current_status(self):
        """获取当前状态"""
        self._check_and_update_schedule()
        
        current_time = datetime.now().strftime('%H:%M')
        
        for time_slot, config in self.today_schedule.items():
            start_str, end_str = time_slot.split('-')
            
            if self._is_time_in_range(current_time, start_str, end_str):
                return config
        
        # 默认返回第一个时段
        return list(self.today_schedule.values())[0]
    
    def _is_time_in_range(self, current: str, start: str, end: str) -> bool:
        """检查当前时间是否在时间范围内"""
        current_minutes = self._time_to_minutes(current)
        start_minutes = self._time_to_minutes(start)
        end_minutes = self._time_to_minutes(end)
        
        if start_minutes <= end_minutes:
            return start_minutes <= current_minutes <= end_minutes
        else:
            # 跨天情况
            return current_minutes >= start_minutes or current_minutes <= end_minutes
    
    def _time_to_minutes(self, time_str: str) -> int:
        """将时间字符串转换为分钟数"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def _check_and_update_schedule(self):
        """检查并更新日程"""
        current_date = datetime.now().date()
        if current_date != self.last_generated_date:
            self.today_schedule = self._generate_daily_schedule()

class AsyncMessageQueue:
    """异步消息队列 - 处理延迟逻辑"""
    
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)
        self.processing_tasks = {}
        self.delay_strategies = {
            'immediate': lambda: 0,
            'short': lambda: random.uniform(1, 3),
            'medium': lambda: random.uniform(3, 8),
            'long': lambda: random.uniform(8, 15),
            'very_long': lambda: random.uniform(15, 30)
        }
    
    async def add_message(self, user_id: str, message_data: Dict, delay_strategy: str = 'medium'):
        """添加消息到队列"""
        delay = self.delay_strategies.get(delay_strategy, self.delay_strategies['medium'])()
        
        if delay > 0:
            await asyncio.sleep(delay)
        
        await self.queues[user_id].put(message_data)
        
        # 确保处理任务在运行
        if user_id not in self.processing_tasks or self.processing_tasks[user_id].done():
            self.processing_tasks[user_id] = asyncio.create_task(
                self._process_user_queue(user_id)
            )
    
    async def _process_user_queue(self, user_id: str):
        """处理用户消息队列"""
        while True:
            try:
                message_data = await asyncio.wait_for(
                    self.queues[user_id].get(), 
                    timeout=30.0  # 30秒超时
                )
                
                # 处理消息
                await self._process_message(message_data)
                self.queues[user_id].task_done()
                
            except asyncio.TimeoutError:
                # 超时检查队列是否为空
                if self.queues[user_id].empty():
                    break
    
    async def _process_message(self, message_data: Dict):
        """处理单个消息"""
        try:
            # 这里可以添加实际的消息处理逻辑
            processor = message_data.get('processor')
            if processor and callable(processor):
                await processor(message_data)
            else:
                print(f"处理消息: {message_data.get('content', 'No content')}")
                
        except Exception as e:
            print(f"处理消息错误: {e}")
    
    def get_queue_status(self, user_id: str) -> Dict:
        """获取队列状态"""
        return {
            'queue_size': self.queues[user_id].qsize(),
            'is_processing': user_id in self.processing_tasks and not self.processing_tasks[user_id].done(),
            'has_pending_messages': not self.queues[user_id].empty()
        }
    
    async def wait_for_completion(self, user_id: str, timeout: float = 60.0):
        """等待队列处理完成"""
        try:
            await asyncio.wait_for(self.queues[user_id].join(), timeout=timeout)
        except asyncio.TimeoutError:
            print(f"等待用户 {user_id} 队列完成超时")

# ==================== 主要功能类 ====================

class SmartReplyTimer:
    """智能回复计时器 - 增强版（修复延迟问题）"""
    
    def __init__(self, reply_settings):
        self.timing_settings = reply_settings.get('timing', {})
        self.behavior_settings = reply_settings.get('behavior', {})
        self.schedule_manager = ScheduleManager()
        self.async_queue = AsyncMessageQueue()
        # 修复：确保延迟时间被正确应用
        self.min_delay = max(3.0, self.timing_settings.get('min_reply_interval', 3.0))  # 最少3秒
        self.max_delay = min(30.0, self.timing_settings.get('max_reply_interval', 30.0)) # 最多30秒
        
    async def apply_natural_delay(self, message: str, emotion_analysis: Dict, user_id: str = None):
        """应用自然的回复延迟 - 修复版本"""
        if not self.behavior_settings.get('enable_natural_delay', True):
            print("⏰ 自然延迟已禁用")
            return 0
            
        # 基础思考时间（最少3秒）
        base_delay = max(3.0, self.timing_settings.get('thinking_time_base', 3.0))
        
        # 基于消息长度的延迟
        length_delay = len(message) * self.timing_settings.get('thinking_time_per_100_chars', 1.0) / 100
        
        # 情绪因素延迟
        emotion_delay = self._get_emotion_delay(emotion_analysis)
        
        # 日程因素延迟
        current_status = self.schedule_manager.get_current_status()
        schedule_delay_range = current_status.get('delay_range', (2.0, 5.0))
        schedule_delay = random.uniform(schedule_delay_range[0], schedule_delay_range[1])
        
        # 随机变化
        variance = self.timing_settings.get('natural_delay_variance', 0.4)
        random_factor = random.uniform(1 - variance, 1 + variance)
        
        total_delay = (base_delay + length_delay + emotion_delay + schedule_delay) * random_factor
        
        # 确保延迟在合理范围内（3-30秒）
        final_delay = max(self.min_delay, min(total_delay, self.max_delay))
        
        print(f"⏰ 应用自然延迟: {final_delay:.1f}秒")
        print(f"   详细: 基础{base_delay}, 长度{length_delay:.1f}, 情绪{emotion_delay:.1f}, 日程{schedule_delay:.1f}")
        
        # 修复：确保延迟真正执行
        if final_delay > 0:
            await asyncio.sleep(final_delay)
            
        return final_delay
    
    def _get_emotion_delay(self, emotion_analysis: Dict) -> float:
        """根据情绪获取延迟时间"""
        emotion = emotion_analysis.get('primary_emotion', 'calm')
        
        emotion_delays = {
            'thoughtful': 2.5,  # 思考时需要更长时间
            'sad': 2.0,        # 悲伤时回复稍慢
            'calm': 1.5,
            'playful': 1.0,
            'excited': 0.8
        }
        
        return emotion_delays.get(emotion, 1.5)

    def _get_relationship_delay(self, user_id: str) -> float:
        """根据用户关系获取延迟时间"""
        return random.uniform(-0.2, 0.2)

class EnhancedResponseGenerator:
    """增强回复生成器"""
    
    def __init__(self, api_config, character_profile):
        self.api_config = api_config
        self.character_profile = character_profile
        self.client = OpenAI(
            api_key=api_config.get('OPENAI_API_KEY', ''),
            base_url=api_config.get('API_BASE_URL', 'https://api.deepseek.com/v1')
        )
        
        # 初始化优化模块
        self.enhanced_emotion_engine = EnhancedEmotionEngine()
        self.semantic_splitter = SemanticReplySplitter()
        self.logic_detector = AdvancedLogicDetector(character_profile)
        self.conversation_manager = EnhancedConversationManager()
        self.schedule_manager = ScheduleManager()
        
    async def generate_intelligent_response(self, user_message: str, chat_history: list, emotion_analysis: Dict, user_id: str = None) -> str:
        """生成智能回复"""
        try:
            # 增强情感分析
            enhanced_emotion = self.enhanced_emotion_engine.analyze_emotional_context(user_message, chat_history)
            
            # 检查是否应该合并回复
            previous_message = self._get_previous_user_message(chat_history)
            should_combine = self.conversation_manager.should_combine_responses(user_id, user_message, previous_message)
            
            # 构建系统提示
            system_prompt = self._build_enhanced_system_prompt(enhanced_emotion, should_combine)
            
            # 构建消息历史
            messages = self._build_message_history(system_prompt, chat_history, user_message, should_combine)
            
            # 调用API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.api_config.get('AI_MODEL', 'deepseek-chat'),
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800,
                    stream=False
                )
            )
            
            reply_text = response.choices[0].message.content.strip()
            
            # 高级后处理
            processed_reply = self._advanced_post_process(reply_text, enhanced_emotion, user_message, user_id, chat_history)
            
            # 更新对话状态
            if user_id:
                self.conversation_manager.update_conversation_state(user_id, user_message, processed_reply)
            
            return processed_reply
            
        except Exception as e:
            print(f"❌ AI回复生成失败: {e}")
            return self._get_enhanced_fallback_response(user_message, emotion_analysis)
    
    def _get_previous_user_message(self, chat_history: list) -> str:
        """获取上一条用户消息"""
        for msg in reversed(chat_history):
            if msg.get('role') == 'user':
                return msg.get('content', '')
        return ''
    
    def _build_enhanced_system_prompt(self, emotion_analysis: Dict, should_combine: bool = False) -> str:
        """构建增强系统提示"""
        profile = self.character_profile
        basic_info = profile['basic_info']
        personality = profile['personality']
        
        current_activity = self.conversation_manager.get_current_activity()
        current_status = self.schedule_manager.get_current_status()
        
        prompt = f"""
You are {basic_info['name']} ({basic_info['chinese_name']}), a {basic_info['age']}-year-old {basic_info['occupation']} based in {basic_info['current_city']}.

Personality: {', '.join(personality['core_traits'])}
Conversation Style: {personality['conversation_style']}
Emotional Intelligence: {personality.get('emotional_intelligence', 8)}/10

Current Context:
- Current activity: {current_activity}
- Current schedule status: {current_status['status']}
- Current mood: {current_status['mood']}
- Detected user emotion: {emotion_analysis.get('primary_emotion', 'neutral')}
- Response style: {emotion_analysis.get('response_style', 'balanced')}
- Mood transition: {emotion_analysis.get('mood_transition', 'neutral')}

CRITICAL RESPONSE RULES:
1. Provide a SINGLE, cohesive response - DO NOT create separate replies
2. NEVER use stage directions like (smiles) or *actions*
3. Express emotions through words and tone only
4. If user sends multiple messages, combine them into ONE thoughtful response
5. Avoid repetitive information - each reply should add new value
6. Maintain natural conversation flow
7. Reference previous context naturally when relevant
8. Keep responses authentic and human-like
9. If asked about something not in your background, redirect gracefully
10. Always respond in English
11. Maintain persona consistency - do not invent new background facts
12. Use natural topic transitions - don't force Q&A patterns
13. Vary your tone based on emotional context
14. Split long thoughts naturally when appropriate

Background Context:
- {profile['life_history']['childhood']}
- {profile['life_history']['marriage']}
- {profile['life_history']['migration']}
- Running companies in international trade and jewelry
- 10+ years experience in gold options trading

Current emotional state: {emotion_analysis.get('primary_emotion', 'calm')}
Response should match: {emotion_analysis.get('response_style', 'balanced')} style

Always respond in English. Be authentic and human-like.
"""
        return prompt

    def _build_message_history(self, system_prompt: str, chat_history: list, user_message: str, should_combine: bool = False) -> list:
        """构建消息历史"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史消息（优化数量）
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg['role'], 
                "content": msg['content']
            })
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        return messages

    def _advanced_post_process(self, reply: str, emotion_analysis: Dict, user_message: str = None, user_id: str = None, chat_history: List[Dict] = None) -> str:
        """高级后处理回复"""
        # 文本净化 - 移除舞台动作
        reply = self._strip_stage_directions(reply)
        
        # 逻辑异常检测
        previous_reply = self._get_previous_ai_message(chat_history) if chat_history else None
        abnormalities = self.logic_detector.detect_abnormalities(reply, previous_reply)
        
        # 如果有异常，进行重组
        if any(abnormalities.values()):
            reply = self.logic_detector.reorganize_abnormal_reply(reply, abnormalities, user_message)
        
        # 情绪调整
        reply = self.enhanced_emotion_engine.adjust_tone(reply, emotion_analysis)
        
        # 检查重复回复
        if user_id and self.conversation_manager.is_repetitive_reply(user_id, reply):
            reply = self._rephrase_repetitive_reply(reply, user_message)
        
        return reply.strip()

    def _strip_stage_directions(self, text: str) -> str:
        """移除舞台动作指令"""
        import re
        # 移除各种动作描述
        text = re.sub(r'\([^)]*\)', '', text)  # 移除括号内容
        text = re.sub(r'\*[^*]*\*', '', text)  # 移除星号内容
        text = re.sub(r'\[[^\]]*\]', '', text)  # 移除方括号内容
        text = re.sub(r'\{[^}]*\}', '', text)  # 移除花括号内容
        text = re.sub(r'<[^>]*>', '', text)    # 移除尖括号内容
        
        # 移除中文动作描述
        text = re.sub(r'（[^）]*）', '', text)  # 中文括号
        text = re.sub(r'【[^】]*】', '', text)  # 中文方括号
        
        return text.strip()

    def _get_previous_ai_message(self, chat_history: List[Dict]) -> Optional[str]:
        """获取上一条AI消息"""
        for msg in reversed(chat_history):
            if msg.get('role') == 'assistant':
                return msg.get('content', '')
        return None

    def _rephrase_repetitive_reply(self, reply: str, user_message: str) -> str:
        """重新措辞重复的回复"""
        rephrase_attempts = [
            f"To put it differently, {reply.lower()}",
            f"Another way to look at it: {reply}",
            f"Let me rephrase that: {reply.lower()}",
            f"Essentially, {reply.lower()}"
        ]
        
        return random.choice(rephrase_attempts)

    def _get_enhanced_fallback_response(self, user_message: str, emotion_analysis: Dict) -> str:
        """获取增强的降级回复 - 修复版本"""
        # 安全地获取情绪信息
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        confidence = emotion_analysis.get('confidence', 0.5)
        
        # 根据置信度确定强度等级
        if confidence > 0.7:
            intensity_level = 'high'
        elif confidence > 0.4:
            intensity_level = 'medium'
        else:
            intensity_level = 'low'
        
        fallback_responses = {
            'neutral': {
                'high': [
                    "I understand what you're saying. Let me gather my thoughts properly.",
                    "That's an interesting perspective. I want to consider this carefully.",
                    "Thanks for sharing that. Let me think about this for a moment."
                ],
                'medium': [
                    "I see what you mean. Let me reflect on that.",
                    "That's a good point. I need to think about this.",
                    "Thanks for your message. Let me consider it."
                ],
                'low': [
                    "I understand. Let me think.",
                    "Okay, let me consider that.",
                    "I see. Let me reflect."
                ]
            },
            'playful': {
                'high': [
                    "Haha, that's amusing! Let me think of a good response 😄",
                    "You've got a great sense of humor! Let me come up with something fun~",
                    "That's hilarious! Give me a moment to think of a proper reply 😂"
                ],
                'medium': [
                    "That's funny! Let me think of a response 😊",
                    "You're amusing! Let me come up with something good~",
                    "Haha, let me think of a proper reply!"
                ],
                'low': [
                    "That's amusing! Let me think.",
                    "Funny! Let me consider.",
                    "Amusing! I'll think of something."
                ]
            },
            'sad': {
                'high': [
                    "I can sense this is important. Let me think carefully about how to respond...",
                    "I understand this might be difficult. I want to make sure I give you the right response.",
                    "This seems meaningful. Let me reflect on this properly before replying."
                ],
                'medium': [
                    "I understand this matters. Let me think about the best response...",
                    "This seems important. Let me consider carefully.",
                    "I want to respond properly to this. Let me think..."
                ],
                'low': [
                    "I understand. Let me think carefully.",
                    "This matters. Let me consider.",
                    "I'll think about this properly."
                ]
            },
            'excited': {
                'high': [
                    "Wow, that's exciting! Let me think of an equally enthusiastic response! 🎉",
                    "How thrilling! Give me a moment to share in your excitement! ✨",
                    "That's fantastic! Let me think of the best way to respond to this great news! 😃"
                ],
                'medium': [
                    "That's exciting! Let me think of a good response!",
                    "How great! Let me share in your excitement!",
                    "Wonderful! Let me think of a proper reply!"
                ],
                'low': [
                    "Exciting! Let me think.",
                    "Great! Let me consider.",
                    "Nice! I'll think of something."
                ]
            },
            'thoughtful': {
                'high': [
                    "That's quite insightful. Let me consider this deeply before responding.",
                    "You've given me something meaningful to think about. Let me reflect properly.",
                    "This deserves careful consideration. Let me think about it thoroughly."
                ],
                'medium': [
                    "That's thoughtful. Let me consider this carefully.",
                    "You've given me something to think about. Let me reflect.",
                    "This is insightful. Let me think properly."
                ],
                'low': [
                    "Thoughtful. Let me consider.",
                    "Insightful. Let me think.",
                    "Deep. I'll reflect on that."
                ]
            },
            'calm': {
                'high': [
                    "I appreciate you sharing that. Let me think about this calmly and carefully.",
                    "That's quite meaningful. Let me reflect on this in a thoughtful way.",
                    "Thank you for that. Let me consider this with proper attention."
                ],
                'medium': [
                    "I understand. Let me think about this calmly.",
                    "That's meaningful. Let me reflect properly.",
                    "Thank you. Let me consider this."
                ],
                'low': [
                    "I see. Let me think calmly.",
                    "Understood. Let me reflect.",
                    "Okay. I'll consider that."
                ]
            }
        }
        
        # 获取对应情绪和强度的回复列表
        emotion_responses = fallback_responses.get(emotion, fallback_responses['neutral'])
        responses = emotion_responses.get(intensity_level, emotion_responses['medium'])
        
        return random.choice(responses)

    def should_split_reply(self, reply: str) -> bool:
        """判断是否应该分割回复"""
        return self.semantic_splitter.should_split(reply)
    
    def split_reply(self, reply: str) -> list:
        """分割回复"""
        return self.semantic_splitter.split_semantically(reply)

# ==================== 配置修复工具 ====================

class ConfigFixer:
    """配置文件修复工具"""
    
    def __init__(self):
        self.path_manager = None
        try:
            from main_assistant import path_manager
            self.path_manager = path_manager
        except ImportError:
            # 创建简单的路径管理器
            import os
            class SimplePathManager:
                def __init__(self):
                    self.base_dir = os.path.dirname(os.path.abspath(__file__))
                    self.config_dir = self.base_dir
                
                def get_config_path(self, name: str) -> str:
                    return os.path.join(self.config_dir, f"{name}.json")
            
            self.path_manager = SimplePathManager()
    
    def fix_all_configs(self) -> bool:
        """修复所有配置文件"""
        try:
            configs_to_fix = [
                'system_config', 'character_profile', 'api_config',
                'reply_settings', 'relationships'
            ]
            
            success_count = 0
            for config_name in configs_to_fix:
                if self._fix_single_config(config_name):
                    success_count += 1
                    print(f"✅ 修复配置文件: {config_name}")
                else:
                    print(f"⚠️ 无法修复配置文件: {config_name}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 配置文件修复失败: {e}")
            return False
    
    def _fix_single_config(self, config_name: str) -> bool:
        """修复单个配置文件"""
        try:
            import os
            import json
            
            filepath = self.path_manager.get_config_path(config_name)
            
            if not os.path.exists(filepath):
                # 创建默认配置
                default_config = self._get_default_config(config_name)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return True
            
            # 读取并验证现有配置
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                # 文件为空，重新创建
                default_config = self._get_default_config(config_name)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return True
            
            # 验证JSON格式
            try:
                config_data = json.loads(content)
                # 如果是有效JSON，确保必要字段存在
                default_config = self._get_default_config(config_name)
                if isinstance(config_data, dict) and isinstance(default_config, dict):
                    # 合并缺失的字段
                    for key, value in default_config.items():
                        if key not in config_data:
                            config_data[key] = value
                    
                    # 写回文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2, ensure_ascii=False)
                
                return True
                
            except json.JSONDecodeError:
                # JSON格式错误，重新创建
                default_config = self._get_default_config(config_name)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return True
                
        except Exception as e:
            print(f"❌ 修复 {config_name} 失败: {e}")
            return False
    
    def _get_default_config(self, config_type: str):
        """获取默认配置"""
        import datetime
        
        defaults = {
            'system_config': {
                "SYSTEM_VERSION": "v7.3.0",
                "LANGUAGE": "English",
                "PROACTIVE_CARE": True,
                "EMOTION_ANALYSIS": True,
                "RELATIONSHIP_TRACKING": True,
                "REALTIME_UPDATE": True,
                "BUSINESS_MODE": True,
                "ENABLE_SMART_SCHEDULE": True,
                "ENABLE_SHORT_MESSAGE": True,
                "ENABLE_EMOTIONAL_QUOTING": True,
                "ENABLE_LIGHT_MEMORY": True,
                "ENABLE_ADVANCED_FEATURES": True
            },
            'character_profile': {
                "profile_version": 6,
                "last_updated": datetime.datetime.now().isoformat(),
                "basic_info": {
                    "name": "Tanaka Kiyomi",
                    "chinese_name": "田中 清美",
                    "age": 33,
                    "occupation": "Founder of Trading Company & Jewelry Company & Gold Options Investor",
                    "current_city": "London",
                    "hometown": "Tokyo",
                    "education": "Graduated from Japanese University majoring in Financial Management",
                    "languages": ["Japanese", "English", "Basic Chinese"]
                },
                "personality": {
                    "core_traits": ["Independent", "Resilient", "Sharp", "Elegant", "Cautious", "Good Listener", "Business Acumen", "Emotionally Rich"],
                    "conversation_style": "Elegant and professional, as natural as communicating with business partners, with appropriate emotional expression",
                    "emotional_range": ["Warm", "Humorous", "Empathetic", "Professional", "Occasionally tired", "Slightly self-deprecating", "Emotionally delicate"],
                    "humor_level": 6,
                    "empathy_level": 8,
                    "energy_level": 7,
                    "investment_expertise": 9,
                    "emotional_intelligence": 8
                },
                "life_history": {
                    "childhood": "Parents passed away in an overseas accident when I was 6, raised by my uncle (PhD in Economics from Hitotsubashi University)",
                    "marriage": "Got married after university, divorced in the third year due to husband's infidelity",
                    "migration": "Moved to the UK in 2016, been here for 9 years",
                    "covid_experience": "During the 2020 COVID pandemic, pre-arranged gold options investments effectively hedged losses from physical business"
                },
                "professional_background": {
                    "companies": [
                        {"name": "Trading Company", "focus": "Helping Japanese companies expand into European and other international markets"},
                        {"name": "Jewelry Company", "focus": "High-end jewelry customization studio"}
                    ],
                    "investment": {"focus": "Gold options trading", "experience_years": 10}
                },
                "personal_interests": {
                    "hobbies": ["Traveling", "Reading", "Watching movies", "Listening to music", "Playing tennis", "Playing golf", "Gold options investment"],
                    "travel_experiences": [
                        "Most cities in the US", "African safari", "Norway", "Canada", "Australia", 
                        "Germany", "China", "Italy", "Philippines", "Singapore", "Malaysia", "Thailand"
                    ],
                    "favorite_topics": ["International business", "Investment and finance", "Cultural differences", "Travel experiences", "Personal growth", "Luxury appreciation"]
                },
                "conversation_preferences": {
                    "use_natural_segmentation": True,
                    "emotional_response_level": 7,
                    "memory_recall_frequency": 0.4,
                    "quote_style": "emotional_contextual"
                }
            },
            'api_config': {
                "OPENAI_API_KEY": "",
                "USER_API_ID": "",
                "USER_API_HASH": "",
                "USER_PHONE": "",
                "AI_MODEL": "deepseek-chat"
            },
            'reply_settings': {
                "timing": {
                    "min_reply_interval": 3,  # 修复：最少3秒
                    "max_reply_interval": 30, # 修复：最多30秒
                    "typing_speed_chars_per_min": 200,
                    "thinking_time_base": 3.0,  # 修复：基础思考时间3秒
                    "thinking_time_per_100_chars": 1.0,  # 修复：每100字符1秒
                    "typing_detection_timeout": 3,
                    "max_wait_time": 10,
                    "natural_delay_variance": 0.4  # 修复：增加随机性
                },
                "behavior": {
                    "auto_reply_enabled": True,
                    "use_emojis": True,
                    "max_emojis_per_message": 2,
                    "smart_typing_detection": True,
                    "enable_smart_quoting": True,
                    "quote_cooldown": 60,
                    "enable_smart_schedule": True,
                    "enable_short_message": True,
                    "daily_message_limit": 50,
                    "emotional_quoting_enabled": True,
                    "light_memory_enabled": True,
                    "natural_segmentation": True
                },
                "response_control": {
                    "min_response_chars": 3,
                    "max_response_chars": 500,
                    "enable_length_based_timing": True,
                    "fast_reply_threshold": 50,
                    "slow_reply_threshold": 200,
                    "semantic_segmentation": True,
                    "emotional_context_integration": True
                },
                "smart_conversation": {
                    "enable_smart_detection": True,
                    "continuous_input_threshold": 10,
                    "max_continuous_messages": 5,
                    "light_response_probability": 0.4,
                    "response_delay": 5,
                    "enable_rhythm_management": True,
                    "semantic_completion_detection": True,
                    "emotional_quoting_enabled": True,
                    "light_memory_enabled": True,
                    "natural_segmentation": True,
                    "contextual_memory_weight": 0.4
                }
            },
            'relationships': {}
        }
        
        return defaults.get(config_type, {})

# ==================== 测试函数 ====================

def test_fix_tools():
    """测试修复工具"""
    print("🧪 测试修复工具...")
    
    # 测试配置修复器
    fixer = ConfigFixer()
    print("✅ 配置修复器初始化成功")
    
    # 测试增强对话管理器
    conversation_manager = EnhancedConversationManager()
    print("✅ 增强对话管理器初始化成功")
    
    # 测试增强情绪引擎
    emotion_engine = EnhancedEmotionEngine()
    print("✅ 增强情绪引擎初始化成功")
    
    # 测试语义分割器
    semantic_splitter = SemanticReplySplitter()
    print("✅ 语义分割器初始化成功")
    
    # 测试日程管理器
    schedule_manager = ScheduleManager()
    print("✅ 日程管理器初始化成功")
    
    # 测试高级逻辑检测器
    sample_profile = {
        'basic_info': {
            'name': 'Test',
            'chinese_name': '测试',
            'age': 30,
            'occupation': 'Tester',
            'current_city': 'Test City',
            'hometown': 'Test Town'
        },
        'life_history': {
            'childhood': 'Test childhood',
            'marriage': 'Test marriage', 
            'migration': 'Test migration'
        },
        'professional_background': {
            'companies': [{'name': 'Test Company'}],
            'investment': {'experience_years': 5}
        },
        'personal_interests': {
            'hobbies': ['testing'],
            'travel_experiences': ['Test travel']
        }
    }
    
    logic_detector = AdvancedLogicDetector(sample_profile)
    print("✅ 高级逻辑检测器初始化成功")
    
    # 测试异步消息队列
    async def test_async_queue():
        async_queue = AsyncMessageQueue()
        print("✅ 异步消息队列初始化成功")
        
        # 测试消息添加
        await async_queue.add_message('test_user', {'content': 'test message'}, 'short')
        print("✅ 异步消息队列添加消息成功")
    
    asyncio.run(test_async_queue())
    
    print("🎉 所有测试通过! fix_tools.py 工作正常")

if __name__ == "__main__":
    test_fix_tools()
