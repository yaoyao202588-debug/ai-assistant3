# -*- coding: utf-8 -*-
"""人格一致性引擎"""
import re
from typing import Dict, List

class PersonalityConsistencyEngine:
    """
    人格一致性引擎
    
    确保回复符合人设特征
    """
    
    def __init__(self, character_profile: Dict):
        self.character = character_profile
        
        # 人设特征
        self.personality_traits = character_profile.get('personality', {}).get('core_traits', [])
        self.age = character_profile.get('basic_info', {}).get('age', 33)
        self.occupation = character_profile.get('basic_info', {}).get('occupation', '')
        
        # 禁止模式
        self.forbidden_patterns = [
            r'作为.*AI',
            r'我是AI',
            r'机器学习',
            r'语言模型',
            r'as an AI',
            r'I am an AI',
            r'人工智能助手'
        ]
        
        # 过度客服化模式
        self.overly_formal_patterns = [
            r'很高兴为您服务',
            r'有什么我可以帮助您',
            r'如果您还有.*问题',
            r'How can I assist you',
            r'Is there anything else',
        ]
        
        # 年龄不符模式(太年轻化)
        self.age_inappropriate_patterns = [
            r'哈哈哈哈+',  # 过多哈
            r'🤣{2,}',  # 过多emoji
            r'好可爱',
            r'超级',
            r'巨',
            r'OMG',
            r'YOLO'
        ]
    
    def validate_response(self, response: str, context: Dict) -> Dict:
        """
        验证回复是否符合人设
        
        Args:
            response: AI生成的回复
            context: 上下文
            
        Returns:
            Dict: 验证结果
        """
        issues = []
        score = 1.0
        
        # 1. 检查禁止模式
        for pattern in self.forbidden_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f'包含AI暴露模式: {pattern}')
                score -= 0.3
        
        # 2. 检查客服化
        for pattern in self.overly_formal_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f'过度客服化: {pattern}')
                score -= 0.2
        
        # 3. 检查年龄不符
        for pattern in self.age_inappropriate_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append(f'年龄不符模式: {pattern}')
                score -= 0.15
        
        # 4. 检查长度
        if len(response) > 200:
            issues.append('回复过长(>200字)')
            score -= 0.1
        
        # 5. 检查emoji过多
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', response))
        if emoji_count > 3:
            issues.append(f'emoji过多({emoji_count}个)')
            score -= 0.1
        
        # 6. 检查感叹号过多
        exclamation_count = response.count('!') + response.count('！')
        if exclamation_count > 3:
            issues.append(f'感叹号过多({exclamation_count}个)')
            score -= 0.1
        
        score = max(0.0, score)
        
        return {
            'pass_threshold': score >= 0.7,
            'score': round(score, 2),
            'issues': issues
        }
    
    def adjust_response_style(self, response: str, emotional_state: str = 'neutral') -> str:
        """
        调整回复风格使其符合人设
        
        Args:
            response: 原始回复
            emotional_state: 情感状态
            
        Returns:
            str: 调整后的回复
        """
        adjusted = response
        
        # 1. 移除AI暴露
        for pattern in self.forbidden_patterns:
            adjusted = re.sub(pattern, '', adjusted, flags=re.IGNORECASE)
        
        # 2. 减少过多的感叹号
        adjusted = re.sub(r'!{2,}', '!', adjusted)
        adjusted = re.sub(r'！{2,}', '！', adjusted)
        
        # 3. 减少过多的emoji
        emoji_pattern = r'([\U0001F300-\U0001F9FF])\1+'
        adjusted = re.sub(emoji_pattern, r'\1', adjusted)
        
        # 4. 移除客服化语言
        adjusted = adjusted.replace('很高兴为您服务', '')
        adjusted = adjusted.replace('请问您还有其他问题吗', '')
        
        # 5. 根据情感调整语气
        if emotional_state in ['sad', 'anxious'] and '哈哈' in adjusted:
            adjusted = adjusted.replace('哈哈', '')  # 移除不合适的笑声
        
        # 6. 确保不过长
        if len(adjusted) > 200:
            sentences = adjusted.split('。')
            adjusted = '。'.join(sentences[:2]) + '。'
        
        return adjusted.strip()
    
    def get_personality_keywords(self) -> List[str]:
        """
        获取人设关键词
        
        Returns:
            List[str]: 关键词列表
        """
        keywords = []
        
        # 基于职业
        if '企业家' in self.occupation or 'Founder' in self.occupation:
            keywords.extend(['商业', '管理', '投资', '公司'])
        
        # 基于性格
        if '独立' in self.personality_traits:
            keywords.extend(['自己', '决定', '选择'])
        
        if '优雅' in self.personality_traits:
            keywords.extend(['体面', '高端', '品质'])
        
        return keywords
