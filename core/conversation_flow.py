# -*- coding: utf-8 -*-
"""自然对话流引擎"""
import random
from typing import Dict, List
from collections import defaultdict, deque

class NaturalConversationFlowEngine:
    """
    自然对话流引擎
    
    管理对话的节奏和流畅性
    """
    
    def __init__(self, memory_system=None):
        self.memory_system = memory_system
        self.recent_topics = defaultdict(lambda: deque(maxlen=5))
        self.conversation_depth = defaultdict(int)
        self.last_topic_shift = defaultdict(float)
    
    def make_decision(self, intent: Dict, emotion: Dict, context: Dict) -> Dict:
        """
        决策对话策略
        
        Args:
            intent: 意图分析结果
            emotion: 情感分析结果
            context: 对话上下文
            
        Returns:
            Dict: 对话决策
        """
        user_id = context.get('user_id', 'default')
        current_topic = context.get('current_topic', 'general')
        
        decision = {
            'response_length': 'medium',
            'temperature': 0.8,
            'should_shift_topic': False,
            'should_ask_question': False,
            'should_share_experience': False,
            'empathy_level': 0.5,
            'current_topic': current_topic,
            'topic_depth': 'surface'
        }
        
        # 1. 基于情感决策
        emotion_primary = emotion.get('primary', 'neutral')
        emotion_intensity = emotion.get('intensity', 0.5)
        
        if emotion_primary in ['sad', 'anxiety', 'fear'] and emotion_intensity > 0.6:
            decision['response_length'] = 'short'  # 共情时应简短
            decision['empathy_level'] = 0.9
            decision['temperature'] = 0.7  # 降低随机性
            decision['should_ask_question'] = False  # 不要追问
        elif emotion_primary in ['joy', 'excitement']:
            decision['response_length'] = 'medium'
            decision['empathy_level'] = 0.7
            decision['should_share_experience'] = random.random() < 0.3
        
        # 2. 基于意图决策
        intent_data = intent if isinstance(intent, dict) else {}
        
        if intent_data.get('need_listening'):
            decision['response_length'] = 'short'
            decision['should_ask_question'] = False
            decision['temperature'] = 0.7
        
        if intent_data.get('need_advice'):
            decision['response_length'] = 'medium'
            decision['should_share_experience'] = True
            decision['temperature'] = 0.75
        
        if intent_data.get('need_comfort'):
            decision['empathy_level'] = 0.9
            decision['temperature'] = 0.7
        
        # 3. 话题管理
        if self._should_shift_topic(user_id, current_topic):
            decision['should_shift_topic'] = True
            decision['should_ask_question'] = True
        
        # 4. 对话深度
        depth = self.conversation_depth[user_id]
        if depth < 3:
            decision['topic_depth'] = 'surface'
        elif depth < 7:
            decision['topic_depth'] = 'medium'
        else:
            decision['topic_depth'] = 'deep'
        
        # 更新状态
        self.recent_topics[user_id].append(current_topic)
        self.conversation_depth[user_id] += 1
        
        return decision
    
    def _should_shift_topic(self, user_id: str, current_topic: str) -> bool:
        """
        判断是否应该转换话题
        
        Args:
            user_id: 用户ID
            current_topic: 当前话题
            
        Returns:
            bool: 是否转换
        """
        # 1. 话题重复太多
        recent = list(self.recent_topics[user_id])
        if recent.count(current_topic) >= 3:
            return True
        
        # 2. 对话轮次过多
        if self.conversation_depth[user_id] > 10:
            if random.random() < 0.3:  # 30%概率转换
                return True
        
        return False
    
    def analyze_conversation_rhythm(self, chat_history: List[Dict]) -> Dict:
        """
        分析对话节奏
        
        Args:
            chat_history: 聊天历史
            
        Returns:
            Dict: 节奏分析结果
        """
        if len(chat_history) < 2:
            return {
                'pace': 'normal',
                'user_engagement': 0.5,
                'ai_verbosity': 0.5
            }
        
        recent_history = chat_history[-10:]
        
        # 计算用户消息长度
        user_messages = [msg for msg in recent_history if msg.get('role') == 'user']
        ai_messages = [msg for msg in recent_history if msg.get('role') == 'assistant']
        
        avg_user_length = sum(len(msg.get('content', '')) for msg in user_messages) / max(len(user_messages), 1)
        avg_ai_length = sum(len(msg.get('content', '')) for msg in ai_messages) / max(len(ai_messages), 1)
        
        # 分析节奏
        pace = 'normal'
        if len(user_messages) > 5 and avg_user_length < 20:
            pace = 'fast'  # 用户发消息快且短
        elif avg_user_length > 100:
            pace = 'slow'  # 用户消息长
        
        # 用户参与度
        engagement = min(1.0, len(user_messages) / 5.0)
        
        # AI话多程度
        verbosity = avg_ai_length / 100.0  # 基于100字为基准
        
        return {
            'pace': pace,
            'user_engagement': round(engagement, 2),
            'ai_verbosity': round(min(1.0, verbosity), 2),
            'avg_user_length': int(avg_user_length),
            'avg_ai_length': int(avg_ai_length)
        }
    
    def suggest_response_strategy(self, rhythm: Dict, intent: Dict, emotion: Dict) -> Dict:
        """
        推荐回复策略
        
        Args:
            rhythm: 节奏分析
            intent: 意图分析
            emotion: 情感分析
            
        Returns:
            Dict: 回复策略
        """
        strategy = {
            'style': 'balanced',
            'length_target': 60,  # 字数
            'use_question': False,
            'use_emoji': True,
            'share_personal': False
        }
        
        # 根据节奏调整
        if rhythm['pace'] == 'fast':
            strategy['style'] = 'brief'
            strategy['length_target'] = 30
        elif rhythm['pace'] == 'slow':
            strategy['style'] = 'detailed'
            strategy['length_target'] = 100
        
        # 根据参与度调整
        if rhythm['user_engagement'] > 0.7:
            strategy['use_question'] = random.random() < 0.4
        
        # 根据AI话多程度调整
        if rhythm['ai_verbosity'] > 0.8:
            strategy['length_target'] = int(strategy['length_target'] * 0.7)
        
        # 根据情感调整
        emotion_primary = emotion.get('primary', 'neutral')
        if emotion_primary in ['sad', 'anxiety']:
            strategy['use_emoji'] = False
            strategy['length_target'] = int(strategy['length_target'] * 0.8)
        
        return strategy
    
    def reset_conversation(self, user_id: str):
        """
        重置对话状态
        
        Args:
            user_id: 用户ID
        """
        self.recent_topics[user_id].clear()
        self.conversation_depth[user_id] = 0
