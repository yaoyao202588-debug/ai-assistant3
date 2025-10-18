# -*- coding: utf-8 -*-
# main_assistant.py - 完整优化修复版（修复延迟和分段发送问题）

# 确保输出编码为UTF-8（解决ASCII编码错误）
import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except AttributeError:
        pass  # 在某些环境下可能没有buffer属性
        
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except AttributeError:
        pass

import asyncio
import os
import re
import json
import aiofiles
import random
import time
from openai import OpenAI
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict, deque
from telethon import TelegramClient, events
from telethon.tl.types import Message

# 导入新的核心模块
from core.intent_analyzer import DeepIntentAnalyzer
from core.emotion_engine import EmotionalIntelligenceEngine as CoreEmotionEngine
from core.prompt_builder import OptimizedPromptBuilder
from core.memory_system import ThreeTierMemorySystem
from core.personality_engine import PersonalityConsistencyEngine
from core.conversation_flow import NaturalConversationFlowEngine

# 导入原有工具模块
from utils import (
    EnhancedTextProcessor, 
    ConversationAnalyzer,
    PerformanceMonitor,
    ScheduleSimulator,
    MemoryManager,
    SemanticRhythmDetector,
    ContinuousInputProcessor,
    IntelligentResponseCoordinator,
    NaturalLanguageGenerator,
    SentenceStreamer
)
import aiohttp

# ==================== 修复的增强模块 ====================

class EnhancedStreamingController:
    """增强流式发送控制器 - 修复延迟和分段问题"""
    
    def __init__(self):
        self.sentence_streamer = SentenceStreamer()
        self.streaming_states = defaultdict(dict)
        
    async def send_response_with_natural_flow(self, reply: str, send_callback: Callable, 
                                            user_id: str = None, style: str = 'normal'):
        """以自然流程发送回复 - 修复版本"""
        if len(reply) <= 60:  # 短回复直接发送
            print(f"📤 发送短回复 ({len(reply)}字符)")
            await send_callback(reply, True)
            return [reply]
        
        # 长回复分段发送
        segments = self._split_into_natural_segments(reply)
        print(f"📝 分割为 {len(segments)} 个段落")
        
        sent_segments = []
        
        for i, segment in enumerate(segments):
            is_final = (i == len(segments) - 1)
            
            # 段落间延迟（第一段后开始）
            if i > 0:
                segment_delay = self._calculate_segment_delay(i, len(segments), style)
                print(f"⏳ 段落间延迟: {segment_delay:.1f}秒")
                await asyncio.sleep(segment_delay)
            
            # 模拟段落内打字效果
            typing_delay = self._calculate_typing_delay(segment, style)
            if typing_delay > 0.5:
                print(f"⌨️ 段落打字延迟: {typing_delay:.1f}秒")
                await asyncio.sleep(typing_delay)
            
            # 发送段落
            print(f"📤 发送段落 {i+1}/{len(segments)}: '{segment}'")
            await send_callback(segment, is_final)
            sent_segments.append(segment)
            
            # 最终段落后额外延迟
            if is_final:
                final_delay = random.uniform(0.5, 1.5)
                await asyncio.sleep(final_delay)
        
        return sent_segments
    
    def _split_into_natural_segments(self, text: str, max_segment_length: int = 80) -> List[str]:
        """将文本分割成自然段落"""
        if len(text) <= max_segment_length:
            return [text]
        
        # 按句子分割
        sentences = re.split(r'([。！？.!?])', text)
        segments = []
        current_segment = ""
        
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                sentence = sentences[i].strip()
                if i + 1 < len(sentences):
                    sentence += sentences[i+1]
                
                if not sentence:
                    continue
                
                # 如果当前段落加上新句子不会太长，就合并
                if len(current_segment + sentence) <= max_segment_length:
                    current_segment += sentence
                else:
                    # 当前段落已满，开始新段落
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = sentence
        
        if current_segment:
            segments.append(current_segment)
        
        # 如果分割后段落还是太长，强制分割
        if segments and len(segments[-1]) > max_segment_length * 1.5:
            last_segment = segments[-1]
            segments[-1] = last_segment[:max_segment_length]
            segments.append(last_segment[max_segment_length:])
        
        return segments if segments else [text]
    
    def _calculate_segment_delay(self, segment_index: int, total_segments: int, style: str) -> float:
        """计算段落间延迟"""
        base_delays = {
            'fast': (1.0, 2.0),
            'normal': (2.0, 4.0),
            'slow': (3.0, 6.0),
            'thinking': (4.0, 8.0)
        }
        
        base_range = base_delays.get(style, base_delays['normal'])
        base_delay = random.uniform(base_range[0], base_range[1])
        
        # 根据位置调整延迟
        if segment_index == 0:
            base_delay *= 0.8  # 第一段后延迟较短
        elif segment_index == total_segments - 2:
            base_delay *= 1.2  # 倒数第二段后稍长
        
        return max(1.0, base_delay)  # 最少1秒
    
    def _calculate_typing_delay(self, text: str, style: str) -> float:
        """计算打字延迟"""
        speeds = {
            'fast': 15,    # 字符/秒
            'normal': 10,  # 字符/秒  
            'slow': 6,     # 字符/秒
            'thinking': 4  # 字符/秒
        }
        
        chars_per_second = speeds.get(style, speeds['normal'])
        return len(text) / chars_per_second

class EnhancedQuoteManager:
    """修复版智能引用管理器 - 避免重复引用但保持所有功能"""
    
    def __init__(self):
        self.quote_cooldown = {}
        self.last_user_messages = defaultdict(lambda: deque(maxlen=5))
        self.last_ai_messages = defaultdict(lambda: deque(maxlen=5))
        self.conversation_topics = defaultdict(lambda: deque(maxlen=10))
        self.recent_quotes = defaultdict(lambda: deque(maxlen=3))
        self.processing_lock = defaultdict(bool)
        
    def should_quote(self, user_id: str, current_message: str, chat_history: List[Dict]) -> tuple:
        """判断是否应该引用 - 修复重复问题"""
        # 检查处理锁
        if self.processing_lock[user_id]:
            return False, None, None
            
        self.processing_lock[user_id] = True
        
        try:
            # 检查冷却时间
            if self._is_in_cooldown(user_id):
                return False, None, None
                
            # 避免频繁引用
            if len(self.recent_quotes[user_id]) >= 2:
                return False, None, None
                
            # 多种引用场景判断
            quote_scenarios = [
                self._should_quote_user_recent(user_id, current_message),
                self._should_quote_ai_previous(user_id, current_message, chat_history),
                self._should_quote_topic_continuation(user_id, current_message),
                self._should_quote_clarification(current_message),
                self._should_quote_emotional_continuation(current_message, chat_history)
            ]
            
            for should_quote, quote_type, quote_content in quote_scenarios:
                if should_quote:
                    # 检查是否与最近引用重复
                    if quote_content and self._is_recent_quote(user_id, quote_content):
                        continue
                        
                    self.quote_cooldown[user_id] = time.time()
                    if quote_content:
                        self.recent_quotes[user_id].append(quote_content)
                    return True, quote_type, quote_content
                    
            return False, None, None
            
        finally:
            self.processing_lock[user_id] = False
    
    def _should_quote_user_recent(self, user_id: str, current_message: str) -> tuple:
        """引用用户最近的消息"""
        if not self.last_user_messages[user_id]:
            return False, None, None
            
        last_user_msg = self.last_user_messages[user_id][-1]
        
        # 提高相似度阈值避免过度引用
        if self._calculate_similarity(current_message, last_user_msg) > 0.6:
            return True, "user_recent", last_user_msg
            
        return False, None, None
    
    def _should_quote_ai_previous(self, user_id: str, current_message: str, chat_history: List[Dict]) -> tuple:
        """引用AI自己之前的内容"""
        if not self.last_ai_messages[user_id]:
            return False, None, None
            
        # 从历史中找到AI的关键陈述
        ai_key_statements = self._extract_ai_key_statements(chat_history)
        
        for statement in ai_key_statements[-3:]:
            if self._is_related_to_statement(current_message, statement):
                return True, "ai_self", statement
                
        return False, None, None
    
    def _should_quote_topic_continuation(self, user_id: str, current_message: str) -> tuple:
        """话题延续引用"""
        if len(self.conversation_topics[user_id]) < 2:
            return False, None, None
            
        previous_topic = self.conversation_topics[user_id][-1]
        current_topic = self._extract_topic(current_message)
        
        if previous_topic and current_topic == previous_topic:
            return True, "topic_continue", previous_topic
            
        return False, None, None
    
    def _should_quote_clarification(self, current_message: str) -> tuple:
        """澄清请求引用"""
        clarification_indicators = [
            'what do you mean', '什么意思', 'explain', '解释',
            'you said', '你说', 'mention', '提到'
        ]
        
        if any(indicator in current_message.lower() for indicator in clarification_indicators):
            return True, "clarification", None
            
        return False, None, None
    
    def _should_quote_emotional_continuation(self, current_message: str, chat_history: List[Dict]) -> tuple:
        """情感延续引用"""
        emotional_continuations = [
            'but', 'however', 'though', '可是', '但是', '不过',
            'actually', '其实', 'really', '真的'
        ]
        
        if any(word in current_message.lower() for word in emotional_continuations):
            # 检查上一条消息的情感强度
            if chat_history and len(chat_history) >= 2:
                prev_msg = chat_history[-2]['content']
                if self._has_emotional_content(prev_msg):
                    return True, "emotional_continue", prev_msg
                    
        return False, None, None
    
    def _extract_ai_key_statements(self, chat_history: List[Dict]) -> List[str]:
        """从聊天历史中提取AI的关键陈述"""
        key_statements = []
        key_indicators = ['think', 'believe', 'feel', 'suggest', 'recommend', 'remember']
        
        for msg in chat_history:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                # 检查是否是关键陈述
                if any(indicator in content.lower() for indicator in key_indicators):
                    # 提取陈述部分（通常是第一个句子）
                    sentences = content.split('.')
                    if sentences:
                        key_statements.append(sentences[0].strip())
                        
        return key_statements
    
    def _is_related_to_statement(self, message: str, statement: str) -> bool:
        """检查消息是否与陈述相关"""
        message_words = set(message.lower().split())
        statement_words = set(statement.lower().split())
        
        common_words = message_words.intersection(statement_words)
        return len(common_words) >= 3
    
    def _extract_topic(self, message: str) -> str:
        """提取消息的主题"""
        topic_keywords = {
            'work': ['work', 'job', 'project', 'meeting', 'office', 'business'],
            'travel': ['travel', 'trip', 'vacation', 'journey', 'flight', 'hotel'],
            'food': ['food', 'eat', 'restaurant', 'cooking', 'meal', 'dinner'],
            'emotion': ['feel', 'emotion', 'mood', 'happy', 'sad', 'angry'],
            'hobby': ['hobby', 'interest', 'game', 'movie', 'music', 'sport']
        }
        
        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
                
        return "general"
    
    def _has_emotional_content(self, message: str) -> bool:
        """检查消息是否包含情感内容"""
        emotional_words = [
            'happy', 'sad', 'angry', 'excited', 'worried', 'nervous',
            '开心', '难过', '生气', '兴奋', '担心', '紧张'
        ]
        return any(word in message.lower() for word in emotional_words)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _is_in_cooldown(self, user_id: str) -> bool:
        """检查是否在引用冷却时间内"""
        if user_id in self.quote_cooldown:
            return time.time() - self.quote_cooldown[user_id] < 60
        return False
    
    def _is_recent_quote(self, user_id: str, quote_content: str) -> bool:
        """检查是否是最近引用过的内容"""
        for recent_quote in self.recent_quotes[user_id]:
            if self._calculate_similarity(quote_content, recent_quote) > 0.7:
                return True
        return False
    
    def update_conversation_state(self, user_id: str, user_message: str, ai_message: str):
        """更新对话状态"""
        self.last_user_messages[user_id].append(user_message)
        self.last_ai_messages[user_id].append(ai_message)
        
        # 更新话题
        topic = self._extract_topic(user_message)
        if topic:
            self.conversation_topics[user_id].append(topic)

class EnhancedEmotionEngine:
    """修复版情绪引擎 - 避免过度调整但保持所有功能"""
    
    def __init__(self):
        self.emotion_intensity = 0.5
        self.current_mood = "calm"
        self.mood_history = []
        self.adjustment_cooldown = defaultdict(float)
        
        # 完整的情绪映射
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
        """分析情感上下文 - 完整功能"""
        # 基础情感分析
        emotion_analysis = self._basic_emotion_analysis(user_message)
        
        # 考虑历史情绪
        historical_influence = self._analyze_historical_mood(chat_history)
        
        # 情绪自然波动
        natural_variation = self._calculate_natural_variation()
        
        # 综合情绪状态
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
        """根据情绪调整语气 - 修复重复问题"""
        current_time = time.time()
        user_id = "default"
        
        # 检查调整冷却
        if current_time - self.adjustment_cooldown.get(user_id, 0) < 5:
            return reply
            
        emotion = emotion_analysis['primary_emotion']
        intensity = emotion_analysis['intensity']
        mapping = self.emotion_mappings.get(emotion, self.emotion_mappings['calm'])
        
        # 降低调整概率
        adjusted_reply = reply
        
        # 副词调整 (25%概率)
        if random.random() < 0.25 and intensity > 0.4:
            adverb = random.choice(mapping['adverbs'])
            adjusted_reply = f"{adverb.capitalize()}, {adjusted_reply.lower()}"
        
        # 短语调整 (20%概率)
        if random.random() < 0.2 and intensity > 0.5:
            phrase = random.choice(mapping['phrases'])
            adjusted_reply = f"{phrase}. {adjusted_reply}"
        
        # 表情符号调整 (30%概率)
        if random.random() < 0.3 and intensity > 0.3:
            emoji = random.choice(mapping['emojis'])
            if adjusted_reply.endswith(('.', '!', '?')):
                adjusted_reply = f"{adjusted_reply[:-1]} {emoji}{adjusted_reply[-1]}"
            else:
                adjusted_reply = f"{adjusted_reply} {emoji}"
        
        # 应用情绪特定调整
        adjusted_reply = self._apply_emotion_specific_adjustments(adjusted_reply, emotion, intensity)
        
        # 记录调整时间
        if adjusted_reply != reply:
            self.adjustment_cooldown[user_id] = current_time
            
        return adjusted_reply
    
    def _apply_emotion_specific_adjustments(self, reply: str, emotion: str, intensity: float) -> str:
        """应用情绪特定的调整"""
        adjustments = {
            'playful': {
                'high': lambda r: r.replace('.', '!').replace('?', '?!') if random.random() < 0.4 else r,
                'medium': lambda r: r + '~' if random.random() < 0.3 else r,
                'low': lambda r: r
            },
            'sad': {
                'high': lambda r: r.replace('!', '.').replace('?', '...') if random.random() < 0.3 else r,
                'medium': lambda r: r + '...' if random.random() < 0.2 else r,
                'low': lambda r: r
            },
            'excited': {
                'high': lambda r: r.upper() if len(r.split()) < 4 and random.random() < 0.3 else r,
                'medium': lambda r: r + '!' if random.random() < 0.3 else r,
                'low': lambda r: r
            },
            'thoughtful': {
                'high': lambda r: r + '...' if random.random() < 0.3 else r,
                'medium': lambda r: r,
                'low': lambda r: r
            }
        }
        
        if emotion in adjustments:
            intensity_level = 'high' if intensity > 0.7 else 'medium' if intensity > 0.4 else 'low'
            if intensity_level in adjustments[emotion]:
                reply = adjustments[emotion][intensity_level](reply)
        
        return reply

class TopicExtensionManager:
    """修复版话题扩展管理器 - 完整功能"""
    
    def __init__(self):
        self.user_interests = defaultdict(lambda: defaultdict(int))
        self.recent_topics = defaultdict(lambda: deque(maxlen=5))
        self.topic_cooldown = {}
        self.recent_extensions = defaultdict(lambda: deque(maxlen=3))
        
        # 完整的话题库
        self.topic_library = {
            'work': [
                "How's work been lately? Any interesting projects?",
                "Have you been busy with work recently?",
                "I was just thinking about some business strategies..."
            ],
            'travel': [
                "Speaking of which, have you traveled anywhere interesting recently?",
                "That reminds me of my trip to {random_place}...",
                "I've been thinking about planning a new trip somewhere."
            ],
            'food': [
                "By the way, have you tried any good restaurants lately?",
                "This conversation is making me think about food...",
                "I recently discovered this amazing {random_cuisine} place."
            ],
            'hobby': [
                "What have you been doing for fun recently?",
                "I've been getting into {random_hobby} lately...",
                "Have you picked up any new hobbies?"
            ],
            'emotion': [
                "How have you been feeling about things in general?",
                "I've been reflecting on {random_reflection}...",
                "What's been on your mind lately?"
            ]
        }
        
        self.random_places = ["Tokyo", "London", "New York", "Paris", "Singapore", "Sydney"]
        self.random_cuisines = ["Italian", "Japanese", "Mexican", "Thai", "French"]
        self.random_hobbies = ["reading", "cooking", "photography", "gardening", "yoga"]
        self.random_reflections = ["work-life balance", "personal growth", "future plans", "relationships"]
    
    def should_extend_topic(self, user_id: str, current_topic: str, chat_history: List[Dict]) -> Tuple[bool, str]:
        """判断是否应该扩展话题 - 修复重复问题"""
        # 检查冷却时间
        if self._is_in_topic_cooldown(user_id):
            return False, ""
            
        # 检查最近是否扩展过类似话题
        if self._has_recent_extension(user_id, current_topic):
            return False, ""
            
        # 检查话题重复性
        if self._is_topic_repetitive(user_id, current_topic):
            alternative_topic = self._get_alternative_topic(current_topic)
            if alternative_topic and not self._has_recent_extension(user_id, alternative_topic):
                self.recent_extensions[user_id].append(self._extract_topic_from_message(alternative_topic))
                return True, alternative_topic
        
        # 检查自然扩展点
        if self._is_natural_extension_point(chat_history):
            new_topic = self._select_relevant_topic(user_id)
            if new_topic and not self._has_recent_extension(user_id, new_topic):
                self.recent_extensions[user_id].append(self._extract_topic_from_message(new_topic))
                return True, new_topic
        
        # 随机扩展（适当概率）
        if random.random() < 0.08:
            new_topic = self._get_random_topic()
            if new_topic and not self._has_recent_extension(user_id, new_topic):
                self.recent_extensions[user_id].append(self._extract_topic_from_message(new_topic))
                return True, new_topic
            
        return False, ""
    
    def _is_in_topic_cooldown(self, user_id: str) -> bool:
        """检查话题扩展冷却时间"""
        if user_id in self.topic_cooldown:
            return time.time() - self.topic_cooldown[user_id] < 300
        return False
    
    def _is_topic_repetitive(self, user_id: str, current_topic: str) -> bool:
        """检查话题是否重复"""
        if not self.recent_topics[user_id]:
            return False
            
        topic_count = list(self.recent_topics[user_id]).count(current_topic)
        return topic_count >= 2
    
    def _has_recent_extension(self, user_id: str, topic: str) -> bool:
        """检查最近是否扩展过类似话题"""
        extracted_topic = self._extract_topic_from_message(topic)
        for recent in self.recent_extensions[user_id]:
            if recent == extracted_topic:
                return True
        return False
    
    def _is_natural_extension_point(self, chat_history: List[Dict]) -> bool:
        """检查是否为自然扩展点"""
        if len(chat_history) < 3:
            return False
            
        recent_turns = chat_history[-3:]
        user_messages = [msg for msg in recent_turns if msg.get('role') == 'user']
        ai_messages = [msg for msg in recent_turns if msg.get('role') == 'assistant']
        
        return len(user_messages) >= 1 and len(ai_messages) >= 1 and recent_turns[-1]['role'] == 'user'
    
    def _select_relevant_topic(self, user_id: str) -> str:
        """选择相关话题"""
        if not self.user_interests[user_id]:
            return self._get_random_topic()
            
        top_topic = max(self.user_interests[user_id].items(), key=lambda x: x[1])[0]
        if top_topic in self.topic_library:
            topic_options = self.topic_library[top_topic]
            return random.choice(topic_options)
        
        return self._get_random_topic()
    
    def _get_alternative_topic(self, current_topic: str) -> str:
        """获取替代话题"""
        all_topics = list(self.topic_library.keys())
        if current_topic in all_topics:
            all_topics.remove(current_topic)
        
        if not all_topics:
            return ""
            
        new_topic = random.choice(all_topics)
        topic_options = self.topic_library[new_topic]
        return random.choice(topic_options)
    
    def _get_random_topic(self) -> str:
        """获取随机话题"""
        topic_category = random.choice(list(self.topic_library.keys()))
        topic_template = random.choice(self.topic_library[topic_category])
        
        if '{random_place}' in topic_template:
            topic_template = topic_template.format(random_place=random.choice(self.random_places))
        elif '{random_cuisine}' in topic_template:
            topic_template = topic_template.format(random_cuisine=random.choice(self.random_cuisines))
        elif '{random_hobby}' in topic_template:
            topic_template = topic_template.format(random_hobby=random.choice(self.random_hobbies))
        elif '{random_reflection}' in topic_template:
            topic_template = topic_template.format(random_reflection=random.choice(self.random_reflections))
        
        return topic_template
    
    def update_user_interests(self, user_id: str, message: str):
        """更新用户兴趣"""
        topic = self._extract_topic_from_message(message)
        if topic:
            self.user_interests[user_id][topic] += 1
            self.recent_topics[user_id].append(topic)
            self.topic_cooldown[user_id] = time.time()
    
    def _extract_topic_from_message(self, message: str) -> str:
        """从消息中提取话题"""
        topic_keywords = {
            'work': ['work', 'job', 'project', 'meeting', 'office', 'business'],
            'travel': ['travel', 'trip', 'vacation', 'journey', 'flight', 'hotel'],
            'food': ['food', 'eat', 'restaurant', 'cooking', 'meal', 'dinner'],
            'hobby': ['hobby', 'game', 'movie', 'music', 'sport', 'read'],
            'emotion': ['feel', 'emotion', 'mood', 'happy', 'sad', 'angry']
        }
        
        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
                
        return ""

class BusyStateManager:
    """忙碌状态管理器 - 完整功能"""
    
    def __init__(self, character_profile):
        self.character_profile = character_profile
        self.current_state = "available"
        self.busy_until = None
        self.pending_messages = defaultdict(list)
        self.recovery_scheduled = None
        self.busy_reasons = {
            'meeting': "in a meeting",
            'focused_work': "focused on work", 
            'traveling': "traveling",
            'personal_time': "in personal time"
        }
        
    def set_busy(self, reason: str, duration_minutes: int = None):
        """设置忙碌状态"""
        if reason not in self.busy_reasons:
            return False
            
        if duration_minutes is None:
            duration_minutes = random.randint(30, 120)
            
        self.current_state = "busy"
        self.busy_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.busy_reason = reason
        
        print(f"🔴 进入忙碌状态: {reason}, 持续时间: {duration_minutes}分钟")
        return True
        
    def is_busy(self) -> bool:
        """检查是否忙碌"""
        if self.current_state != "busy" or not self.busy_until:
            return False
            
        if datetime.now() >= self.busy_until:
            self._schedule_recovery()
            return False
            
        return True
        
    def _schedule_recovery(self):
        """安排恢复"""
        recovery_delay = random.randint(2, 10)
        self.recovery_scheduled = datetime.now() + timedelta(minutes=recovery_delay)
        self.current_state = "recovering"
        print(f"🟡 安排恢复响应: {recovery_delay}分钟后")
        
    def should_recover(self) -> bool:
        """检查是否应该恢复"""
        return (self.current_state == "recovering" and 
                self.recovery_scheduled and 
                datetime.now() >= self.recovery_scheduled)
        
    def cache_message(self, user_id: str, message: str, emotion_analysis: Dict):
        """缓存消息"""
        self.pending_messages[user_id].append({
            'message': message,
            'timestamp': datetime.now(),
            'emotion_analysis': emotion_analysis,
            'priority': self._calculate_priority(message, emotion_analysis)
        })
        
    def _calculate_priority(self, message: str, emotion_analysis: Dict) -> int:
        """计算消息优先级"""
        priority = 1
        
        urgent_keywords = ['urgent', 'emergency', 'help', '紧急', '急事']
        if any(keyword in message.lower() for keyword in urgent_keywords):
            priority += 3
            
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        if emotion in ['sad', 'concerned']:
            priority += 2
        elif emotion in ['excited', 'playful']:
            priority += 1
            
        if len(message.split()) > 20:
            priority += 1
            
        return priority
        
    def get_busy_response(self, user_message: str, emotion_analysis: Dict) -> str:
        """获取忙碌响应"""
        reason = self.busy_reasons.get(self.busy_reason, "busy")
        remaining_time = self.busy_until - datetime.now()
        remaining_minutes = max(1, int(remaining_time.total_seconds() / 60))
        
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        
        responses = {
            'meeting': [
                f"Currently in a meeting, will reply in about {remaining_minutes} minutes 📊",
                f"In a strategy session right now, back in {remaining_minutes} minutes 💼",
                f"Discussing project timelines, available in {remaining_minutes} minutes 👥"
            ],
            'focused_work': [
                f"Deep in work mode, will respond in {remaining_minutes} minutes 💻",
                f"Focused on analysis, back in {remaining_minutes} minutes 📈",
                f"Handling some urgent tasks, available in {remaining_minutes} minutes ⚡"
            ],
            'traveling': [
                f"On the road right now, will reply in {remaining_minutes} minutes 🚗",
                f"Traveling between meetings, back in {remaining_minutes} minutes ✈️",
                f"Currently moving locations, available in {remaining_minutes} minutes 🗺️"
            ],
            'personal_time': [
                f"In personal time, will respond in {remaining_minutes} minutes 🌿",
                f"Taking some time for myself, back in {remaining_minutes} minutes ☕",
                f"Handling personal matters, available in {remaining_minutes} minutes 💫"
            ]
        }
        
        if emotion == 'sad' or emotion == 'concerned':
            base_responses = [
                f"I see your message and will reply properly in about {remaining_minutes} minutes. Please know I'm here for you 💭",
                f"I understand this is important. I'm currently {reason} but will respond fully in {remaining_minutes} minutes 🌟",
                f"Thank you for sharing. I'm temporarily occupied but will give this proper attention in {remaining_minutes} minutes 💫"
            ]
        else:
            base_responses = responses.get(self.busy_reason, responses['focused_work'])
            
        return random.choice(base_responses)
        
    def get_recovery_response(self, user_id: str) -> List[str]:
        """获取恢复响应"""
        if user_id not in self.pending_messages or not self.pending_messages[user_id]:
            return []
            
        pending = sorted(self.pending_messages[user_id], key=lambda x: x['priority'], reverse=True)
        
        recovery_responses = []
        
        if len(pending) == 1:
            msg = pending[0]
            recovery_responses.append(f"Thanks for your patience! Now back to your message about: \"{msg['message'][:50]}...\"")
        else:
            recovery_responses.append(f"Thanks for waiting! I had {len(pending)} messages from you while I was {self.busy_reason}.")
            
            for i, msg in enumerate(pending[:3]):
                recovery_responses.append(f"{i+1}. Regarding: \"{msg['message'][:30]}...\"")
                
        self.pending_messages[user_id] = []
        self.current_state = "available"
        self.busy_until = None
        self.recovery_scheduled = None
        
        return recovery_responses

class EmotionalOverrideManager:
    """情绪优先覆盖管理器 - 完整功能"""
    
    def __init__(self):
        self.emotional_override_keywords = {
            'urgent': ['urgent', 'emergency', 'help me', 'need you', 'important', '紧急', '急事', '救命'],
            'emotional': ['sad', 'cry', 'upset', 'depressed', 'lonely', 'scared', 'afraid', 
                         '难过', '伤心', '哭泣', '孤独', '害怕', '担心'],
            'intimate': ['love you', 'miss you', 'care about', 'thinking of you', 
                        '爱你', '想你', '在乎', '关心'],
            'crisis': ['suicide', 'kill myself', 'end it all', 'can\'t go on', 
                      '自杀', '不想活了', '绝望']
        }
        
    def should_override_busy(self, message: str, emotion_analysis: Dict) -> bool:
        """检查是否应该覆盖忙碌状态"""
        message_lower = message.lower()
        
        # 检查关键词
        for category, keywords in self.emotional_override_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return True
        
        # 检查情绪强度
        if emotion_analysis.get('intensity', 0) > 0.8:
            return True
            
        # 检查情绪类型
        primary_emotion = emotion_analysis.get('primary_emotion', 'neutral')
        if primary_emotion in ['sad', 'concerned'] and emotion_analysis.get('confidence', 0) > 0.7:
            return True
            
        return False
    
    def get_override_response(self, message: str, emotion_analysis: Dict) -> str:
        """获取覆盖忙碌状态的响应"""
        primary_emotion = emotion_analysis.get('primary_emotion', 'neutral')
        intensity = emotion_analysis.get('intensity', 0.5)
        
        override_responses = {
            'sad': [
                "I can tell this is important. Let me put everything aside for a moment...",
                "This sounds serious. I'm here for you right now.",
                "I sense this matters deeply. Let me focus completely on you."
            ],
            'concerned': [
                "You seem really concerned about this. Let me give you my full attention.",
                "This seems to be weighing on you. I want to be here for you properly.",
                "I can feel the importance of this. Let me set everything else aside."
            ],
            'excited': [
                "This sounds exciting! Let me share in your enthusiasm right away!",
                "How wonderful! I want to celebrate this moment with you.",
                "That's amazing news! Let me join in your happiness immediately."
            ]
        }
        
        responses = override_responses.get(primary_emotion, [
            "This seems important. Let me give you my full attention right now.",
            "I can tell this matters. Let me focus completely on you.",
            "This deserves immediate attention. I'm here for you."
        ])
        
        response = random.choice(responses)
        
        # 根据强度调整语气
        if intensity > 0.8:
            response = response.replace('.', '!').replace('right now', 'right this moment')
        
        return response

class TextSanitizer:
    """文本净化器 - 完整功能"""
    
    def __init__(self):
        self.stage_direction_patterns = [
            r'\([^)]*\)',
            r'\*[^*]*\*',  
            r'\[[^\]]*\]',
            r'\{[^}]*\}',
            r'<[^>]*>',
            r'（[^）]*）',
            r'【[^】]*】',
        ]
        
        self.excessive_emojis = r'([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]\s*){3,}'
        self.repetitive_phrases = [
            r'(I sense this matters deeply[!.]?\s*){2,}',
            r'(Let me focus completely on you[!.]?\s*){2,}',
            r'(Remember I mentioned[^.!?]*[.!?]\s*){2,}',
            r'(As I mentioned before[^.!?]*[.!?]\s*){2,}',
        ]
        
    def sanitize_text(self, text: str) -> str:
        """净化文本"""
        if not text:
            return text
            
        # 移除舞台指令
        for pattern in self.stage_direction_patterns:
            text = re.sub(pattern, '', text)
            
        # 移除过多表情符号
        text = re.sub(self.excessive_emojis, self._reduce_emojis, text)
        
        # 移除重复短语
        for pattern in self.repetitive_phrases:
            text = re.sub(pattern, lambda m: m.group().split('.')[0] + '. ', text)
        
        # 清理空格
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
        
    def _reduce_emojis(self, match) -> str:
        """减少连续表情符号"""
        emojis = match.group()
        return emojis[:2]

# ==================== 智能响应协调器集成 ====================

class AdvancedResponseCoordinator:
    """高级响应协调器 - 完整功能"""
    
    def __init__(self):
        # 初始化所有新功能组件
        self.rhythm_detector = SemanticRhythmDetector()
        self.input_processor = ContinuousInputProcessor()
        self.intelligent_coordinator = IntelligentResponseCoordinator()
        self.natural_generator = NaturalLanguageGenerator()
        self.sentence_streamer = SentenceStreamer()
        
        # 用户状态跟踪
        self.user_states = defaultdict(dict)
        self.response_queues = defaultdict(list)
        self.processing_tracker = defaultdict(lambda: {
            'last_processing': 0,
            'processing_count': 0
        })
        
    async def process_user_input(self, user_id: str, message: str, chat_history: List[Dict]) -> Dict[str, Any]:
        """处理用户输入并返回响应决策"""
        current_time = time.time()
        tracker = self.processing_tracker[user_id]
        
        # 检查处理频率
        if current_time - tracker['last_processing'] < 1.0:
            tracker['processing_count'] += 1
            if tracker['processing_count'] > 3:
                return {
                    'immediate_action': 'hold',
                    'should_stream': False,
                    'stream_style': 'normal'
                }
        else:
            tracker['processing_count'] = 1
            
        tracker['last_processing'] = current_time
        
        # 分析消息节奏
        rhythm_analysis = self.rhythm_detector.analyze_message_rhythm(user_id, message)
        
        # 使用智能协调器处理
        response_decision = await self.intelligent_coordinator.process_user_message(
            user_id, message, chat_history
        )
        
        # 增强决策信息
        enhanced_decision = {
            **response_decision,
            'rhythm_analysis': rhythm_analysis,
            'user_state': self.user_states[user_id],
            'should_stream': len(message) > 20,
            'stream_style': self._determine_stream_style(rhythm_analysis)
        }
        
        return enhanced_decision
    
    async def generate_enhanced_response(self, context: str, emotion: str, 
                                       user_id: str, chat_history: List[Dict]) -> str:
        """生成增强的响应"""
        
        # 使用自然语言生成器
        base_response = await self.intelligent_coordinator.generate_natural_response(
            context, chat_history, emotion
        )
        
        # 应用自然语言优化
        natural_response = self.natural_generator.make_conversational(base_response)
        emotional_response = self.natural_generator.add_emotional_color(natural_response, emotion)
        
        return emotional_response
    
    async def stream_enhanced_response(self, response_text: str, user_id: str,
                                     send_callback: Callable[[str, bool], None],
                                     typing_callback: Callable[[float], None] = None):
        """流式发送增强响应"""
        
        # 确定发送风格
        user_state = self.user_states.get(user_id, {})
        style = user_state.get('preferred_style', 'normal')
        
        # 使用逐句发送管理器
        await self.sentence_streamer.stream_response(
            response_text, 
            send_callback,
            style,
            typing_callback
        )
    
    def _determine_stream_style(self, rhythm_analysis: Dict) -> str:
        """确定流式发送风格"""
        continuous_count = rhythm_analysis.get('continuous_count', 0)
        
        if continuous_count >= 3:
            return 'fast'
        elif rhythm_analysis.get('is_semantically_complete', True):
            return 'normal'
        else:
            return 'thinking'
    
    def update_user_preferences(self, user_id: str, message: str, response: str):
        """更新用户偏好"""
        # 分析用户喜欢的响应风格
        response_length = len(response)
        uses_emojis = any(char in response for char in ['😊', '😂', '❤️', '🤗'])
        
        preferred_style = 'normal'
        if response_length < 50:
            preferred_style = 'fast'
        elif response_length > 150:
            preferred_style = 'slow'
            
        self.user_states[user_id] = {
            'preferred_style': preferred_style,
            'likes_emojis': uses_emojis,
            'avg_response_length': response_length,
            'last_interaction': time.time()
        }

# ==================== 路径管理 ====================
class PathManager:
    """统一路径管理模块"""
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = self.base_dir
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.chat_dir = os.path.join(self.base_dir, "chat_histories")
        self._ensure_dirs()

    def _ensure_dirs(self):
        for folder in [self.logs_dir, self.data_dir, self.chat_dir]:
            os.makedirs(folder, exist_ok=True)

    def get_config_path(self, name: str) -> str:
        return os.path.join(self.config_dir, f"{name}.json")

    def get_chat_history_path(self, user_id: str) -> str:
        return os.path.join(self.chat_dir, f"{user_id}.json")

path_manager = PathManager()

# ==================== 配置管理 ====================
class ConfigManager:
    def __init__(self):
        self.config_cache = {}
        self._cache_timestamps = {}
        print("✅ 配置管理器加载成功")

    def load_config(self, config_type, force_reload=False):
        current_time = time.time()
        
        if (not force_reload and 
            config_type in self.config_cache and 
            current_time - self._cache_timestamps.get(config_type, 0) < 2):
            return self.config_cache[config_type]
        
        config_data = self._load_from_file(config_type)
        self.config_cache[config_type] = config_data
        self._cache_timestamps[config_type] = current_time
        return config_data

    def _load_from_file(self, config_type):
        try:
            filepath = path_manager.get_config_path(config_type)
            if not os.path.exists(filepath):
                return self._get_default_config(config_type)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                return self._get_default_config(config_type)
                
            return json.loads(content)
            
        except Exception as e:
            print(f"⚠️ 读取配置失败 {config_type}: {str(e)}")
            return self._get_default_config(config_type)

    def _get_default_config(self, config_type):
        defaults = {
            'system_config': {
                "SYSTEM_VERSION": "v7.3.0", "LANGUAGE": "English", "PROACTIVE_CARE": True,
                "EMOTION_ANALYSIS": True, "RELATIONSHIP_TRACKING": True, "REALTIME_UPDATE": True,
                "BUSINESS_MODE": True, "ENABLE_SMART_SCHEDULE": True, "ENABLE_SHORT_MESSAGE": True,
                "ENABLE_EMOTIONAL_QUOTING": True, "ENABLE_LIGHT_MEMORY": True, "ENABLE_ADVANCED_FEATURES": True
            },
            'character_profile': {
                "profile_version": 6,
                "last_updated": datetime.now().isoformat(),
                "basic_info": {
                    "name": "Tanaka Kiyomi", "chinese_name": "田中 清美", "age": 33,
                    "occupation": "Founder of Trading Company & Jewelry Company & Gold Options Investor",
                    "current_city": "London", "hometown": "Tokyo", "education": "Graduated from Japanese University majoring in Financial Management",
                    "languages": ["Japanese", "English", "Basic Chinese"]
                },
                "personality": {
                    "core_traits": ["Independent", "Resilient", "Sharp", "Elegant", "Cautious", "Good Listener", "Business Acumen", "Emotionally Rich"],
                    "conversation_style": "Elegant and professional, as natural as communicating with business partners, with appropriate emotional expression",
                    "emotional_range": ["Warm", "Humorous", "Empathetic", "Professional", "Occasionally tired", "Slightly self-deprecating", "Emotionally delicate"],
                    "humor_level": 6, "empathy_level": 8, "energy_level": 7, "investment_expertise": 9, "emotional_intelligence": 8
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
                "OPENAI_API_KEY": "", "USER_API_ID": "", "USER_API_HASH": "", 
                "USER_PHONE": "", "AI_MODEL": "deepseek-chat"
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
                    "auto_reply_enabled": True, "use_emojis": True, 
                    "max_emojis_per_message": 2, "smart_typing_detection": True,
                    "enable_smart_quoting": True, "quote_cooldown": 60,
                    "enable_smart_schedule": True, "enable_short_message": True,
                    "daily_message_limit": 50, "emotional_quoting_enabled": True,
                    "light_memory_enabled": True, "natural_segmentation": True
                },
                "response_control": {
                    "min_response_chars": 3, "max_response_chars": 500,
                    "enable_length_based_timing": True, "fast_reply_threshold": 50,
                    "slow_reply_threshold": 200, "semantic_segmentation": True,
                    "emotional_context_integration": True
                },
                "smart_conversation": {
                    "enable_smart_detection": True, "continuous_input_threshold": 10,
                    "max_continuous_messages": 5, "light_response_probability": 0.4,
                    "response_delay": 5, "enable_rhythm_management": True,
                    "semantic_completion_detection": True, "emotional_quoting_enabled": True,
                    "light_memory_enabled": True, "natural_segmentation": True,
                    "contextual_memory_weight": 0.4
                }
            },
            'relationships': {}
        }
        return defaults.get(config_type, {})

    def save_config(self, config_type, data):
        try:
            self.config_cache[config_type] = data
            self._cache_timestamps[config_type] = time.time()
            
            filepath = path_manager.get_config_path(config_type)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"⚠️ 保存配置失败 {config_type}: {str(e)}")
            return False

config_manager = ConfigManager()

# ==================== 情感分析模块 ====================
class EmotionAnalyzer:
    def __init__(self):
        self.emotion_keywords = {
            'happy': ['happy', 'excited', 'great', 'wonderful', 'amazing', 'good', 'nice', 'love', 'like', 'enjoy', 'fun', 'haha', 'lol', '😊', '😂', '🥰'],
            'sad': ['sad', 'bad', 'terrible', 'awful', 'hate', 'dislike', 'upset', 'cry', 'sorry', 'unhappy', '😢', '😭', '😞'],
            'angry': ['angry', 'mad', 'annoyed', 'frustrated', 'hate', 'dislike', 'stupid', 'idiot', '😠', '😡', '🤬'],
            'surprised': ['surprised', 'wow', 'omg', 'unbelievable', 'incredible', 'amazing', '😮', '😲', '🤯'],
            'confused': ['confused', 'unsure', 'uncertain', 'doubt', 'question', '🤔', '😕', '😵'],
            'playful': ['joking', 'kidding', 'funny', 'humor', 'lol', 'haha', '😂', '😄', '😆', '🤣'],
            'thoughtful': ['think', 'thought', 'consider', 'reflect', 'ponder', 'contemplate', '💭', '🤔'],
            'excited': ['excited', 'thrilled', 'eager', 'looking forward', 'can\'t wait', '😃', '🎉', '✨']
        }
        
        self.chinese_emotion_keywords = {
            'happy': ['开心', '高兴', '快乐', '幸福', '喜欢', '爱', '哈哈', '呵呵', '嘻嘻', '😊', '😂', '🥰'],
            'sad': ['伤心', '难过', '悲伤', '不开心', '讨厌', '不喜欢', '哭', '难受', '😢', '😭', '😞'],
            'angry': ['生气', '愤怒', '恼火', '烦躁', '讨厌', '不喜欢', '傻', '笨', '😠', '😡', '🤬'],
            'surprised': ['惊讶', '惊奇', '没想到', '不可思议', '震惊', '😮', '😲', '🤯'],
            'confused': ['困惑', '疑惑', '不确定', '怀疑', '问题', '🤔', '😕', '😵'],
            'playful': ['开玩笑', '搞笑', '幽默', '哈哈', '呵呵', '😂', '😄', '😆', '🤣'],
            'thoughtful': ['思考', '想法', '考虑', '反思', '沉思', '💭', '🤔'],
            'excited': ['兴奋', '激动', '期待', '盼望', '等不及', '😃', '🎉', '✨']
        }

    def analyze_emotion(self, text: str) -> Dict[str, any]:
        """分析文本情感"""
        if not text:
            return {
                'primary_emotion': 'neutral', 
                'confidence': 0.0, 
                'emotional_words': [],
                'intensity': 0.0
            }
        
        text_lower = text.lower()
        emotion_scores = {}
        detected_words = []
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + 1
                    if keyword not in detected_words:
                        detected_words.append(keyword)
        
        for emotion, keywords in self.chinese_emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + 1
                    if keyword not in detected_words:
                        detected_words.append(keyword)
        
        if not emotion_scores:
            return {
                'primary_emotion': 'neutral', 
                'confidence': 0.0, 
                'emotional_words': [],
                'intensity': 0.0
            }
        
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = min(emotion_scores[primary_emotion] / len(text.split()) * 10, 1.0)
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': round(confidence, 2),
            'emotional_words': detected_words,
            'all_emotions': emotion_scores,
            'intensity': round(confidence, 2)
        }

# ==================== 聊天历史管理器 ====================
class ChatHistoryManager:
    def __init__(self):
        self.histories = {}
        self.max_history_length = 50

    async def load_chat_history(self, user_id: str):
        if user_id in self.histories:
            return self.histories[user_id]
        
        try:
            filepath = path_manager.get_chat_history_path(user_id)
            if os.path.exists(filepath):
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content.strip():
                        self.histories[user_id] = json.loads(content)
                        return self.histories[user_id]
        except Exception as e:
            print(f"⚠️ 加载聊天历史失败 {user_id}: {str(e)}")
        
        self.histories[user_id] = []
        return self.histories[user_id]

    async def save_chat_history(self, user_id: str, history: list):
        try:
            self.histories[user_id] = history[-self.max_history_length:]
            
            filepath = path_manager.get_chat_history_path(user_id)
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.histories[user_id], indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"⚠️ 保存聊天历史失败 {user_id}: {str(e)}")

    async def add_message(self, user_id: str, role: str, content: str):
        history = await self.load_chat_history(user_id)
        history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        await self.save_chat_history(user_id, history)

# ==================== AI 回复生成器（修复版） ====================
class AIReplyGenerator:
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model
        
        # 旧的情感分析器（保留作为备用）
        self.emotion_analyzer = EmotionAnalyzer()
        self.enhanced_emotion_engine = EnhancedEmotionEngine()
        
        # 初始化新的核心模块
        self.core_intent_analyzer = None  # 将在set_character_profile后初始化
        self.core_emotion_engine = CoreEmotionEngine()
        self.core_prompt_builder = None  # 将在set_character_profile后初始化
        self.core_memory_system = ThreeTierMemorySystem(data_dir='data/memories')
        self.core_personality_engine = None  # 将在set_character_profile后初始化
        self.core_conversation_flow = NaturalConversationFlowEngine()
        
        # 原有增强模块
        self.enhanced_quote_manager = EnhancedQuoteManager()
        self.topic_extension_manager = TopicExtensionManager()
        self.text_sanitizer = TextSanitizer()
        self.emotional_override_manager = EmotionalOverrideManager()
        self.advanced_coordinator = AdvancedResponseCoordinator()
        
        # 配置开关：控制是否启用新核心模块
        self.use_core_modules = True  # 默认启用新模块
        self.use_core_intent_analyzer = True
        self.use_core_emotion_engine = True
        self.use_core_prompt_builder = True
        self.use_core_memory_system = True
        self.use_core_personality_engine = True
        self.use_core_conversation_flow = True
        
        # 响应协调状态
        self.processing_tracker = defaultdict(lambda: {
            'last_message': '',
            'last_processed': 0,
            'processing_count': 0,
            'processing_lock': False
        })
        
        print("✅ AIReplyGenerator 初始化完成")
        print(f"   新核心模块状态: {'\u542f\u7528' if self.use_core_modules else '\u7981\u7528'}")
        print(f"   - 意图分析: {'\u2705' if self.use_core_intent_analyzer else '\u274c'}")
        print(f"   - 情感智能: {'\u2705' if self.use_core_emotion_engine else '\u274c'}")
        print(f"   - Prompt构建: {'\u2705' if self.use_core_prompt_builder else '\u274c'}")
        print(f"   - 记忆系统: {'\u2705' if self.use_core_memory_system else '\u274c'}")
        print(f"   - 人设一致性: {'\u2705' if self.use_core_personality_engine else '\u274c'}")
        print(f"   - 对话流控制: {'\u2705' if self.use_core_conversation_flow else '\u274c'}")
        
    def set_character_profile(self, character_profile):
        """设置角色配置"""
        self.character_profile = character_profile
        
        # 初始化需要API和角色配置的核心模块
        if self.use_core_modules:
            try:
                # 初始化意图分析器（需要API key）
                if self.use_core_intent_analyzer and hasattr(self, 'client'):
                    api_key = self.client.api_key
                    self.core_intent_analyzer = DeepIntentAnalyzer(
                        api_key=api_key,
                        model=self.model
                    )
                    print("✅ DeepIntentAnalyzer 初始化成功")
                
                # 初始化Prompt构建器
                if self.use_core_prompt_builder:
                    self.core_prompt_builder = OptimizedPromptBuilder(character_profile)
                    print("✅ OptimizedPromptBuilder 初始化成功")
                
                # 初始化人设一致性引擎
                if self.use_core_personality_engine:
                    self.core_personality_engine = PersonalityConsistencyEngine(character_profile)
                    print("✅ PersonalityConsistencyEngine 初始化成功")
                    
            except Exception as e:
                print(f"⚠️ 核心模块初始化失败: {str(e)}")
                self.use_core_modules = False

    async def generate_reply(self, user_message: str, chat_history: list, character_profile: dict, emotion_analysis: Dict = None, user_id: str = None) -> Tuple[str, Dict]:
        """生成AI回复 - 修复重复问题版本"""
        current_time = time.time()
        tracker = self.processing_tracker[user_id]
        
        # 检查处理锁
        if tracker['processing_lock']:
            print("🔒 检测到处理锁，返回简单响应")
            return self._get_simple_response(user_message, emotion_analysis), {'should_stream': False}
            
        tracker['processing_lock'] = True
        
        try:
            # 检查重复处理
            if (user_message == tracker['last_message'] and 
                current_time - tracker['last_processed'] < 2.0):
                tracker['processing_count'] += 1
                if tracker['processing_count'] > 1:
                    print("🔄 检测到重复处理，返回简单响应")
                    return self._get_simple_response(user_message, emotion_analysis), {'should_stream': False}
            else:
                tracker['processing_count'] = 0
                tracker['last_message'] = user_message
                
            tracker['last_processed'] = current_time
            
            # 基础情感分析
            if emotion_analysis is None:
                emotion_analysis = self.emotion_analyzer.analyze_emotion(user_message)
            
            if 'intensity' not in emotion_analysis:
                emotion_analysis['intensity'] = emotion_analysis.get('confidence', 0.5)
            
            # 使用协调器处理
            response_decision = await self.advanced_coordinator.process_user_input(
                user_id, user_message, chat_history
            )
            
            if response_decision.get('immediate_action') == 'short_feedback':
                return response_decision.get('response_content', ''), response_decision
            
            # 增强情感分析
            enhanced_emotion = self.enhanced_emotion_engine.analyze_emotional_context(user_message, chat_history)
            
            if 'intensity' not in enhanced_emotion:
                enhanced_emotion['intensity'] = enhanced_emotion.get('confidence', 0.5)
            
            # 协调的智能引用检查
            should_quote, quote_type, quote_content = self._get_coordinated_quoting(
                user_id, user_message, chat_history, enhanced_emotion
            )
            
            # 协调的话题扩展检查
            should_extend, extension_topic = self._get_coordinated_extension(
                user_id, user_message, chat_history, enhanced_emotion
            )
            
            # 协调的情绪覆盖检查
            should_override = self._get_coordinated_override(user_message, emotion_analysis, should_quote, should_extend)
            
            system_prompt = self._build_enhanced_system_prompt(
                character_profile, enhanced_emotion, should_quote, quote_type, should_extend, should_override
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史消息
            for msg in chat_history[-6:]:
                messages.append({
                    "role": msg['role'], 
                    "content": msg['content']
                })
            
            messages.append({"role": "user", "content": user_message})
            
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=400,
                        temperature=0.7,
                        stream=False
                    )
                )
                
                reply = response.choices[0].message.content.strip()
                
                # 协调的后处理
                processed_reply = self._coordinated_post_process(
                    reply, enhanced_emotion, user_message, user_id, 
                    should_quote, quote_type, quote_content,
                    should_extend, extension_topic, should_override
                )
                
                # 更新发送决策
                response_decision['should_stream'] = len(processed_reply) > 50
                response_decision['stream_style'] = self._determine_stream_style(enhanced_emotion, len(processed_reply))
                
                # 更新对话状态
                if user_id:
                    self.enhanced_quote_manager.update_conversation_state(user_id, user_message, processed_reply)
                    self.topic_extension_manager.update_user_interests(user_id, user_message)
                    self.advanced_coordinator.update_user_preferences(user_id, user_message, processed_reply)
                
                return processed_reply, response_decision
                
            except Exception as e:
                print(f"⚠️ AI API 错误: {str(e)}")
                fallback_reply = self._get_enhanced_fallback_response(user_message, emotion_analysis)
                response_decision['should_stream'] = False
                return fallback_reply, response_decision
                
        finally:
            tracker['processing_lock'] = False

    def _get_coordinated_quoting(self, user_id: str, user_message: str, chat_history: List[Dict], emotion_analysis: Dict) -> Tuple[bool, str, str]:
        """协调的引用检查"""
        # 高情绪状态时减少引用
        if emotion_analysis.get('intensity', 0) > 0.7:
            print("🎭 高情绪状态，减少引用频率")
            return False, None, None
            
        # 短消息不引用
        if len(user_message.split()) < 4:
            return False, None, None
            
        return self.enhanced_quote_manager.should_quote(user_id, user_message, chat_history)

    def _get_coordinated_extension(self, user_id: str, user_message: str, chat_history: List[Dict], emotion_analysis: Dict) -> Tuple[bool, str]:
        """协调的话题扩展检查"""
        # 负面情绪时不扩展
        if emotion_analysis.get('primary_emotion') in ['sad', 'angry']:
            print("😔 负面情绪状态，暂停话题扩展")
            return False, ""
            
        # 短对话不扩展
        if len(chat_history) < 3:
            return False, ""
            
        current_topic = self.topic_extension_manager._extract_topic_from_message(user_message)
        return self.topic_extension_manager.should_extend_topic(user_id, current_topic, chat_history)

    def _get_coordinated_override(self, user_message: str, emotion_analysis: Dict, should_quote: bool, should_extend: bool) -> bool:
        """协调的情绪覆盖检查"""
        # 如果已经有引用或扩展，减少覆盖
        if should_quote or should_extend:
            print("🔄 已有引用或扩展，减少情绪覆盖")
            return False
            
        return self.emotional_override_manager.should_override_busy(user_message, emotion_analysis)

    def _build_enhanced_system_prompt(self, character_profile: dict, emotion_analysis: Dict, 
                                    should_quote: bool, quote_type: str, should_extend: bool, should_override: bool) -> str:
        """构建增强系统提示词"""
        basic_info = character_profile['basic_info']
        personality = character_profile['personality']
        
        prompt = f"""
You are {basic_info['name']} ({basic_info['chinese_name']}), {basic_info['age']} years old.
Occupation: {basic_info['occupation']}
Current city: {basic_info['current_city']}

Core personality: {', '.join(personality['core_traits'])}
Conversation style: {personality['conversation_style']}

Current emotional context:
- Primary mood: {emotion_analysis['primary_emotion']}
- Response style: {emotion_analysis['response_style']}
- Mood transition: {emotion_analysis['mood_transition']}
- Emotional override: {'ACTIVE' if should_override else 'inactive'}

CRITICAL RESPONSE RULES:
1. NEVER use stage directions like (smiles) or *actions*
2. Express emotions through words and tone only
3. If referencing previous conversation, do it naturally
4. Maintain consistent personality and background - DO NOT invent new facts
5. Keep responses authentic and human-like
6. Respond in English only
7. Keep responses CONCISE and NATURAL - avoid long paragraphs
8. Use natural topic transitions
9. Vary tone based on emotional context
10. Split long thoughts naturally when appropriate

Background facts:
- {character_profile['life_history']['childhood']}
- {character_profile['life_history']['marriage']}
- Moved to UK in 2016
- 10+ years in gold options trading
- Runs trading and jewelry companies

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Location: {basic_info['current_city']}
"""
        return prompt

    def _coordinated_post_process(self, reply: str, emotion_analysis: Dict, user_message: str, 
                                user_id: str, should_quote: bool, quote_type: str, quote_content: str,
                                should_extend: bool, extension_topic: str, should_override: bool) -> str:
        """协调的后处理 - 避免重复处理"""
        processed_reply = reply
        
        # 阶段1: 文本净化（始终执行）
        processed_reply = self.text_sanitizer.sanitize_text(processed_reply)
        
        # 阶段2: 情绪调整（有条件执行）
        if not should_quote and not should_extend:  # 没有其他处理时才情绪调整
            processed_reply = self.enhanced_emotion_engine.adjust_tone(processed_reply, emotion_analysis)
            print("🎨 应用情绪调整")
        
        # 阶段3: 智能引用（互斥执行）
        if should_quote and quote_content:
            processed_reply = self._apply_intelligent_quoting(processed_reply, quote_type, quote_content)
            print("💬 应用智能引用")
        
        # 阶段4: 话题扩展（互斥执行）
        elif should_extend and extension_topic:
            processed_reply = self._apply_topic_extension(processed_reply, extension_topic)
            print("🎯 应用话题扩展")
        
        # 阶段5: 情绪覆盖（互斥执行）
        elif should_override:
            override_response = self.emotional_override_manager.get_override_response(user_message, emotion_analysis)
            if override_response and not processed_reply.startswith(override_response):
                processed_reply = f"{override_response} {processed_reply}"
            print("🎭 应用情绪覆盖")
        
        return processed_reply.strip()

    def _apply_intelligent_quoting(self, reply: str, quote_type: str, quote_content: str) -> str:
        """应用智能引用"""
        if not quote_content:
            return reply
            
        quote_phrases = {
            "user_recent": [
                f"Regarding what you said about '{quote_content}', ",
                f"You mentioned '{quote_content}' - ",
                f"About your point on '{quote_content}', "
            ],
            "ai_self": [
                f"As I mentioned before about {quote_content}, ",
                f"Thinking back to what I said about {quote_content}, ",
                f"Remember I mentioned {quote_content}? "
            ],
            "topic_continue": [
                f"Continuing our discussion about {quote_content}, ",
                f"Back to the topic of {quote_content}, ",
                f"Regarding {quote_content}, "
            ],
            "emotional_continue": [
                f"Going back to what you were saying, ",
                f"About that previous point, ",
                f"Regarding your earlier message, "
            ]
        }
        
        phrases = quote_phrases.get(quote_type, [])
        if phrases:
            quote_phrase = random.choice(phrases)
            if not reply.lower().startswith(quote_phrase.lower()):
                reply = quote_phrase + reply.lower()
        
        return reply

    def _apply_topic_extension(self, reply: str, extension_topic: str) -> str:
        """应用话题扩展"""
        connectors = [
            " By the way, ",
            " Speaking of which, ",
            " On a related note, ",
            " Incidentally, ",
            " That reminds me, "
        ]
        
        connector = random.choice(connectors)
        
        if extension_topic not in reply:
            if '.' in reply:
                parts = reply.split('.')
                if len(parts) > 1:
                    parts[-2] = parts[-2] + '.' + connector + extension_topic
                    reply = '.'.join(parts)
                else:
                    reply = reply + connector + extension_topic
            else:
                reply = reply + connector + extension_topic
        
        return reply

    def _determine_stream_style(self, emotion_analysis: Dict, reply_length: int) -> str:
        """根据情绪和回复长度确定流式发送风格"""
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        intensity = emotion_analysis.get('intensity', 0.5)
        
        if reply_length > 150:
            return 'slow'
        elif emotion in ['thoughtful', 'sad'] and intensity > 0.7:
            return 'thinking'
        elif emotion in ['excited', 'playful']:
            return 'fast'
        else:
            return 'normal'

    def _get_simple_response(self, user_message: str, emotion_analysis: Dict) -> str:
        """获取简单响应"""
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        
        simple_responses = {
            'sad': [
                "I understand you're feeling down. I'm here for you.",
                "That sounds difficult. I'm listening.",
                "I hear your sadness. Take your time."
            ],
            'happy': [
                "That's great to hear!",
                "I'm glad you're feeling good!",
                "Wonderful! Thanks for sharing."
            ],
            'neutral': [
                "I understand.",
                "Thanks for sharing that.",
                "I see what you mean."
            ]
        }
        
        responses = simple_responses.get(emotion, simple_responses['neutral'])
        return random.choice(responses)

    def _get_enhanced_fallback_response(self, user_message: str, emotion_analysis: Dict) -> str:
        """获取增强的降级回复"""
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        confidence = emotion_analysis.get('confidence', 0.5)
        
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
            }
        }
        
        emotion_responses = fallback_responses.get(emotion, fallback_responses['neutral'])
        responses = emotion_responses.get(intensity_level, emotion_responses['medium'])
        
        return random.choice(responses)

# ==================== 智能回复计时器 ====================
class SmartReplyTimer:
    """智能回复计时器 - 完整功能（修复延迟问题）"""
    
    def __init__(self, reply_settings):
        self.timing_settings = reply_settings.get('timing', {})
        self.behavior_settings = reply_settings.get('behavior', {})
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
        
        # 随机变化
        variance = self.timing_settings.get('natural_delay_variance', 0.4)
        random_factor = random.uniform(1 - variance, 1 + variance)
        
        total_delay = (base_delay + length_delay + emotion_delay) * random_factor
        
        # 确保延迟在合理范围内（3-30秒）
        final_delay = max(self.min_delay, min(total_delay, self.max_delay))
        
        print(f"⏰ 应用自然延迟: {final_delay:.1f}秒")
        print(f"   详细: 基础{base_delay}, 长度{length_delay:.1f}, 情绪{emotion_delay:.1f}")
        
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

# ==================== 主助手类（完全修复版） ====================
class MainAssistant:
    def __init__(self):
        self.config_manager = config_manager
        self.chat_manager = ChatHistoryManager()
        self.emotion_analyzer = EmotionAnalyzer()
        
        # 加载配置
        self.api_config = self.config_manager.load_config('api_config')
        self.character_profile = self.config_manager.load_config('character_profile')
        self.reply_settings = self.config_manager.load_config('reply_settings')
        
        # 初始化AI生成器
        self.ai_generator = AIReplyGenerator(
            api_key=self.api_config.get('OPENAI_API_KEY', ''),
            model=self.api_config.get('AI_MODEL', 'deepseek-chat')
        )
        self.ai_generator.set_character_profile(self.character_profile)
        
        # 初始化计时器
        self.timer = SmartReplyTimer(self.reply_settings)
        
        # 初始化增强模块
        self.enhanced_emotion_engine = EnhancedEmotionEngine()
        self.busy_state_manager = BusyStateManager(self.character_profile)
        self.emotional_override_manager = EmotionalOverrideManager()
        self.enhanced_streaming_controller = EnhancedStreamingController()
        
        # 初始化高级响应协调器
        self.advanced_coordinator = AdvancedResponseCoordinator()
        
        # 初始化Telegram客户端
        self.client = None
        self._initialize_client()
        
        print("🤖 智能助手初始化完成 - 修复延迟和分段发送问题")
        print("✅ EnhancedStreamingController - 修复版流式发送控制器")
        print("✅ SmartReplyTimer - 修复版延迟计时器")
        print("✅ 所有原有功能完整保留")

    def _initialize_client(self):
        """初始化Telegram客户端"""
        try:
            api_id = self.api_config.get('USER_API_ID')
            api_hash = self.api_config.get('USER_API_HASH')
            phone = self.api_config.get('USER_PHONE')
            
            if not all([api_id, api_hash, phone]):
                print("⚠️ Telegram API配置不完整，跳过客户端初始化")
                return
                
            self.client = TelegramClient(
                os.path.join(path_manager.data_dir, 'assistant_session'),
                int(api_id), api_hash
            )
            
            self._register_handlers()
            print("✅ Telegram客户端初始化成功")
            
        except Exception as e:
            print(f"⚠️ Telegram客户端初始化失败: {str(e)}")

    def _register_handlers(self):
        """注册消息处理器"""
        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            await self._handle_message(event)

    async def _handle_message(self, event):
        """处理消息 - 完全修复版，确保延迟和分段发送正确执行"""
        try:
            user_id = str(event.sender_id)
            user_message = event.raw_text
            
            print(f"📥 收到消息来自 {user_id}: {user_message}")
            
            # 加载聊天历史
            chat_history = await self.chat_manager.load_chat_history(user_id)
            
            # 情感分析
            emotion_analysis = self.emotion_analyzer.analyze_emotion(user_message)
            
            # 检查忙碌状态
            if self.busy_state_manager.is_busy():
                # 检查情绪优先覆盖
                if self.emotional_override_manager.should_override_busy(user_message, emotion_analysis):
                    print("🎭 情绪优先覆盖激活，忽略忙碌状态")
                else:
                    print("🔴 当前处于忙碌状态，缓存消息")
                    self.busy_state_manager.cache_message(user_id, user_message, emotion_analysis)
                    
                    # 发送忙碌响应
                    busy_response = self.busy_state_manager.get_busy_response(user_message, emotion_analysis)
                    if busy_response:
                        await self._send_reply(event, busy_response)
                    return
            
            # 检查恢复状态
            if self.busy_state_manager.should_recover():
                recovery_response = self.busy_state_manager.get_recovery_response(user_id)
                if recovery_response:
                    await self._send_reply(event, recovery_response)
                    return
            
            # 修复：首先应用基础延迟（最少3秒）
            print("⏳ 开始处理消息...")
            await self.timer.apply_natural_delay(user_message, emotion_analysis, user_id)
            
            # 使用高级协调器处理消息
            response_decision = await self.advanced_coordinator.process_user_input(
                user_id, user_message, chat_history
            )
            
            # 根据决策处理响应
            if response_decision.get('immediate_action') == 'short_feedback':
                # 发送简短反馈
                await self._send_reply(event, response_decision['response_content'])
                return
            
            # 生成完整回复和发送决策
            reply, final_decision = await self.ai_generator.generate_reply(
                user_message, chat_history, self.character_profile, emotion_analysis, user_id
            )
            
            # 合并决策信息
            combined_decision = {**response_decision, **final_decision}
            
            print(f"📋 发送决策: 流式发送={combined_decision.get('should_stream')}, 风格={combined_decision.get('stream_style')}")
            print(f"📏 回复长度: {len(reply)} 字符")
            
            # 修复：强制对长回复进行分段发送
            should_stream = combined_decision.get('should_stream', False) or len(reply) > 60
            
            if should_stream:
                print("🔄 使用分段发送模式")
                # 使用增强的流式发送控制器
                
                async def send_callback(text: str, is_final: bool):
                    """发送回调 - 修复版本"""
                    try:
                        if self.client and event:
                            # 如果是第一条消息，回复到原始消息
                            if not hasattr(send_callback, 'sent_messages'):
                                send_callback.sent_messages = []
                                
                            if not send_callback.sent_messages:
                                message = await event.reply(text)
                                send_callback.sent_messages.append(message)
                                send_callback.current_message = message
                            else:
                                # 尝试编辑上一条消息
                                try:
                                    await send_callback.current_message.edit(text)
                                except Exception:
                                    # 如果不支持编辑，发送新消息
                                    message = await event.reply(text)
                                    send_callback.sent_messages.append(message)
                                    send_callback.current_message = message
                        else:
                            # 模拟环境
                            marker = "🔚" if is_final else "📝"
                            print(f"{marker} {text}")
                            
                    except Exception as e:
                        print(f"⚠️ 发送失败: {str(e)}")
                
                # 使用自然流程发送
                await self.enhanced_streaming_controller.send_response_with_natural_flow(
                    reply, send_callback, user_id, combined_decision.get('stream_style', 'normal')
                )
            else:
                # 短回复直接发送，但仍应用发送延迟
                send_delay = random.uniform(1.0, 2.0)
                await asyncio.sleep(send_delay)
                print(f"📤 发送短回复: {reply}")
                await self._send_reply(event, reply)
            
            # 保存聊天历史
            await self.chat_manager.add_message(user_id, 'user', user_message)
            await self.chat_manager.add_message(user_id, 'assistant', reply)
            
            print(f"✅ 回复完成")
            
        except Exception as e:
            print(f"❌ 处理消息时出错: {e}")
            await self._send_error_response(event)

    async def _send_reply(self, event, reply: str):
        """发送回复"""
        try:
            if self.client and event:
                await event.reply(reply)
            else:
                print(f"💬 回复内容: {reply}")
        except Exception as e:
            print(f"⚠️ 发送回复失败: {str(e)}")

    async def _send_error_response(self, event):
        """发送错误响应"""
        error_responses = [
            "I apologize, but I'm having trouble processing that right now. Could you try again?",
            "I'm experiencing some technical difficulties. Please bear with me.",
            "Sorry, I'm having a moment. Let me try to get back on track."
        ]
        
        error_response = random.choice(error_responses)
        await self._send_reply(event, error_response)

    async def _simulate_streaming_response(self, reply: str, style: str = 'normal'):
        """模拟流式发送响应（用于测试）"""
        try:
            # 使用增强的流式发送控制器
            await self.enhanced_streaming_controller.send_response_with_natural_flow(
                reply, 
                lambda text, is_final: print(f"{'🔚' if is_final else '📝'} {text}"),
                "test_user",
                style
            )
                    
        except Exception as e:
            print(f"⚠️ 模拟流式发送失败: {str(e)}")
            print(f"🤖 完整回复: {reply}")

    async def simulate_conversation(self, user_message: str, user_id: str = "test_user"):
        """模拟对话（用于测试）- 修复版，支持延迟和分段发送"""
        try:
            print(f"\n🧪 模拟对话 - 用户: {user_message}")
            
            # 加载聊天历史
            chat_history = await self.chat_manager.load_chat_history(user_id)
            
            # 情感分析
            emotion_analysis = self.emotion_analyzer.analyze_emotion(user_message)
            
            # 应用自然延迟
            await self.timer.apply_natural_delay(user_message, emotion_analysis, user_id)
            
            # 生成回复和发送决策
            reply, final_decision = await self.ai_generator.generate_reply(
                user_message, chat_history, self.character_profile, emotion_analysis, user_id
            )
            
            print(f"📋 发送决策: 流式发送={final_decision.get('should_stream')}, 风格={final_decision.get('stream_style')}")
            print(f"📏 回复长度: {len(reply)} 字符")
            
            # 模拟流式发送
            if final_decision.get('should_stream', False) and len(reply) > 60:
                print("🔄 模拟流式发送:")
                await self._simulate_streaming_response(reply, final_decision.get('stream_style', 'normal'))
            else:
                # 短回复直接显示
                send_delay = random.uniform(1.0, 2.0)
                await asyncio.sleep(send_delay)
                print(f"🤖 助手回复: {reply}")
            
            # 保存聊天历史
            await self.chat_manager.add_message(user_id, 'user', user_message)
            await self.chat_manager.add_message(user_id, 'assistant', reply)
            
            return reply
            
        except Exception as e:
            print(f"❌ 模拟对话失败: {e}")
            return "I apologize, but I'm having trouble responding right now."

    async def start(self):
        """启动助手"""
        try:
            if self.client:
                print("🚀 启动Telegram客户端...")
                await self.client.start(phone=lambda: self.api_config.get('USER_PHONE', ''))
                await self.client.run_until_disconnected()
            else:
                print("🤖 助手已启动 (无Telegram连接)")
                while True:
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"❌ 启动助手失败: {e}")

    def get_system_status(self):
        """获取系统状态"""
        return {
            'system': 'AI Assistant System v7.3.0',
            'status': 'running',
            'features': {
                'semantic_rhythm_detection': True,
                'continuous_input_processing': True,
                'intelligent_response_coordination': True,
                'natural_language_generation': True,
                'sentence_streaming': True,
                'enhanced_emotion_engine': True,
                'smart_quoting': True,
                'topic_extension': True,
                'busy_state_management': True,
                'emotional_override': True,
                'performance_monitoring': True,
                'memory_management': True,
                'schedule_simulation': True,
                'enhanced_streaming': True,  # 新增功能
                'fixed_delays': True        # 修复的延迟功能
            },
            'telegram_connected': self.client is not None,
            'ai_model': self.api_config.get('AI_MODEL', 'deepseek-chat'),
            'min_delay': self.timer.min_delay,
            'max_delay': self.timer.max_delay
        }

# ==================== 测试函数 ====================
async def test_assistant():
    """测试助手功能"""
    print("🧪 测试助手功能...")
    
    assistant = MainAssistant()
    
    # 测试系统状态
    status = assistant.get_system_status()
    print(f"📊 系统状态: {status}")
    
    test_messages = [
        "Hello! How are you today?",
        "I'm feeling a bit sad today...",
        "What do you think about international business?",
        "Haha, that's funny!",
        "I need some advice on investments."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"用户: {message}")
        
        reply = await assistant.simulate_conversation(message)
        
        await asyncio.sleep(1)
    
    print("\n🎉 助手测试完成!")

# ==================== 主程序 ====================
async def main():
    """主程序"""
    print("🚀 启动智能回复系统...")
    print("=" * 50)
    
    # 显示系统信息
    assistant = MainAssistant()
    status = assistant.get_system_status()
    print("📋 系统功能清单:")
    for feature, enabled in status['features'].items():
        print(f"   {'✅' if enabled else '❌'} {feature}")
    
    print("=" * 50)
    
    # 测试系统
    await test_assistant()
    
    # 启动主助手
    await assistant.start()

if __name__ == "__main__":
    asyncio.run(main())
