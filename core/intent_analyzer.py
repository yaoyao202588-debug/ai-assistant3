# -*- coding: utf-8 -*-
"""深度意图分析器"""
import re
import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from openai import OpenAI

@dataclass
class IntentProfile:
    """意图画像数据类"""
    surface_intent: str  # 表层意图
    emotional_state: str  # 情感状态
    social_need: str  # 社交需求
    urgency_level: float  # 紧急程度 0-1
    topic_shift: bool  # 是否在转换话题
    hidden_concerns: List[str]  # 隐藏的担忧
    need_listening: bool  # 需要倾听
    need_advice: bool  # 需要建议
    need_comfort: bool  # 需要安慰
    confidence: float  # 分析置信度

class DeepIntentAnalyzer:
    """
    深度意图分析器
    
    使用DeepSeek API进行多层次意图理解
    """
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model
        
        # 意图分析专用prompt
        self.analysis_prompt = self._build_analysis_prompt()
    
    def analyze_intent(self, message: str, context: Dict) -> IntentProfile:
        """
        综合分析用户意图
        
        Args:
            message: 用户消息
            context: 对话上下文
        
        Returns:
            IntentProfile: 意图分析结果
        """
        # 1. 准备分析上下文
        analysis_context = self._prepare_context(message, context)
        
        # 2. 调用API进行深度分析
        analysis_result = self._call_intent_api(analysis_context)
        
        # 3. 解析结果
        intent_profile = self._parse_analysis_result(analysis_result)
        
        # 4. 后处理和验证
        intent_profile = self._post_process(intent_profile, message, context)
        
        return intent_profile
    
    def _build_analysis_prompt(self) -> str:
        """
        构建意图分析的System Prompt
        """
        return """你是一个专业的心理学家和对话分析专家。你的任务是深入分析用户消息,理解其真实意图和需求。

请从以下维度分析:

1. **表层意图** - 用户字面上在说什么
2. **情感状态** - 用户的真实情绪(可能与表达不一致)
3. **社交需求** - 用户期望的互动方式:
   - listening: 需要倾听和陪伴
   - advice: 寻求建议和解决方案
   - comfort: 需要安慰和鼓励
   - companionship: 简单的社交陪伴
   - validation: 需要认可和肯定

4. **紧急程度** (0-1):
   - 0.0-0.3: 日常闲聊
   - 0.4-0.6: 有些在意的事
   - 0.7-0.9: 比较紧急/重要
   - 0.9-1.0: 非常紧急/危机

5. **隐藏的担忧** - 用户可能没有直接说出的潜在问题

6. **话题转换** - 是否在尝试改变话题方向

**分析原则**:
- 不要只看字面意思,要理解深层含义
- 注意情绪和语气的矛盾(如说"没事"但可能有事)
- 考虑文化背景(东亚文化倾向含蓄表达)
- 区分"想说的"和"能说的"

请以JSON格式输出分析结果:
```json
{
  "surface_intent": "...",
  "emotional_state": "...",
  "social_need": "listening/advice/comfort/companionship/validation",
  "urgency_level": 0.0-1.0,
  "hidden_concerns": ["concern1", "concern2"],
  "topic_shift": true/false,
  "need_listening": true/false,
  "need_advice": true/false,
  "need_comfort": true/false,
  "reasoning": "简要说明分析理由"
}
```"""
    
    def _prepare_context(self, message: str, context: Dict) -> str:
        """
        准备分析上下文
        """
        context_parts = []
        
        # 1. 最近对话
        if context.get('recent_exchanges'):
            recent = context['recent_exchanges'][-3:]
            summary = "\n".join([
                f"{'用户' if ex['role']=='user' else 'AI'}: {ex['content']}"
                for ex in recent
            ])
            context_parts.append(f"**最近对话**:\n{summary}")
        
        # 2. 情绪趋势
        if context.get('emotional_trend'):
            context_parts.append(
                f"**情绪趋势**: {context['emotional_trend']}"
            )
        
        # 3. 用户特征
        if context.get('user_traits'):
            traits = context['user_traits']
            context_parts.append(
                f"**用户特征**: {traits.get('communication_style', '未知')}"
            )
        
        # 4. 当前消息
        context_parts.append(f"\n**待分析消息**: {message}")
        
        return "\n\n".join(context_parts)
    
    def _call_intent_api(self, context: str) -> Dict:
        """
        调用API进行意图分析
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.analysis_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.3,  # 分析任务需要较低温度
                max_tokens=500,
                response_format={"type": "json_object"}  # 强制JSON输出
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"⚠️ 意图分析API调用失败: {str(e)}")
            return self._get_fallback_analysis()
    
    def _parse_analysis_result(self, result: Dict) -> IntentProfile:
        """
        解析API返回的分析结果
        """
        return IntentProfile(
            surface_intent=result.get('surface_intent', '日常交流'),
            emotional_state=result.get('emotional_state', 'neutral'),
            social_need=result.get('social_need', 'companionship'),
            urgency_level=float(result.get('urgency_level', 0.3)),
            topic_shift=result.get('topic_shift', False),
            hidden_concerns=result.get('hidden_concerns', []),
            need_listening=result.get('need_listening', False),
            need_advice=result.get('need_advice', False),
            need_comfort=result.get('need_comfort', False),
            confidence=self._calculate_confidence(result)
        )
    
    def _post_process(self, profile: IntentProfile, 
                     message: str, context: Dict) -> IntentProfile:
        """
        后处理和验证
        
        应用规则修正和常识验证
        """
        # 1. 紧急关键词检测
        urgent_keywords = ['紧急', '急事', '救命', '帮帮我', 'urgent', 'emergency']
        if any(keyword in message.lower() for keyword in urgent_keywords):
            profile.urgency_level = max(profile.urgency_level, 0.8)
        
        # 2. 负面情绪强化检测
        negative_intensifiers = ['很', '非常', '特别', '太', '极其']
        negative_words = ['累', '难过', '痛苦', '烦', '压力', '焦虑']
        
        if any(intensifier in message for intensifier in negative_intensifiers):
            if any(word in message for word in negative_words):
                profile.need_comfort = True
                profile.need_listening = True
        
        # 3. 疑问句通常需要建议
        if '?' in message or '吗' in message or '呢' in message:
            if not profile.need_listening:  # 如果不是倾诉类
                profile.need_advice = True
        
        return profile
    
    def _calculate_confidence(self, result: Dict) -> float:
        """
        计算分析置信度
        
        基于:
        - reasoning的详细程度
        - 各项指标的一致性
        - 上下文丰富度
        """
        # 简化版置信度计算
        base_confidence = 0.7
        
        # 有reasoning说明
        if result.get('reasoning') and len(result['reasoning']) > 20:
            base_confidence += 0.1
        
        # 多项指标一致
        need_count = sum([
            result.get('need_listening', False),
            result.get('need_advice', False),
            result.get('need_comfort', False)
        ])
        if need_count > 0:  # 有明确需求
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _get_fallback_analysis(self) -> Dict:
        """
        API失败时的降级分析
        """
        return {
            "surface_intent": "日常交流",
            "emotional_state": "neutral",
            "social_need": "companionship",
            "urgency_level": 0.3,
            "hidden_concerns": [],
            "topic_shift": False,
            "need_listening": False,
            "need_advice": False,
            "need_comfort": False,
            "reasoning": "Fallback analysis"
        }
