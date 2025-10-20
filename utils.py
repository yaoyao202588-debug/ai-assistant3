# utils.py - 完整优化版（修复延迟和分段发送问题）
import json
import os
import re
import time
import random
import asyncio
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict, deque

# ==================== 性能监控器（新增）====================

class PerformanceMonitor:
    """性能监控器 - 监控系统性能指标"""
    
    def __init__(self):
        self.metrics = {
            'response_times': deque(maxlen=100),
            'error_rates': deque(maxlen=100),
            'conversation_lengths': deque(maxlen=100),
            'api_calls': deque(maxlen=100),
            'memory_usage': deque(maxlen=100)
        }
        self.start_time = time.time()
        self.error_count = 0
        self.success_count = 0
        
    def record_response_time(self, response_time: float):
        """记录响应时间"""
        self.metrics['response_times'].append(response_time)
    
    def record_error(self, error_type: str = "general"):
        """记录错误"""
        self.metrics['error_rates'].append(1)
        self.error_count += 1
    
    def record_success(self):
        """记录成功"""
        self.metrics['error_rates'].append(0)
        self.success_count += 1
    
    def record_conversation_length(self, length: int):
        """记录对话长度"""
        self.metrics['conversation_lengths'].append(length)
    
    def record_api_call(self, duration: float):
        """记录API调用"""
        self.metrics['api_calls'].append(duration)
    
    def record_memory_usage(self, usage_mb: float):
        """记录内存使用"""
        self.metrics['memory_usage'].append(usage_mb)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        report = {
            'uptime_hours': round(uptime / 3600, 2),
            'total_conversations': len(self.metrics['conversation_lengths']),
            'total_api_calls': len(self.metrics['api_calls']),
            'error_count': self.error_count,
            'success_count': self.success_count,
            'success_rate': round(self.success_count / max(1, self.success_count + self.error_count) * 100, 2)
        }
        
        # 响应时间统计
        if self.metrics['response_times']:
            response_times = list(self.metrics['response_times'])
            report.update({
                'avg_response_time': round(sum(response_times) / len(response_times), 2),
                'max_response_time': round(max(response_times), 2),
                'min_response_time': round(min(response_times), 2),
                'response_time_95th': round(sorted(response_times)[int(len(response_times) * 0.95)], 2)
            })
        
        # API调用统计
        if self.metrics['api_calls']:
            api_calls = list(self.metrics['api_calls'])
            report.update({
                'avg_api_duration': round(sum(api_calls) / len(api_calls), 2),
                'api_calls_per_hour': round(len(api_calls) / (uptime / 3600), 2)
            })
        
        # 对话长度统计
        if self.metrics['conversation_lengths']:
            conv_lengths = list(self.metrics['conversation_lengths'])
            report.update({
                'avg_conversation_length': round(sum(conv_lengths) / len(conv_lengths), 1),
                'max_conversation_length': max(conv_lengths)
            })
        
        # 内存使用统计
        if self.metrics['memory_usage']:
            memory_usage = list(self.metrics['memory_usage'])
            report.update({
                'avg_memory_usage_mb': round(sum(memory_usage) / len(memory_usage), 2),
                'max_memory_usage_mb': round(max(memory_usage), 2)
            })
        
        return report
    
    def get_health_status(self) -> str:
        """获取健康状态"""
        report = self.get_performance_report()
        
        error_rate = report.get('success_rate', 100)
        avg_response_time = report.get('avg_response_time', 0)
        
        if error_rate < 80:
            return 'unhealthy'
        elif error_rate < 90 or avg_response_time > 10:
            return 'degraded'
        else:
            return 'healthy'
    
    def reset_metrics(self):
        """重置指标"""
        self.metrics = {
            'response_times': deque(maxlen=100),
            'error_rates': deque(maxlen=100),
            'conversation_lengths': deque(maxlen=100),
            'api_calls': deque(maxlen=100),
            'memory_usage': deque(maxlen=100)
        }
        self.error_count = 0
        self.success_count = 0
        self.start_time = time.time()

# ==================== 记忆管理器 ====================

class MemoryManager:
    """记忆管理器 - 管理对话记忆和上下文"""
    
    def __init__(self):
        self.user_memories = defaultdict(dict)
        self.conversation_contexts = defaultdict(lambda: deque(maxlen=10))
        self.important_facts = defaultdict(list)
        
    def add_memory(self, user_id: str, memory_type: str, content: str, importance: int = 1):
        """添加记忆"""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = {}
            
        if memory_type not in self.user_memories[user_id]:
            self.user_memories[user_id][memory_type] = []
            
        memory_item = {
            'content': content,
            'importance': importance,
            'timestamp': datetime.now().isoformat(),
            'access_count': 0
        }
        
        self.user_memories[user_id][memory_type].append(memory_item)
        
        if importance >= 3:
            self.important_facts[user_id].append(content)
            
    def get_relevant_memories(self, user_id: str, context: str, max_memories: int = 3) -> List[str]:
        """获取相关记忆"""
        if user_id not in self.user_memories:
            return []
            
        relevant_memories = []
        context_words = set(context.lower().split())
        
        for memory_type, memories in self.user_memories[user_id].items():
            for memory in memories:
                memory_words = set(memory['content'].lower().split())
                common_words = context_words.intersection(memory_words)
                
                if len(common_words) >= 1:  # 至少有一个共同词
                    relevance_score = len(common_words) + memory['importance']
                    relevant_memories.append((relevance_score, memory['content']))
                    memory['access_count'] += 1
                    
        # 按相关性排序并返回
        relevant_memories.sort(reverse=True)
        return [memory for score, memory in relevant_memories[:max_memories]]
    
    def update_conversation_context(self, user_id: str, message: str, role: str):
        """更新对话上下文"""
        context_item = {
            'role': role,
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        self.conversation_contexts[user_id].append(context_item)
        
    def get_conversation_context(self, user_id: str, max_items: int = 5) -> List[Dict]:
        """获取对话上下文"""
        return list(self.conversation_contexts[user_id])[-max_items:]
    
    def get_important_facts(self, user_id: str) -> List[str]:
        """获取重要事实"""
        return self.important_facts.get(user_id, [])[:5]

# ==================== 自然语言生成器 ====================

class NaturalLanguageGenerator:
    """自然语言生成器 - 让AI回复更口语化"""
    
    def __init__(self):
        self.filler_words = ['嗯', '啊', '那个', '就是', '其实', '话说', '呃', '嘛']
        self.transition_phrases = {
            'continue': ['然后呢', '接着说吧', '后来怎样了', '再然后'],
            'empathy': ['真的假的', '天呐', '不会吧', '太不容易了', '哎呀'],
            'encourage': ['你继续说', '我在听', '然后呢', '嗯嗯', '明白了'],
            'agreement': ['确实', '没错', '对的', '就是这样', '我也觉得']
        }
        self.sentence_breakers = ['。', '！', '？', '...', '～', '~', '♪']
        self.emotional_suffixes = {
            'happy': ['～', '！', '♪', '💫', '😊'],
            'sad': ['...', '。', '唉', '😔', '💔'],
            'excited': ['！', '！！', '💫', '🔥', '😄'],
            'calm': ['。', '～', '', '🙂'],
            'caring': ['呀', '呢', '喔', '❤️', '🤗'],
            'neutral': ['。', '～', '']
        }
        self._language = 'Chinese'  # default based on current content

    def set_language(self, language: str):
        """设置语言偏好，支持 English/Chinese 简单分流"""
        lang = (language or '').lower()
        if 'en' in lang:
            self._language = 'English'
        else:
            self._language = 'Chinese'
        
    def make_conversational(self, text: str) -> str:
        """让文本更口语化"""
        if not text or len(text.strip()) < 2:
            return text
            
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return self._process_single_sentence(text, 0, 1)
            
        conversational_sentences = []
        
        for i, sentence in enumerate(sentences):
            conv_sentence = self._process_single_sentence(sentence, i, len(sentences))
            conversational_sentences.append(conv_sentence)
            
        result = ''.join(conversational_sentences)
        return result
    
    def _split_sentences(self, text: str) -> List[str]:
        """智能分割句子"""
        if self._language == 'English':
            sentences = re.split(r'([.!?])', text)
        else:
            # 保护一些特殊标点不被分割（中文）
            text = re.sub(r'([！？])', r'\1。', text)
            sentences = re.split(r'([。！？…])', text)
        
        # 重新组合标点
        result = []
        i = 0
        while i < len(sentences):
            if sentences[i].strip():
                if i + 1 < len(sentences) and sentences[i+1] in ['。', '！', '？', '…']:
                    combined = sentences[i] + sentences[i+1]
                    result.append(combined)
                    i += 2
                else:
                    result.append(sentences[i])
                    i += 1
            else:
                i += 1
                
        return [s for s in result if s.strip()]
    
    def _process_single_sentence(self, sentence: str, index: int, total: int) -> str:
        """处理单个句子使其更口语化"""
        sentence = sentence.strip()
        if not sentence:
            return ""
            
        # 随机添加填充词（只在某些位置）
        if index > 0 and random.random() < 0.25:
            if random.random() < 0.6 and len(sentence) > 4:
                filler = random.choice(self.filler_words)
                sentence = filler + '，' + sentence
        
        # 处理句尾，使其更自然
        if self._language == 'English':
            if not sentence.endswith(('.', '!', '?')):
                sentence += random.choice(['.', '...', '!'])
        else:
            if not any(sentence.endswith(end) for end in self.sentence_breakers):
                ending = random.choice(['。', '～', '...', '！'])
                sentence += ending
            
        # 随机添加表情符号（概率较低）
        if random.random() < 0.15:
            emotions = ['😊', '😂', '🤔', '❤️', '👉', '🙏']
            if any(sentence.endswith(end) for end in ['。', '！', '？']):
                sentence = sentence[:-1] + random.choice(emotions) + sentence[-1]
                
        return sentence
    
    def add_emotional_color(self, text: str, emotion: str = 'neutral') -> str:
        """根据情绪添加语气词"""
        if not text:
            return text
            
        suffixes = self.emotional_suffixes.get(emotion, self.emotional_suffixes['neutral'])
        
        # 在适当位置添加语气词
        if random.random() < 0.3:
            if text.endswith(('。', '！', '？')):
                text = text[:-1] + random.choice(suffixes) + text[-1]
            else:
                text += random.choice(suffixes)
                
        return text
    
    def insert_conversational_elements(self, text: str, context: Dict = None) -> str:
        """插入对话元素"""
        if len(text) < 10:
            return text
            
        # 在长文本中随机插入过渡词
        sentences = self._split_sentences(text)
        if len(sentences) > 2:
            # 随机选择位置插入过渡词
            if random.random() < 0.4:
                insert_pos = random.randint(1, len(sentences)-1)
                transition = random.choice(self.transition_phrases['continue'])
                sentences[insert_pos] = transition + '，' + sentences[insert_pos]
                
        return ''.join(sentences)

# ==================== 逐句发送管理器（增强版） ====================

class SentenceStreamer:
    """逐句发送管理器 - 模拟人类打字和思考（修复延迟问题）"""
    
    def __init__(self):
        # 修复：调整打字速度，使其更真实
        self.typing_speeds = {
            'fast': (0.04, 0.10),    # 每个字符的打字时间（秒）- 修复：增加延迟
            'normal': (0.08, 0.15),  # 修复：增加正常速度的延迟
            'slow': (0.12, 0.25),    # 修复：增加慢速的延迟
            'thinking': (0.20, 0.40) # 修复：增加思考状态的延迟
        }
        # 修复：增加句间延迟
        self.sentence_delays = {
            'short': (1.2, 2.0),     # 句间延迟（秒）- 修复：增加延迟
            'normal': (1.8, 3.0),    # 修复：增加正常延迟
            'long': (2.5, 4.5),      # 修复：增加长延迟
            'thinking': (3.0, 6.0)   # 修复：增加思考延迟
        }
        # 新增：打字状态跟踪
        self.typing_status = defaultdict(bool)
    
    async def simulate_typing_status(self, client, chat, duration: float):
        """模拟打字状态"""
        if client and chat:
            try:
                await client.send_action(chat, action='typing')
                self.typing_status[chat] = True
                await asyncio.sleep(min(duration, 5.0))  # 最多显示5秒打字状态
            except Exception as e:
                print(f"⚠️ 模拟打字状态失败: {e}")
    
    async def stream_response(self, full_response: str, 
                            message_callback: Callable[[str, bool], None],
                            style: str = 'normal',
                            typing_callback: Callable[[float], None] = None) -> List[str]:
        """逐句流式发送响应 - 增强版（修复延迟问题）"""
        sentences = self._split_into_streamable_sentences(full_response)
        if not sentences:
            return []
            
        sent_sentences = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            # 计算本句的打字时间 - 修复：确保有最小延迟
            typing_delay = max(0.5, self._calculate_typing_delay(sentence, i, len(sentences), style))
            
            # 计算句间思考时间 - 修复：确保有最小延迟
            if i > 0:
                sentence_delay = max(1.0, self._calculate_sentence_delay(i, len(sentences), style))
                
                # 在句间延迟期间模拟打字状态
                if typing_callback:
                    await typing_callback(sentence_delay)
                else:
                    await asyncio.sleep(sentence_delay)
            
            # 模拟打字效果（对长句子）- 修复：增加打字效果的概率
            if len(sentence) > 6 and random.random() < 0.8:
                await self._simulate_typing(sentence, message_callback, typing_delay, i, typing_callback)
            else:
                # 直接发送短句，但仍模拟打字
                if typing_callback:
                    await typing_callback(typing_delay * 0.7)
                else:
                    await asyncio.sleep(typing_delay * 0.7)
                    
                if message_callback:
                    await message_callback(sentence, is_final=(i == len(sentences)-1))
            
            sent_sentences.append(sentence)
            
        return sent_sentences
    
    def set_language(self, language: str):
        lang = (language or '').lower()
        self._language = 'English' if 'en' in lang else 'Chinese'

    def _split_into_streamable_sentences(self, text: str) -> List[str]:
        """将文本分割成适合流式发送的句子"""
        if not text:
            return []
            
        # 基础分割
        if getattr(self, '_language', 'Chinese') == 'English':
            sentences = re.split(r'([.!?])', text)
        else:
            sentences = re.split(r'([。！？…])', text)
        result = []
        i = 0
        
        while i < len(sentences):
            if sentences[i].strip():
                current_sentence = sentences[i].strip()
                
                # 合并标点
                if i + 1 < len(sentences) and sentences[i+1] in ['。', '！', '？', '…', '.', '!', '?']:
                    current_sentence += sentences[i+1]
                    i += 1
                
                # 如果句子太长，进一步分割 - 修复：降低分割阈值
                if len(current_sentence) > 20:  # 修复：从25降低到20
                    sub_sentences = self._split_long_sentence(current_sentence)
                    result.extend(sub_sentences)
                else:
                    result.append(current_sentence)
                    
            i += 1
            
        return [s for s in result if s.strip()]
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """分割长句子"""
        # 按逗号、分号等分割
        parts = re.split(r'([，,；;,:])', sentence)
        if len(parts) == 1:
            # 没有明显分割点，按长度分割
            if len(sentence) > 30:  # 修复：从35降低到30
                mid_point = len(sentence) // 2
                # 找最近的空间分割
                space_pos = sentence.find(' ', mid_point - 5)
                if space_pos != -1 and space_pos > len(sentence) * 0.3:
                    return [sentence[:space_pos], sentence[space_pos:].strip()]
                else:
                    return [sentence[:mid_point], sentence[mid_point:]]
            else:
                return [sentence]
                
        result = []
        current_part = ""
        
        for i in range(0, len(parts), 2):
            if i < len(parts):
                segment = parts[i]
                if i + 1 < len(parts):
                    segment += parts[i+1]
                    
                if current_part:
                    current_part += segment
                    if len(current_part) >= 12:  # 修复：从15降低到12
                        result.append(current_part)
                        current_part = ""
                else:
                    if len(segment) >= 10:  # 修复：从12降低到10
                        result.append(segment)
                    else:
                        current_part = segment
                
        if current_part:
            if result and len(result[-1] + current_part) < 25:  # 修复：从30降低到25
                result[-1] += current_part
            else:
                result.append(current_part)
                
        return result if result else [sentence]
    
    def _calculate_typing_delay(self, sentence: str, sentence_index: int, 
                              total_sentences: int, style: str) -> float:
        """计算打字延迟 - 修复：增加基础延迟"""
        base_speed = self.typing_speeds.get(style, self.typing_speeds['normal'])
        chars_per_second = 1 / random.uniform(base_speed[0], base_speed[1])
        
        # 根据句子位置调整速度
        if sentence_index == 0:
            # 第一句可能稍慢（思考）
            chars_per_second *= random.uniform(0.6, 0.8)  # 修复：进一步降低第一句速度
        elif sentence_index == total_sentences - 1:
            # 最后一句可能稍快
            chars_per_second *= random.uniform(1.1, 1.3)
            
        # 根据句子复杂度调整
        complexity = self._calculate_sentence_complexity(sentence)
        chars_per_second *= (1.0 - complexity * 0.3)  # 修复：增加复杂度影响
        
        delay = len(sentence) / chars_per_second
        return max(0.8, min(delay, 12.0))  # 修复：限制在0.8-12秒之间
    
    def _calculate_sentence_delay(self, sentence_index: int, total_sentences: int, style: str) -> float:
        """计算句间延迟 - 修复：增加基础延迟"""
        base_delay = self.sentence_delays.get(style, self.sentence_delays['normal'])
        delay = random.uniform(base_delay[0], base_delay[1])
        
        # 根据上下文调整延迟
        if sentence_index == 0:
            delay *= random.uniform(1.3, 2.0)  # 修复：开始前更多思考
        elif sentence_index == total_sentences - 1:
            delay *= random.uniform(0.7, 0.9)   # 最后一句间隔短些
            
        # 随机长时间思考 - 修复：增加概率
        if random.random() < 0.25:  # 修复：从0.15增加到0.25
            delay *= random.uniform(1.8, 3.5)  # 修复：增加长时间思考的范围
            
        return max(1.2, min(delay, 15.0))  # 修复：限制在1.2-15秒之间
    
    def _calculate_sentence_complexity(self, sentence: str) -> float:
        """计算句子复杂度"""
        # 简单的复杂度评估
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', sentence))
        total_chars = len(sentence)
        
        if total_chars == 0:
            return 0.0
            
        chinese_ratio = chinese_chars / total_chars
        comma_count = sentence.count('，') + sentence.count(',')
        
        complexity = (1.0 - chinese_ratio) * 0.4 + min(comma_count * 0.15, 0.4)  # 修复：增加复杂度权重
        return min(complexity, 1.0)
    
    async def _simulate_typing(self, sentence: str, message_callback: Callable, 
                             total_delay: float, sentence_index: int, typing_callback: Callable = None):
        """模拟打字效果 - 修复：增加打字效果"""
        # 对短句子或特定情况不模拟打字
        if len(sentence) <= 3 or random.random() < 0.2:  # 修复：降低不模拟打字的概率
            if typing_callback:
                await typing_callback(total_delay * 0.6)  # 修复：增加延迟比例
            await message_callback(sentence, is_final=False)
            return
            
        words = list(sentence)
        current_display = ""
        typed_chars = 0
        
        # 修复：增加打字效果的随机性
        for i, char in enumerate(words):
            current_display += char
            typed_chars += 1
            
            # 只在特定时机回调，减少频繁更新 - 修复：调整更新频率
            should_update = (
                i == len(words) - 1 or  # 最后一个字符
                typed_chars >= 2 or     # 修复：从3降低到2个字符
                char in ['，', '。', '！', '？', ' '] or  # 标点符号和空格后
                random.random() < 0.4   # 修复：从0.3增加到0.4
            )
            
            if should_update and message_callback:
                await message_callback(current_display, is_final=False)
                typed_chars = 0
            
            # 计算这个字符的延迟 - 修复：增加延迟随机性
            char_delay = total_delay / len(sentence) * random.uniform(0.6, 1.4)
            if typing_callback and i % 2 == 0:  # 修复：每2个字符模拟一次打字状态
                await typing_callback(char_delay)
            else:
                await asyncio.sleep(char_delay)
        
        # 确保最终显示完整句子
        if message_callback:
            await message_callback(sentence, is_final=False)

# ==================== 增强文本处理器 ====================

class EnhancedTextProcessor:
    """增强文本处理器 - 支持智能分割和语义分析"""
    
    def __init__(self):
        self.sentence_enders = ['.', '!', '?', '。', '！', '？']
        self.discourse_markers = [
            'however', 'but', 'and', 'so', 'then', 'therefore',
            'meanwhile', 'additionally', 'furthermore', 'consequently',
            'although', 'though', 'nevertheless', 'moreover'
        ]
        self.natural_generator = NaturalLanguageGenerator()
        
    def semantic_split(self, text: str, max_segments: int = 3) -> List[str]:
        """基于语义分割文本"""
        if len(text) < 80:  # 修复：降低分割阈值
            return [text]
            
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            return [text]
            
        semantic_groups = self._group_semantically(sentences)
        
        # 确保每组不超过最大分段数
        final_segments = []
        for group in semantic_groups:
            segment = ' '.join(group)
            if len(segment) > 40:  # 修复：确保分段有足够内容，降低阈值
                final_segments.append(segment)
                
        # 如果分段太多，合并较小的分段
        while len(final_segments) > max_segments:
            shortest_indices = sorted(range(len(final_segments)), 
                                    key=lambda i: len(final_segments[i]))[:2]
            shortest_indices.sort(reverse=True)
            
            merged = f"{final_segments[shortest_indices[1]]} {final_segments[shortest_indices[0]]}"
            final_segments.pop(shortest_indices[0])
            final_segments[shortest_indices[1]] = merged
            
        return final_segments if final_segments else [text]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割成句子"""
        sentence_endings = r'[.!?。！？]+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _group_semantically(self, sentences: List[str]) -> List[List[str]]:
        """基于语义分组句子"""
        if len(sentences) <= 1:
            return [sentences]
            
        groups = []
        current_group = [sentences[0]]
        
        for i in range(1, len(sentences)):
            current_sentence = sentences[i]
            
            # 检查语义连续性
            if self._are_sentences_connected(current_group[-1], current_sentence):
                current_group.append(current_sentence)
            else:
                groups.append(current_group)
                current_group = [current_sentence]
                
        if current_group:
            groups.append(current_group)
            
        return groups
    
    def _are_sentences_connected(self, sent1: str, sent2: str) -> bool:
        """检查两个句子是否语义连接"""
        pronoun_references = ['它', '这', '那', '这些', '那些', '他', '她', '他们']
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
    
    def calculate_reading_time(self, text: str, wpm: int = 200) -> float:
        """计算阅读时间（分钟）"""
        words = len(text.split())
        return words / wpm
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """提取关键词"""
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这个', '那个'}
        words = text.lower().split()
        
        word_freq = defaultdict(int)
        for word in words:
            if (len(word) > 1 and 
                word not in stop_words and 
                re.match(r'^[\u4e00-\u9fff_a-zA-Z0-9]+$', word)):
                word_freq[word] += 1
                
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:max_keywords]]

# ==================== 语义节奏检测机制 ====================

class SemanticRhythmDetector:
    """语义节奏检测器 - 判断用户是在连续输入还是等待回应"""
    
    def __init__(self):
        self.user_message_buffer = defaultdict(list)
        self.last_message_time = defaultdict(float)
        self.short_feedback_sent = defaultdict(bool)
        self.conversation_states = defaultdict(lambda: {
            'waiting_for_completion': False,
            'continuous_input_count': 0,
            'last_short_feedback_time': 0,
            'pending_messages': []
        })
        
    def analyze_message_rhythm(self, user_id: str, message: str, timestamp: float = None) -> Dict[str, Any]:
        """分析消息节奏"""
        if timestamp is None:
            timestamp = time.time()
            
        state = self.conversation_states[user_id]
        time_since_last = timestamp - self.last_message_time[user_id] if self.last_message_time[user_id] else float('inf')
        
        # 判断是否为连续输入 - 修复：增加连续输入的时间阈值
        is_continuous = time_since_last < 4.0  # 修复：从3秒增加到4秒
        is_semantically_complete = self._is_semantically_complete(message)
        should_hold_reply = False
        
        if is_continuous or not is_semantically_complete:
            should_hold_reply = True
            state['waiting_for_completion'] = True
            state['continuous_input_count'] += 1
        else:
            state['waiting_for_completion'] = False
            state['continuous_input_count'] = 0
            self.short_feedback_sent[user_id] = False
            
        # 添加到待处理消息列表
        state['pending_messages'].append({
            'content': message,
            'timestamp': timestamp,
            'is_continuous': is_continuous
        })
        
        # 限制待处理消息数量
        if len(state['pending_messages']) > 10:
            state['pending_messages'] = state['pending_messages'][-10:]
        
        # 更新最后消息时间
        self.last_message_time[user_id] = timestamp
        
        return {
            'should_hold_reply': should_hold_reply,
            'is_continuous_input': is_continuous,
            'is_semantically_complete': is_semantically_complete,
            'continuous_count': state['continuous_input_count'],
            'time_since_last': time_since_last
        }
    
    def _is_semantically_complete(self, message: str) -> bool:
        """判断消息是否语义完整"""
        sentence_enders = ['.', '!', '?', '。', '！', '？', '…', '...']
        discourse_continuations = [
            '然后', '接着', '而且', '另外', '还有', '不过', '但是', 
            '虽然', '因为', '所以', '如果', '当', '然后呢', '接着呢',
            'and', 'but', 'however', 'so', 'then', 'because', 'if', 'when'
        ]
        
        message_clean = message.strip()
        
        # 如果以结束标点结尾，通常表示完整
        if any(message_clean.endswith(ender) for ender in sentence_enders):
            return True
            
        # 如果包含延续性词语，可能不完整
        if any(cont in message_clean for cont in discourse_continuations):
            return False
            
        # 短消息且没有结束标点，可能不完整 - 修复：调整阈值
        if len(message_clean) < 8 and not any(ender in message_clean for ender in sentence_enders):  # 修复：从10降低到8
            return False
            
        # 检查是否是疑问句
        if any(message_clean.endswith(q) for q in ['?', '？', '吗', '呢', '吧']):
            return True
            
        return True
    
    def should_send_short_feedback(self, user_id: str) -> Tuple[bool, str]:
        """判断是否应该发送简短反馈"""
        state = self.conversation_states[user_id]
        current_time = time.time()
        
        # 检查条件：连续输入超过2条，且10秒内没有发送过简短反馈
        if (state['continuous_input_count'] >= 2 and 
            not self.short_feedback_sent[user_id] and
            current_time - state['last_short_feedback_time'] > 10.0):
            
            state['last_short_feedback_time'] = current_time
            self.short_feedback_sent[user_id] = True
            
            feedback_options = [
                "嗯，我在听~",
                "好像挺累的…你继续说。",
                "嗯哼，怎么啦？",
                "听着呢，你慢慢说~",
                "然后呢？",
                "我在听，你继续~",
                "明白了，继续说吧~",
                "嗯嗯，还有呢？"
            ]
            
            return True, random.choice(feedback_options)
            
        return False, ""
    
    def get_pending_messages(self, user_id: str) -> List[Dict]:
        """获取待处理消息"""
        state = self.conversation_states[user_id]
        return state['pending_messages']
    
    def clear_pending_messages(self, user_id: str):
        """清除待处理消息"""
        state = self.conversation_states[user_id]
        state['pending_messages'] = []
        state['waiting_for_completion'] = False
        self.short_feedback_sent[user_id] = False
        
    def get_conversation_state(self, user_id: str) -> Dict[str, Any]:
        """获取对话状态"""
        state = self.conversation_states[user_id]
        return {
            'waiting_for_completion': state['waiting_for_completion'],
            'continuous_input_count': state['continuous_input_count'],
            'pending_message_count': len(state['pending_messages']),
            'last_short_feedback_time': state['last_short_feedback_time']
        }

# ==================== 连续输入处理器 ====================

class ContinuousInputProcessor:
    """连续输入处理器 - 合并和优化连续消息"""
    
    def __init__(self):
        self.text_processor = EnhancedTextProcessor()
        
    def merge_continuous_messages(self, messages: List[Dict]) -> str:
        """合并连续消息"""
        if not messages:
            return ""
            
        if len(messages) == 1:
            return messages[0]['content']
            
        # 提取所有消息内容
        contents = [msg['content'] for msg in messages]
        
        # 语义合并
        merged_text = self._semantic_merge(contents)
        
        return merged_text
    
    def _semantic_merge(self, contents: List[str]) -> str:
        """语义合并多个消息内容"""
        if len(contents) == 1:
            return contents[0]
            
        # 情绪词保留
        emotional_words = ['唉', '哈哈', '呜呜', '唉呀', '天啊', '真的', '好累', '开心', '难过', '生气']
        emotional_segments = []
        
        # 普通内容合并
        normal_segments = []
        
        for content in contents:
            content_clean = content.strip()
            # 检查是否是情绪表达
            is_emotional = (any(emo_word in content_clean for emo_word in emotional_words) and 
                          len(content_clean) <= 8)
            
            if is_emotional:
                emotional_segments.append(content_clean)
            else:
                normal_segments.append(content_clean)
        
        # 构建合并文本
        merged_parts = []
        
        # 添加情绪表达
        if emotional_segments:
            merged_parts.append("，".join(emotional_segments))
            
        # 添加主要内容
        if normal_segments:
            main_content = " ".join(normal_segments)
            
            # 使用文本处理器进行智能分割和重组
            sentences = self.text_processor._split_into_sentences(main_content)
            if len(sentences) > 1:
                # 重新组织句子，确保流畅
                reorganized = self._reorganize_sentences(sentences)
                merged_parts.append(reorganized)
            else:
                merged_parts.append(main_content)
        
        result = "。".join(merged_parts)
        # 确保以合适的标点结尾
        if result and not any(result.endswith(end) for end in ['。', '！', '？', '.', '!', '?']):
            result += "。"
            
        return result
    
    def _reorganize_sentences(self, sentences: List[str]) -> str:
        """重新组织句子以获得更好的流畅性"""
        if len(sentences) <= 1:
            return sentences[0] if sentences else ""
            
        # 简单的句子重组逻辑
        result = []
        i = 0
        while i < len(sentences):
            current_sentence = sentences[i].strip()
            
            if i < len(sentences) - 1:
                next_sentence = sentences[i + 1].strip()
                
                # 如果当前句子很短，尝试与下一句合并
                if len(current_sentence) < 12 and not any(current_sentence.endswith(end)  # 修复：从15降低到12
                                                         for end in ['.', '!', '?', '。', '！', '？']):
                    combined = current_sentence + "，" + next_sentence
                    result.append(combined)
                    i += 2
                    continue
            
            result.append(current_sentence)
            i += 1
        
        return "。".join(result)
    
    def extract_main_topics(self, merged_text: str) -> List[str]:
        """从合并文本中提取主要话题"""
        keywords = self.text_processor.extract_keywords(merged_text, max_keywords=3)
        
        # 情绪识别
        emotional_patterns = {
            '疲惫': ['累', '困', '疲倦', '辛苦', '折腾'],
            '工作压力': ['开会', '工作', '项目', '客户', '压力'],
            '情绪低落': ['唉', '难过', '不开心', '郁闷', '烦躁'],
            '交通': ['地铁', '公交', '打车', '堵车', '通勤']
        }
        
        detected_topics = []
        for topic, patterns in emotional_patterns.items():
            if any(pattern in merged_text for pattern in patterns):
                detected_topics.append(topic)
                
        return detected_topics[:2]

# ==================== 智能响应协调器（增强版） ====================

class IntelligentResponseCoordinator:
    """智能响应协调器 - 集成语义节奏检测和连续输入处理"""
    
    def __init__(self):
        self.rhythm_detector = SemanticRhythmDetector()
        self.input_processor = ContinuousInputProcessor()
        self.conversation_analyzer = ConversationAnalyzer()
        self.language_generator = NaturalLanguageGenerator()
        self.sentence_streamer = SentenceStreamer()
        self.response_timers = defaultdict(lambda: None)
        self.user_last_full_response = defaultdict(float)
        self.user_conversation_style = defaultdict(lambda: 'normal')
        
    async def process_user_message(self, user_id: str, message: str, 
                                 chat_history: List[Dict] = None) -> Dict[str, Any]:
        """处理用户消息并返回响应决策"""
        if chat_history is None:
            chat_history = []
            
        current_time = time.time()
        rhythm_analysis = self.rhythm_detector.analyze_message_rhythm(user_id, message, current_time)
        
        response_decision = {
            'immediate_action': 'hold',  # hold, short_feedback, full_response
            'response_content': '',
            'merged_context': '',
            'analysis': rhythm_analysis,
            'should_delay': False,
            'delay_duration': 0,
            'topics': [],
            'emotion': 'neutral',
            'should_stream': True,  # 新增：默认启用流式发送
            'stream_style': 'normal'  # 新增：流式发送风格
        }
        
        # 检查是否需要发送简短反馈
        if rhythm_analysis['should_hold_reply']:
            should_feedback, feedback_text = self.rhythm_detector.should_send_short_feedback(user_id)
            
            if should_feedback:
                response_decision['immediate_action'] = 'short_feedback'
                response_decision['response_content'] = feedback_text
                response_decision['should_stream'] = False  # 简短反馈不流式发送
            else:
                response_decision['immediate_action'] = 'hold'
                
            # 设置延迟响应定时器
            self._set_response_timer(user_id)
            
        else:
            # 用户停止连续输入，生成完整响应
            pending_messages = self.rhythm_detector.get_pending_messages(user_id)
            merged_context = self.input_processor.merge_continuous_messages(pending_messages)
            topics = self.input_processor.extract_main_topics(merged_context)
            emotion = self._detect_appropriate_emotion(merged_context, chat_history)
            
            response_decision['immediate_action'] = 'full_response'
            response_decision['merged_context'] = merged_context
            response_decision['topics'] = topics
            response_decision['emotion'] = emotion
            response_decision['should_delay'] = True
            response_decision['delay_duration'] = self._calculate_natural_delay(merged_context)
            response_decision['should_stream'] = len(merged_context) > 30  # 长内容启用流式
            response_decision['stream_style'] = self._determine_stream_style(rhythm_analysis)
            
            # 更新最后完整响应时间
            self.user_last_full_response[user_id] = current_time
            
            # 清除待处理消息
            self.rhythm_detector.clear_pending_messages(user_id)
            
        return response_decision
    
    async def generate_natural_response(self, context: str, chat_history: List[Dict] = None, 
                                      emotion: str = 'neutral') -> str:
        """生成自然口语化的响应"""
        # 这里应该是调用AI模型生成原始响应
        raw_response = await self._simulate_ai_response(context, chat_history)
        
        # 应用自然语言处理
        conversational_response = self.language_generator.make_conversational(raw_response)
        emotional_response = self.language_generator.add_emotional_color(conversational_response, emotion)
        
        return emotional_response
    
    async def stream_natural_response(self, response_text: str, 
                                    message_callback: Callable[[str, bool], None],
                                    typing_callback: Callable[[float], None] = None,
                                    style: str = 'normal') -> List[str]:
        """流式发送自然响应"""
        return await self.sentence_streamer.stream_response(
            response_text, message_callback, style, typing_callback
        )
    
    def _set_response_timer(self, user_id: str):
        """设置响应定时器"""
        # 在实际实现中，这里应该使用异步定时器
        # 这里简化为标记
        self.response_timers[user_id] = time.time()
    
    def _calculate_natural_delay(self, context: str) -> float:
        """计算自然延迟时间"""
        base_delay = 2.0  # 修复：基础延迟从1.5增加到2.0
        length_factor = min(len(context) / 100, 3.0)  # 长度因素
        complexity_factor = len(re.findall(r'[，。！？]', context)) * 0.4  # 修复：复杂度因素从0.3增加到0.4
        
        total_delay = base_delay + length_factor + complexity_factor
        return min(total_delay, 10.0)  # 修复：最大延迟从8秒增加到10秒
    
    def _detect_appropriate_emotion(self, context: str, chat_history: List[Dict]) -> str:
        """检测合适的情绪"""
        emotional_words = {
            'happy': ['开心', '高兴', '快乐', '哈哈', '嘻嘻', '棒', '好', '喜欢'],
            'sad': ['难过', '伤心', '哭', '唉', '郁闷', '不开心', '糟糕'],
            'excited': ['激动', '兴奋', '惊喜', '哇', '厉害', '太棒了'],
            'calm': ['平静', '安静', '放松', '舒服', '惬意'],
            'caring': ['累', '辛苦', '困', '疲倦', '压力', '忙']
        }
        
        context_lower = context.lower()
        
        for emotion, words in emotional_words.items():
            if any(word in context_lower for word in words):
                return emotion
                
        return 'neutral'
    
    def _determine_stream_style(self, rhythm_analysis: Dict) -> str:
        """确定流式发送风格"""
        continuous_count = rhythm_analysis.get('continuous_count', 0)
        
        if continuous_count >= 3:
            return 'fast'  # 连续输入时加快响应
        elif rhythm_analysis.get('is_semantically_complete', True):
            return 'normal'  # 完整消息使用正常速度
        else:
            return 'thinking'  # 不完整消息使用思考速度
    
    async def _simulate_ai_response(self, context: str, chat_history: List[Dict] = None) -> str:
        """模拟AI响应生成（实际应该调用真正的AI模型）"""
        # 这里应该是调用真实AI模型的代码
        # 现在用模拟响应代替
        
        response_templates = [
            "我明白你的意思。{} 这确实是个值得关注的情况。",
            "嗯，关于{}，我觉得可以从几个方面来看待这个问题。",
            "听到你提到{}，我有些想法可以和你分享。",
            "{} 这个话题挺有意思的，让我想想怎么回应比较好。",
            "从你描述的情况来看，{} 确实需要认真对待。"
        ]
        
        # 提取关键词作为话题
        keywords = self.input_processor.extract_main_topics(context)
        topic = keywords[0] if keywords else "这个"
        
        template = random.choice(response_templates)
        return template.format(topic)

# ==================== 对话分析器 ====================

class ConversationAnalyzer:
    """对话分析器 - 分析对话模式和用户偏好"""
    
    def __init__(self):
        self.user_patterns = defaultdict(dict)
        self.conversation_metrics = defaultdict(lambda: {
            'avg_response_length': 0,
            'preferred_topics': [],
            'conversation_style': 'normal',
            'interaction_frequency': 0
        })
        
    def analyze_conversation_pattern(self, user_id: str, messages: List[Dict]):
        """分析对话模式"""
        if not messages:
            return
            
        # 分析响应长度
        response_lengths = [len(msg.get('content', '')) for msg in messages if msg.get('role') == 'assistant']
        if response_lengths:
            avg_length = sum(response_lengths) / len(response_lengths)
            self.conversation_metrics[user_id]['avg_response_length'] = avg_length
            
        # 分析话题偏好
        all_content = ' '.join([msg.get('content', '') for msg in messages])
        topics = self._extract_frequent_topics(all_content)
        self.conversation_metrics[user_id]['preferred_topics'] = topics[:3]
        
    def _extract_frequent_topics(self, text: str) -> List[str]:
        """提取频繁话题"""
        # 简化的关键词提取
        words = text.lower().split()
        word_freq = defaultdict(int)
        
        for word in words:
            if len(word) > 1:
                word_freq[word] += 1
                
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        return self.conversation_metrics[user_id]

# ==================== 日程模拟器 ====================

class ScheduleSimulator:
    """日程模拟器 - 处理日程安排和提醒功能"""
    
    def __init__(self):
        self.schedules = defaultdict(list)
        self.reminders = defaultdict(list)
        
    def add_schedule(self, user_id: str, schedule_data: Dict) -> bool:
        """添加日程"""
        try:
            self.schedules[user_id].append(schedule_data)
            return True
        except Exception:
            return False
            
    def get_today_schedules(self, user_id: str) -> List[Dict]:
        """获取今日日程"""
        today = datetime.now().date()
        user_schedules = self.schedules.get(user_id, [])
        
        today_schedules = []
        for schedule in user_schedules:
            schedule_date = schedule.get('date')
            if schedule_date and schedule_date.date() == today:
                today_schedules.append(schedule)
                
        return today_schedules
        
    def set_reminder(self, user_id: str, reminder_data: Dict) -> bool:
        """设置提醒"""
        try:
            self.reminders[user_id].append(reminder_data)
            return True
        except Exception:
            return False
            
    def check_reminders(self, user_id: str) -> List[Dict]:
        """检查待触发提醒"""
        current_time = datetime.now()
        user_reminders = self.reminders.get(user_id, [])
        
        due_reminders = []
        remaining_reminders = []
        
        for reminder in user_reminders:
            reminder_time = reminder.get('remind_time')
            if reminder_time and reminder_time <= current_time:
                due_reminders.append(reminder)
            else:
                remaining_reminders.append(reminder)
                
        # 更新剩余提醒
        self.reminders[user_id] = remaining_reminders
        
        return due_reminders

    def simulate_schedule_analysis(self, user_input: str) -> Dict[str, Any]:
        """模拟日程分析（兼容旧版本）"""
        return {
            'has_schedule': False,
            'schedule_type': 'none',
            'reminder_set': False,
            'analysis': '暂未检测到日程安排'
        }

# ==================== 工具函数 ====================

async def safe_json_load(filepath: str, default: Any = None) -> Any:
    """安全加载JSON文件"""
    try:
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            if content.strip():
                return json.loads(content)
    except Exception as e:
        print(f"⚠️ 加载JSON文件失败 {filepath}: {e}")
    
    return default

async def safe_json_save(filepath: str, data: Any) -> bool:
    """安全保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"⚠️ 保存JSON文件失败 {filepath}: {e}")
        return False

def format_timestamp(timestamp: datetime = None) -> str:
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
    if not text1 or not text2:
        return 0.0
        
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
        
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union

def get_random_delay(base_delay: float, variance: float = 0.3) -> float:
    """获取随机延迟"""
    variation = random.uniform(1 - variance, 1 + variance)
    return max(0.1, base_delay * variation)

def sanitize_filename(filename: str) -> str:
    """净化文件名"""
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:100-len(ext)] + ext
    return sanitized

def is_chinese_text(text: str) -> bool:
    """判断是否为中文文本"""
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars) / max(len(text), 1) > 0.3

def extract_emojis(text: str) -> List[str]:
    """提取表情符号"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.findall(text)

# ==================== 测试函数 ====================

async def test_enhanced_utils():
    """测试增强的工具函数"""
    print("🧪 测试增强工具函数...")
    
    # 测试性能监控器
    monitor = PerformanceMonitor()
    monitor.record_success()
    monitor.record_response_time(1.5)
    monitor.record_api_call(0.8)
    
    report = monitor.get_performance_report()
    print(f"📊 性能报告: {report}")
    print(f"🏥 健康状态: {monitor.get_health_status()}")
    
    # 测试自然语言生成器
    generator = NaturalLanguageGenerator()
    test_text = "今天工作很累，开了很多会议，现在在地铁上。"
    
    conversational = generator.make_conversational(test_text)
    print(f"✅ 口语化转换: {conversational}")
    
    emotional = generator.add_emotional_color(conversational, 'caring')
    print(f"✅ 情绪化处理: {emotional}")
    
    # 测试逐句发送
    streamer = SentenceStreamer()
    
    async def mock_callback(text: str, is_final: bool):
        print(f"📤 发送: '{text}' {'(最终)' if is_final else ''}")
    
    async def mock_typing_callback(duration: float):
        print(f"⌨️ 模拟打字: {duration:.1f}秒")
        await asyncio.sleep(duration)
    
    print("🧪 测试逐句发送...")
    long_response = "今天天气真好啊！阳光明媚，微风拂面。我觉得这样的天气最适合出去散步了。你要不要也出去走走呢？呼吸一下新鲜空气对身体很好的。"
    
    await streamer.stream_response(long_response, mock_callback, 'normal', mock_typing_callback)
    
    # 测试智能响应协调器
    coordinator = IntelligentResponseCoordinator()
    
    # 模拟连续对话
    test_messages = [
        "老妖，我今天好累。",
        "开了一天的会。",
        "现在还在加班。",
        "唉，感觉身体被掏空。"
    ]
    
    print("🧪 测试完整对话流程...")
    for i, msg in enumerate(test_messages):
        print(f"👤 用户: {msg}")
        decision = await coordinator.process_user_message('test_user', msg)
        print(f"  决策: {decision['immediate_action']}")
        
        if decision['immediate_action'] == 'full_response':
            natural_response = await coordinator.generate_natural_response(
                decision['merged_context'],
                emotion=decision['emotion']
            )
            print(f"  🤖 生成响应: {natural_response}")
            
            # 模拟流式发送
            await coordinator.stream_natural_response(
                natural_response,
                mock_callback,
                mock_typing_callback,
                decision['stream_style']
            )
        
        if i < len(test_messages) - 1:
            await asyncio.sleep(2)
    
    print("🎉 增强工具函数测试完成!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_utils())
