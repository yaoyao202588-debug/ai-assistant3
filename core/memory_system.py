# -*- coding: utf-8 -*-
"""三层记忆系统"""
import json
import os
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

class ThreeTierMemorySystem:
    """
    三层记忆系统
    
    - 工作记忆 (Working Memory): 最近5-10轮对话
    - 情景记忆 (Episodic Memory): 重要对话片段
    - 语义记忆 (Semantic Memory): 用户画像和长期知识
    """
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # 三层记忆存储
        self.working_memory = defaultdict(list)  # user_id -> [messages]
        self.episodic_memory = defaultdict(list)  # user_id -> [episodes]
        self.semantic_memory = defaultdict(dict)  # user_id -> {profile}
        
        self.working_memory_size = 5
        self.episodic_memory_max = 50
        
    def process_conversation_turn(self, user_id: str, user_msg: str, 
                                  ai_response: str, emotional_context: Dict, 
                                  intent_context: Dict):
        """处理一轮对话"""
        # 1. 更新工作记忆
        self._update_working_memory(user_id, user_msg, ai_response)
        
        # 2. 判断是否值得存入情景记忆
        if self._is_important_episode(user_msg, emotional_context, intent_context):
            self._add_to_episodic_memory(user_id, user_msg, ai_response, emotional_context)
        
        # 3. 更新语义记忆
        self._update_semantic_memory(user_id, user_msg, intent_context)
    
    def _update_working_memory(self, user_id: str, user_msg: str, ai_response: str):
        """更新工作记忆"""
        self.working_memory[user_id].append({
            'role': 'user',
            'content': user_msg,
            'timestamp': datetime.now().isoformat()
        })
        self.working_memory[user_id].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保持大小限制
        if len(self.working_memory[user_id]) > self.working_memory_size * 2:
            self.working_memory[user_id] = self.working_memory[user_id][-self.working_memory_size * 2:]
    
    def _is_important_episode(self, message: str, emotional_context: Dict, 
                             intent_context: Dict) -> bool:
        """判断是否为重要情景"""
        # 1. 情感强度高
        if emotional_context.get('intensity', 0) > 0.7:
            return True
        
        # 2. 紧急程度高
        if intent_context.get('urgency_level', 0) > 0.7:
            return True
        
        # 3. 包含个人信息
        personal_keywords = ['我', '工作', '家', '朋友', '喜欢', '不喜欢']
        if any(keyword in message for keyword in personal_keywords):
            return True
        
        return False
    
    def _add_to_episodic_memory(self, user_id: str, user_msg: str, 
                                ai_response: str, emotional_context: Dict):
        """添加到情景记忆"""
        episode = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'user_message': user_msg,
            'ai_response': ai_response,
            'emotion': emotional_context.get('primary', 'neutral'),
            'summary': user_msg[:100]  # 简化的摘要
        }
        
        self.episodic_memory[user_id].append(episode)
        
        # 保持大小限制
        if len(self.episodic_memory[user_id]) > self.episodic_memory_max:
            self.episodic_memory[user_id] = self.episodic_memory[user_id][-self.episodic_memory_max:]
    
    def _update_semantic_memory(self, user_id: str, message: str, 
                               intent_context: Dict):
        """更新语义记忆"""
        if user_id not in self.semantic_memory:
            self.semantic_memory[user_id] = {
                'personal_info': {},
                'preferences': {},
                'relationship_stage': '初识'
            }
        
        # 提取个人信息关键词
        if '工作' in message or 'work' in message.lower():
            self.semantic_memory[user_id]['personal_info']['has_work_topic'] = True
        
        # 更新沟通偏好
        if intent_context.get('social_need'):
            social_need = intent_context['social_need']
            if 'communication_style' not in self.semantic_memory[user_id]['preferences']:
                self.semantic_memory[user_id]['preferences']['communication_style'] = social_need
    
    def retrieve_relevant_memories(self, user_id: str, max_working: int = 3,
                                   max_episodic: int = 2, max_semantic: int = 5) -> Dict:
        """检索相关记忆"""
        return {
            'working': self.working_memory.get(user_id, [])[-max_working*2:],
            'episodic': self.episodic_memory.get(user_id, [])[-max_episodic:],
            'semantic': self.semantic_memory.get(user_id, {})
        }
    
    def save_to_disk(self, user_id: str):
        """保存到磁盘"""
        user_data = {
            'working_memory': self.working_memory.get(user_id, []),
            'episodic_memory': self.episodic_memory.get(user_id, []),
            'semantic_memory': self.semantic_memory.get(user_id, {})
        }
        
        filepath = os.path.join(self.data_dir, f'{user_id}_memory.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    
    def load_from_disk(self, user_id: str):
        """从磁盘加载"""
        filepath = os.path.join(self.data_dir, f'{user_id}_memory.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                self.working_memory[user_id] = user_data.get('working_memory', [])
                self.episodic_memory[user_id] = user_data.get('episodic_memory', [])
                self.semantic_memory[user_id] = user_data.get('semantic_memory', {})
