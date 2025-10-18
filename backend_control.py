# backend_control.py - 优化修复版 v7.5 (集成增强功能)
import streamlit as st
import json
import os
import time
import subprocess
import threading
import sys
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="Kiyomi AI Assistant 控制中心 v7.5",
    layout="wide",
    page_icon="👑"
)

# 设置编码
if os.name == 'nt':
    os.system('chcp 65001 > nul')

class BackendControl:
    def __init__(self):
        # 设置编码环境
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # 导入配置管理器
        try:
            from main_assistant import ConfigManager, path_manager
            self.config_manager = ConfigManager()
            self.path_manager = path_manager
            print("✅ 配置管理器加载成功")
        except ImportError as e:
            st.error(f"❌ 导入配置管理器失败: {e}")
            return
        
        # 导入增强功能模块
        try:
            from utils import (
                SemanticRhythmDetector, 
                ContinuousInputProcessor, 
                IntelligentResponseCoordinator,
                PerformanceMonitor,
                NaturalLanguageGenerator,
                SentenceStreamer,
                EnhancedTextProcessor,
                ConversationAnalyzer,
                MemoryManager,
                ScheduleSimulator
            )
            self.enhanced_modules_available = True
            print("✅ 增强功能模块加载成功")
        except ImportError as e:
            st.warning(f"⚠️ 增强功能模块加载失败: {e}")
            self.enhanced_modules_available = False
        
        # 新增优化功能设置
        self.enhanced_features = {
            'enable_advanced_emotion': True,
            'enable_semantic_splitting': True,
            'enable_logic_detection': True,
            'enable_async_queue': True,
            'enable_self_reference': True,
            'enable_topic_extension': True,
            'enable_busy_state': True,
            'enable_text_sanitization': True,
            'enable_semantic_rhythm': True,
            'enable_continuous_input_processing': True,
            'enable_intelligent_coordination': True,
            'enable_performance_monitoring': True,
            'enable_enhanced_quoting': True,  # 新增：增强引用管理
            'enable_emotional_override': True,  # 新增：情绪优先覆盖
            'enable_sentence_streaming': True,  # 新增：逐句发送
            'enable_memory_management': True,  # 新增：记忆管理
            'enable_conversation_analysis': True  # 新增：对话分析
        }
    
    def load_config(self, config_type):
        """使用配置管理器加载配置"""
        try:
            config = self.config_manager.load_config(config_type)
            
            if not config or config is None:
                print(f"⚠️ 配置 {config_type} 为空，使用默认值")
                return self._get_default_config(config_type)
                
            return config
        except Exception as e:
            print(f"⚠️ 加载配置失败 {config_type}: {e}")
            return self._get_default_config(config_type)

    def _get_default_config(self, config_type):
        """获取默认配置"""
        defaults = {
            'relationships': {},
            'system_config': {
                "SYSTEM_VERSION": "v7.5.0",
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
                "ENABLE_ADVANCED_FEATURES": True,
                "ENABLE_SEMANTIC_RHYTHM": True,
                "ENABLE_CONTINUOUS_INPUT_PROCESSING": True,
                "ENABLE_INTELLIGENT_COORDINATION": True,
                "ENABLE_ENHANCED_QUOTING": True,  # 新增
                "ENABLE_EMOTIONAL_OVERRIDE": True,  # 新增
                "ENABLE_SENTENCE_STREAMING": True  # 新增
            },
            'character_profile': {
                "profile_version": 7,
                "last_updated": datetime.now().isoformat(),
                "basic_info": {
                    "name": "Tanaka Kiyomi",
                    "chinese_name": "田中 清美",
                    "preferred_name": "Kiyomi",
                    "age": 33,
                    "birthday": "1992-08-22",
                    "height": "5'6\"",
                    "weight": "110 lbs",
                    "nationality": "Japanese",
                    "current_citizenship": "UK Citizen",
                    "gender": "female",
                    "occupation": "Founder of Trading Company & Jewelry Company & Gold Options Investor",
                    "hometown": "Tokyo",
                    "current_city": "London",
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
                    "covid_experience": "During the 2020 COVID pandemic, pre-arranged gold options investments effectively hedged losses from physical business",
                    "current_life": "Running two companies in the UK and doing personal investments, living independently"
                },
                "professional_background": {
                    "companies": [
                        {
                            "name": "Trading Company",
                            "focus": "Helping Japanese companies expand into European and other international markets",
                            "services": ["Market research", "Product localization", "International logistics", "After-sales support"],
                            "established": 2017
                        },
                        {
                            "name": "Jewelry Company",
                            "focus": "High-end jewelry customization studio",
                            "style": "Blending Japanese traditional aesthetics with modern design",
                            "established": 2018
                        }
                    ],
                    "investment": {
                        "focus": "Gold options trading",
                        "experience_years": 10,
                        "purpose": "Provides important cash flow and risk hedging",
                        "expertise_level": "Advanced"
                    }
                },
                "personal_interests": {
                    "hobbies": ["Traveling", "Reading", "Watching movies", "Listening to music", "Playing tennis", "Playing golf", "Gold options investment"],
                    "travel_experiences": [
                        "Most US cities", "African safari", "Norway", "Canada", "Australia", 
                        "Germany", "China", "Italy", "Philippines", "Singapore", "Malaysia", "Thailand"
                    ],
                    "favorite_topics": ["International business", "Investment and finance", "Cultural differences", "Travel experiences", "Personal growth", "Luxury appreciation"]
                },
                "conversation_preferences": {
                    "use_natural_segmentation": True,
                    "emotional_response_level": 7,
                    "memory_recall_frequency": 0.4,
                    "quote_style": "emotional_contextual",
                    "enable_self_reference": True,
                    "enable_topic_extension": True,
                    "enable_semantic_rhythm": True,
                    "enable_continuous_processing": True,
                    "enable_enhanced_quoting": True,  # 新增
                    "enable_emotional_override": True,  # 新增
                    "enable_sentence_streaming": True  # 新增
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
                    "min_reply_interval": 2,
                    "max_reply_interval": 60,
                    "typing_speed_chars_per_min": 200,
                    "thinking_time_base": 1.5,
                    "thinking_time_per_100_chars": 0.5,
                    "typing_detection_timeout": 3,
                    "max_wait_time": 10,
                    "natural_delay_variance": 0.3,
                    "async_processing_delay": 1.0,
                    "streaming_sentence_delay": 0.8,  # 新增：逐句发送延迟
                    "streaming_typing_delay": 0.3  # 新增：打字延迟
                },
                "behavior": {
                    "auto_reply_enabled": True,
                    "use_emojis": True,
                    "max_emojis_per_message": 2,
                    "emoji_min_interval": 3,
                    "use_typos": False,
                    "be_casual": True,
                    "detect_typing_status": True,
                    "handle_reply_references": True,
                    "smart_typing_detection": True,
                    "advanced_personality": True,
                    "enable_smart_quoting": True,
                    "quote_cooldown": 60,
                    "enable_smart_schedule": True,
                    "enable_short_message": True,
                    "daily_message_limit": 50,
                    "emotional_quoting_enabled": True,
                    "light_memory_enabled": True,
                    "natural_segmentation": True,
                    "enable_advanced_emotion": True,
                    "enable_logic_detection": True,
                    "enable_semantic_rhythm": True,
                    "enable_continuous_input_processing": True,
                    "enable_enhanced_quoting": True,  # 新增
                    "enable_emotional_override": True,  # 新增
                    "enable_sentence_streaming": True  # 新增
                },
                "response_control": {
                    "min_response_chars": 3,
                    "max_response_chars": 500,
                    "enable_length_based_timing": True,
                    "fast_reply_threshold": 50,
                    "slow_reply_threshold": 200,
                    "semantic_segmentation": True,
                    "emotional_context_integration": True,
                    "enable_semantic_splitting": True,
                    "enable_intelligent_coordination": True,
                    "enable_enhanced_quoting": True,  # 新增
                    "enable_emotional_override": True  # 新增
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
                    "contextual_memory_weight": 0.4,
                    "enable_self_reference": True,
                    "enable_topic_extension": True,
                    "enable_semantic_rhythm_detection": True,
                    "enable_continuous_merge": True,
                    "enable_intelligent_response": True,
                    "enable_enhanced_quoting": True,  # 新增
                    "enable_emotional_override": True,  # 新增
                    "enable_sentence_streaming": True  # 新增
                },
                "advanced_features": {
                    "enable_advanced_emotion": True,
                    "enable_semantic_splitting": True,
                    "enable_logic_detection": True,
                    "enable_async_queue": True,
                    "enable_busy_state": True,
                    "enable_text_sanitization": True,
                    "max_async_queue_size": 10,
                    "busy_state_timeout": 300,
                    "enable_semantic_rhythm": True,
                    "enable_continuous_input_processing": True,
                    "enable_intelligent_coordination": True,
                    "enable_performance_monitoring": True,
                    "enable_enhanced_quoting": True,  # 新增
                    "enable_emotional_override": True,  # 新增
                    "enable_sentence_streaming": True,  # 新增
                    "enable_memory_management": True,  # 新增
                    "enable_conversation_analysis": True  # 新增
                },
                "enhanced_quoting": {  # 新增：增强引用配置
                    "quote_cooldown_time": 60,
                    "max_recent_quotes": 3,
                    "similarity_threshold": 0.6,
                    "enable_user_recent_quoting": True,
                    "enable_ai_self_quoting": True,
                    "enable_topic_continuation": True,
                    "enable_clarification_quoting": True,
                    "enable_emotional_continuation": True
                },
                "emotional_override": {  # 新增：情绪优先覆盖配置
                    "enable_urgent_override": True,
                    "enable_emotional_override": True,
                    "enable_intimate_override": True,
                    "enable_crisis_override": True,
                    "override_intensity_threshold": 0.8,
                    "override_confidence_threshold": 0.7
                },
                "sentence_streaming": {  # 新增：逐句发送配置
                    "enable_streaming": True,
                    "min_length_for_streaming": 50,
                    "max_sentence_length": 100,
                    "sentence_delay_base": 0.5,
                    "typing_delay_multiplier": 0.01,
                    "enable_typing_simulation": True,
                    "streaming_styles": ["normal", "fast", "slow", "thinking"]
                }
            }
        }
        return defaults.get(config_type, {})
    
    def save_config(self, config_type, data):
        """保存配置"""
        try:
            result = self.config_manager.save_config(config_type, data)
            if result:
                st.success(f"✅ {config_type} 保存成功!")
            return result
        except Exception as e:
            st.error(f"❌ 保存失败: {e}")
            return False
    
    def _check_configs(self):
        """检查配置文件状态"""
        all_good = True
        
        config_files = [
            'system_config', 'character_profile', 'api_config', 
            'reply_settings', 'relationships'
        ]
        
        for config_type in config_files:
            try:
                config = self.load_config(config_type)
                if not config:
                    st.warning(f"⚠️ 配置文件加载警告: {config_type} - 使用默认值")
                else:
                    print(f"✅ 配置 {config_type} 加载成功")
            except Exception as e:
                st.error(f"❌ 配置文件错误: {config_type} - {e}")
                all_good = False
        
        return all_good
    
    def run_fix_configs(self):
        """运行配置文件修复"""
        try:
            from fix_tools import ConfigFixer
            fixer = ConfigFixer()
            success = fixer.fix_all_configs()
            
            if success:
                st.success("✅ 配置文件修复完成!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("❌ 修复失败")
                
        except Exception as e:
            st.error(f"❌ 修复失败: {e}")
    
    def _is_main_running(self):
        """检查主程序是否在运行"""
        try:
            import psutil
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = process.info.get('cmdline', [])
                    if cmdline and 'main_assistant.py' in ' '.join(cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except ImportError:
            try:
                result = subprocess.run(
                    ["tasklist", "/fi", "imagename eq python.exe", "/fo", "csv"], 
                    capture_output=True, text=True, timeout=5
                )
                return "main_assistant.py" in result.stdout
            except:
                return False
    
    def is_recent(self, timestamp, hours=24):
        """检查时间是否在最近范围内"""
        try:
            if not timestamp:
                return False
            last_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return (datetime.now() - last_time).total_seconds() < hours * 3600
        except:
            return False
    
    def render_dashboard(self):
        """渲染仪表板页面"""
        st.header("📊 系统仪表板 v7.5")
        
        system_config = self.load_config('system_config')
        character = self.load_config('character_profile')
        relationships = self.load_config('relationships')
        reply_settings = self.load_config('reply_settings')
        
        timing = reply_settings.get('timing', {})
        behavior = reply_settings.get('behavior', {})
        smart_conv = reply_settings.get('smart_conversation', {})
        advanced_features = reply_settings.get('advanced_features', {})
        enhanced_quoting = reply_settings.get('enhanced_quoting', {})
        emotional_override = reply_settings.get('emotional_override', {})
        sentence_streaming = reply_settings.get('sentence_streaming', {})
        
        # 顶部指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            user_count = len(relationships) if isinstance(relationships, dict) else 0
            st.metric("总用户数", user_count)
        with col2:
            if isinstance(relationships, dict):
                active_users = sum(1 for rel in relationships.values() if self.is_recent(rel.get('last_interaction', '')))
            else:
                active_users = 0
            st.metric("活跃用户", active_users)
        with col3:
            st.metric("系统版本", system_config.get('SYSTEM_VERSION', 'v7.5.0'))
        with col4:
            st.metric("当前角色", character.get('basic_info', {}).get('name', 'Unknown'))
        
        # 角色信息卡片
        st.subheader("👑 角色信息")
        col1, col2 = st.columns(2)
        
        with col1:
            basic_info = character.get('basic_info', {})
            st.info(f"""
            **{basic_info.get('chinese_name', '')} ({basic_info.get('name', '')})**
            - 🎂 {basic_info.get('age', '')} 岁 ({basic_info.get('birthday', '')})
            - 🏙️ 居住在 {basic_info.get('current_city', '')}
            - 💼 {basic_info.get('occupation', '')}
            - 📈 {character.get('professional_background', {}).get('investment', {}).get('experience_years', '')} 年投资经验
            - 💫 情绪智能: {character.get('personality', {}).get('emotional_intelligence', 'N/A')}/10
            """)
        
        with col2:
            personality = character.get('personality', {})
            st.info(f"""
            **性格特点**
            - 核心特质: {', '.join(personality.get('core_traits', []))}
            - 对话风格: {personality.get('conversation_style', '')}
            - 情绪范围: {', '.join(personality.get('emotional_range', []))}
            - 情绪引用: {'✅ 启用' if behavior.get('emotional_quoting_enabled') else '❌ 禁用'}
            - 轻记忆: {'✅ 启用' if behavior.get('light_memory_enabled') else '❌ 禁用'}
            - 人设一致性: {'✅ 启用' if behavior.get('advanced_personality') else '❌ 禁用'}
            """)
        
        # 系统状态
        st.subheader("🟢 系统状态")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**核心功能**")
            st.write(f"• 智能输入检测: {'✅ 启用' if behavior.get('smart_typing_detection') else '❌ 禁用'}")
            st.write(f"• 表情符号: {'✅ 启用' if behavior.get('use_emojis') else '❌ 禁用'}")
            st.write(f"• 自动回复: {'✅ 启用' if behavior.get('auto_reply_enabled') else '❌ 禁用'}")
            st.write(f"• 智能引用: {'✅ 启用' if behavior.get('enable_smart_quoting', True) else '❌ 禁用'}")
            st.write(f"• 智能作息: {'✅ 启用' if behavior.get('enable_smart_schedule', True) else '❌ 禁用'}")
            st.write(f"• 情绪引用: {'✅ 启用' if behavior.get('emotional_quoting_enabled', True) else '❌ 禁用'}")
        
        with col2:
            st.write("**性能设置**")
            st.write(f"• 打字速度: {timing.get('typing_speed_chars_per_min', 200)} 字符/分钟")
            st.write(f"• 输入检测: {timing.get('typing_detection_timeout', 3)} 秒")
            st.write(f"• 最大等待时间: {timing.get('max_wait_time', 10)} 秒")
            st.write(f"• 引用冷却: {behavior.get('quote_cooldown', 60)} 秒")
            st.write(f"• 每日限制: {behavior.get('daily_message_limit', 50)} 条消息")
            st.write(f"• 轻记忆权重: {smart_conv.get('contextual_memory_weight', 0.4)}")
        
        # 新增增强功能状态
        st.subheader("🚀 增强功能 v7.5")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**智能对话优化**")
            st.write(f"• 高级情绪引擎: {'✅ 启用' if advanced_features.get('enable_advanced_emotion', True) else '❌ 禁用'}")
            st.write(f"• 语义分割: {'✅ 启用' if advanced_features.get('enable_semantic_splitting', True) else '❌ 禁用'}")
            st.write(f"• 逻辑检测: {'✅ 启用' if advanced_features.get('enable_logic_detection', True) else '❌ 禁用'}")
            st.write(f"• 自我引用: {'✅ 启用' if smart_conv.get('enable_self_reference', True) else '❌ 禁用'}")
            st.write(f"• 话题扩展: {'✅ 启用' if smart_conv.get('enable_topic_extension', True) else '❌ 禁用'}")
            st.write(f"• 异步队列: {'✅ 启用' if advanced_features.get('enable_async_queue', True) else '❌ 禁用'}")
        
        with col2:
            st.write("**系统优化**")
            st.write(f"• 忙碌状态: {'✅ 启用' if advanced_features.get('enable_busy_state', True) else '❌ 禁用'}")
            st.write(f"• 文本净化: {'✅ 启用' if advanced_features.get('enable_text_sanitization', True) else '❌ 禁用'}")
            st.write(f"• 语义节奏检测: {'✅ 启用' if advanced_features.get('enable_semantic_rhythm', True) else '❌ 禁用'}")
            st.write(f"• 连续输入处理: {'✅ 启用' if advanced_features.get('enable_continuous_input_processing', True) else '❌ 禁用'}")
            st.write(f"• 智能响应协调: {'✅ 启用' if advanced_features.get('enable_intelligent_coordination', True) else '❌ 禁用'}")
            st.write(f"• 性能监控: {'✅ 启用' if advanced_features.get('enable_performance_monitoring', True) else '❌ 禁用'}")
        
        # 新增高级功能状态
        st.subheader("🎯 高级功能")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**增强引用管理**")
            st.write(f"• 用户最近消息引用: {'✅ 启用' if enhanced_quoting.get('enable_user_recent_quoting', True) else '❌ 禁用'}")
            st.write(f"• AI自我引用: {'✅ 启用' if enhanced_quoting.get('enable_ai_self_quoting', True) else '❌ 禁用'}")
            st.write(f"• 话题延续引用: {'✅ 启用' if enhanced_quoting.get('enable_topic_continuation', True) else '❌ 禁用'}")
            st.write(f"• 澄清请求引用: {'✅ 启用' if enhanced_quoting.get('enable_clarification_quoting', True) else '❌ 禁用'}")
            st.write(f"• 情感延续引用: {'✅ 启用' if enhanced_quoting.get('enable_emotional_continuation', True) else '❌ 禁用'}")
            st.write(f"• 相似度阈值: {enhanced_quoting.get('similarity_threshold', 0.6)}")
        
        with col2:
            st.write("**情绪优先覆盖**")
            st.write(f"• 紧急消息覆盖: {'✅ 启用' if emotional_override.get('enable_urgent_override', True) else '❌ 禁用'}")
            st.write(f"• 情感消息覆盖: {'✅ 启用' if emotional_override.get('enable_emotional_override', True) else '❌ 禁用'}")
            st.write(f"• 亲密消息覆盖: {'✅ 启用' if emotional_override.get('enable_intimate_override', True) else '❌ 禁用'}")
            st.write(f"• 危机消息覆盖: {'✅ 启用' if emotional_override.get('enable_crisis_override', True) else '❌ 禁用'}")
            st.write(f"• 强度阈值: {emotional_override.get('override_intensity_threshold', 0.8)}")
            st.write(f"• 置信度阈值: {emotional_override.get('override_confidence_threshold', 0.7)}")
        
        # 逐句发送状态
        st.subheader("💬 逐句发送设置")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"• 启用逐句发送: {'✅ 是' if sentence_streaming.get('enable_streaming', True) else '❌ 否'}")
            st.write(f"• 最小发送长度: {sentence_streaming.get('min_length_for_streaming', 50)} 字符")
            st.write(f"• 最大句子长度: {sentence_streaming.get('max_sentence_length', 100)} 字符")
            st.write(f"• 基础句子延迟: {sentence_streaming.get('sentence_delay_base', 0.5)} 秒")
        
        with col2:
            st.write(f"• 打字延迟倍数: {sentence_streaming.get('typing_delay_multiplier', 0.01)}")
            st.write(f"• 启用打字模拟: {'✅ 是' if sentence_streaming.get('enable_typing_simulation', True) else '❌ 否'}")
            st.write(f"• 支持发送风格: {', '.join(sentence_streaming.get('streaming_styles', ['normal', 'fast', 'slow', 'thinking']))}")
        
        # 增强功能模块状态
        st.subheader("🔧 增强模块状态")
        col1, col2 = st.columns(2)
        
        with col1:
            if self.enhanced_modules_available:
                st.success("✅ 增强功能模块已加载")
                st.write("• SemanticRhythmDetector: ✅ 可用")
                st.write("• ContinuousInputProcessor: ✅ 可用")
                st.write("• IntelligentResponseCoordinator: ✅ 可用")
                st.write("• PerformanceMonitor: ✅ 可用")
                st.write("• SentenceStreamer: ✅ 可用")
                st.write("• EnhancedTextProcessor: ✅ 可用")
            else:
                st.warning("⚠️ 增强功能模块未加载")
                st.write("• 部分高级功能可能不可用")
        
        with col2:
            # 性能监控信息（如果可用）
            if self.enhanced_modules_available:
                try:
                    from utils import PerformanceMonitor
                    monitor = PerformanceMonitor()
                    health_status = monitor.get_health_status()
                    st.write(f"• 系统健康状态: {health_status}")
                    
                    report = monitor.get_performance_report()
                    st.write(f"• 平均响应时间: {report.get('avg_response_time', 'N/A')}秒")
                    st.write(f"• 成功率: {report.get('success_rate', 'N/A')}%")
                except Exception as e:
                    st.write(f"• 性能监控: 暂不可用")
    
    def render_character_editor(self):
        """渲染角色编辑器"""
        st.header("🎭 角色管理 v7.5")
        
        st.info("💡 更改将实时同步到主程序！基于田中清美的真实背景 - 优化情绪表达")
        
        character = self.load_config('character_profile')
        
        basic_info = character.get('basic_info', {})
        personality = character.get('personality', {})
        background = character.get('life_history', {})
        professional = character.get('professional_background', {})
        interests = character.get('personal_interests', {})
        preferences = character.get('conversation_preferences', {})
        
        # 基础信息
        st.subheader("👤 基础信息")
        col1, col2 = st.columns(2)
        
        with col1:
            basic_info['name'] = st.text_input("英文名", basic_info.get('name', 'Tanaka Kiyomi'), key="name_en")
            basic_info['chinese_name'] = st.text_input("中文名", basic_info.get('chinese_name', '田中 清美'), key="name_cn")
            basic_info['age'] = st.number_input("年龄", min_value=1, max_value=100, value=basic_info.get('age', 33), key="age")
        
        with col2:
            basic_info['birthday'] = st.text_input("生日", basic_info.get('birthday', '1992-08-22'), key="birthday")
            basic_info['current_city'] = st.text_input("当前城市", basic_info.get('current_city', 'London'), key="city")
            basic_info['occupation'] = st.text_input("职业", basic_info.get('occupation', 'Founder of Trading Company & Jewelry Company & Gold Options Investor'), key="occupation")
        
        # 个人经历
        st.subheader("📖 个人经历")
        background['childhood'] = st.text_area(
            "童年经历", 
            background.get('childhood', 'Parents passed away in an overseas accident when I was 6, raised by my uncle (PhD in Economics from Hitotsubashi University)'),
            key="childhood"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            background['marriage'] = st.text_input(
                "婚姻经历", 
                background.get('marriage', 'Got married after university, divorced in the third year due to husband\'s infidelity'),
                key="marriage"
            )
        with col2:
            background['migration'] = st.text_input(
                "迁移经历", 
                background.get('migration', 'Moved to the UK in 2016, been here for 9 years'),
                key="migration"
            )
        
        # 性格特点
        st.subheader("💫 性格设置")
        col1, col2 = st.columns(2)
        
        with col1:
            traits_text = ", ".join(personality.get('core_traits', []))
            new_traits = st.text_area("性格特质 (逗号分隔)", traits_text, key="traits")
            personality['core_traits'] = [t.strip() for t in new_traits.split(",") if t.strip()]
            
            personality['conversation_style'] = st.text_area(
                "对话风格", 
                personality.get('conversation_style', 'Elegant and professional, as natural as communicating with business partners, with appropriate emotional expression'),
                key="conv_style"
            )
        
        with col2:
            current_humor = personality.get('humor_level', 6)
            personality['humor_level'] = st.slider(
                "幽默等级", 
                min_value=1,
                max_value=10,
                value=current_humor,
                key="humor"
            )
            
            current_empathy = personality.get('empathy_level', 8)
            personality['empathy_level'] = st.slider(
                "同理心等级", 
                min_value=1,
                max_value=10,
                value=current_empathy,
                key="empathy"
            )
            
            current_energy = personality.get('energy_level', 7)
            personality['energy_level'] = st.slider(
                "精力等级", 
                min_value=1,
                max_value=10,
                value=current_energy,
                key="energy"
            )
            
            current_ei = personality.get('emotional_intelligence', 8)
            personality['emotional_intelligence'] = st.slider(
                "情绪智能", 
                min_value=1,
                max_value=10,
                value=current_ei,
                key="ei"
            )
        
        # 对话偏好 - 新增增强功能设置
        st.subheader("💬 对话偏好")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'conversation_preferences' not in character:
                character['conversation_preferences'] = {}
            
            preferences['use_natural_segmentation'] = st.checkbox(
                "使用自然分段", 
                value=preferences.get('use_natural_segmentation', True),
                key="natural_segmentation"
            )
            
            preferences['enable_self_reference'] = st.checkbox(
                "启用自我引用", 
                value=preferences.get('enable_self_reference', True),
                key="self_reference"
            )
            
            preferences['enable_topic_extension'] = st.checkbox(
                "启用话题扩展", 
                value=preferences.get('enable_topic_extension', True),
                key="topic_extension"
            )
            
            preferences['enable_semantic_rhythm'] = st.checkbox(
                "启用语义节奏检测", 
                value=preferences.get('enable_semantic_rhythm', True),
                key="semantic_rhythm"
            )
        
        with col2:
            preferences['enable_continuous_processing'] = st.checkbox(
                "启用连续输入处理", 
                value=preferences.get('enable_continuous_processing', True),
                key="continuous_processing"
            )
            
            preferences['enable_enhanced_quoting'] = st.checkbox(
                "启用增强引用", 
                value=preferences.get('enable_enhanced_quoting', True),
                key="enhanced_quoting_pref"
            )
            
            preferences['enable_emotional_override'] = st.checkbox(
                "启用情绪优先覆盖", 
                value=preferences.get('enable_emotional_override', True),
                key="emotional_override_pref"
            )
            
            preferences['enable_sentence_streaming'] = st.checkbox(
                "启用逐句发送", 
                value=preferences.get('enable_sentence_streaming', True),
                key="sentence_streaming_pref"
            )
        
        # 保存按钮
        if st.button("💾 保存角色配置", type="primary"):
            character['basic_info'] = basic_info
            character['personality'] = personality
            character['life_history'] = background
            character['last_updated'] = datetime.now().isoformat()
            character['conversation_preferences'] = preferences
            
            if self.save_config('character_profile', character):
                st.success("✅ 角色配置已保存！")
                time.sleep(1)
                st.rerun()
    
    def render_reply_settings(self):
        """渲染回复设置"""
        st.header("⚙️ 回复设置 v7.5")
        
        st.info("💡 调整AI的回复行为和高级功能设置")
        
        reply_settings = self.load_config('reply_settings')
        
        timing = reply_settings.get('timing', {})
        behavior = reply_settings.get('behavior', {})
        response_control = reply_settings.get('response_control', {})
        smart_conv = reply_settings.get('smart_conversation', {})
        advanced_features = reply_settings.get('advanced_features', {})
        enhanced_quoting = reply_settings.get('enhanced_quoting', {})
        emotional_override = reply_settings.get('emotional_override', {})
        sentence_streaming = reply_settings.get('sentence_streaming', {})
        
        # 基础行为设置
        st.subheader("🔄 基础行为")
        col1, col2 = st.columns(2)
        
        with col1:
            behavior['auto_reply_enabled'] = st.checkbox(
                "启用自动回复", 
                value=behavior.get('auto_reply_enabled', True),
                key="auto_reply"
            )
            
            behavior['use_emojis'] = st.checkbox(
                "使用表情符号", 
                value=behavior.get('use_emojis', True),
                key="use_emojis"
            )
            
            behavior['detect_typing_status'] = st.checkbox(
                "检测打字状态", 
                value=behavior.get('detect_typing_status', True),
                key="detect_typing"
            )
            
            behavior['handle_reply_references'] = st.checkbox(
                "处理回复引用", 
                value=behavior.get('handle_reply_references', True),
                key="handle_references"
            )
        
        with col2:
            behavior['smart_typing_detection'] = st.checkbox(
                "智能打字检测", 
                value=behavior.get('smart_typing_detection', True),
                key="smart_typing"
            )
            
            behavior['advanced_personality'] = st.checkbox(
                "高级人设一致性", 
                value=behavior.get('advanced_personality', True),
                key="advanced_personality"
            )
            
            behavior['enable_smart_quoting'] = st.checkbox(
                "启用智能引用", 
                value=behavior.get('enable_smart_quoting', True),
                key="smart_quoting"
            )
            
            behavior['emotional_quoting_enabled'] = st.checkbox(
                "启用情绪引用", 
                value=behavior.get('emotional_quoting_enabled', True),
                key="emotional_quoting"
            )
        
        # 时间控制
        st.subheader("⏱️ 时间控制")
        col1, col2 = st.columns(2)
        
        with col1:
            timing['min_reply_interval'] = st.number_input(
                "最小回复间隔(秒)", 
                min_value=0,
                max_value=60,
                value=timing.get('min_reply_interval', 2),
                key="min_interval"
            )
            
            timing['max_reply_interval'] = st.number_input(
                "最大回复间隔(秒)", 
                min_value=1,
                max_value=300,
                value=timing.get('max_reply_interval', 60),
                key="max_interval"
            )
            
            timing['typing_speed_chars_per_min'] = st.number_input(
                "打字速度(字符/分钟)", 
                min_value=50,
                max_value=500,
                value=timing.get('typing_speed_chars_per_min', 200),
                key="typing_speed"
            )
        
        with col2:
            timing['thinking_time_base'] = st.number_input(
                "基础思考时间(秒)", 
                min_value=0.0,
                max_value=10.0,
                value=timing.get('thinking_time_base', 1.5),
                step=0.1,
                key="thinking_base"
            )
            
            timing['typing_detection_timeout'] = st.number_input(
                "打字检测超时(秒)", 
                min_value=1,
                max_value=30,
                value=timing.get('typing_detection_timeout', 3),
                key="typing_timeout"
            )
            
            timing['max_wait_time'] = st.number_input(
                "最大等待时间(秒)", 
                min_value=5,
                max_value=60,
                value=timing.get('max_wait_time', 10),
                key="max_wait"
            )
        
        # 智能对话设置
        st.subheader("🧠 智能对话")
        col1, col2 = st.columns(2)
        
        with col1:
            smart_conv['enable_smart_detection'] = st.checkbox(
                "启用智能检测", 
                value=smart_conv.get('enable_smart_detection', True),
                key="smart_detection"
            )
            
            smart_conv['enable_rhythm_management'] = st.checkbox(
                "启用节奏管理", 
                value=smart_conv.get('enable_rhythm_management', True),
                key="rhythm_management"
            )
            
            smart_conv['semantic_completion_detection'] = st.checkbox(
                "语义完成检测", 
                value=smart_conv.get('semantic_completion_detection', True),
                key="semantic_completion"
            )
            
            smart_conv['enable_self_reference'] = st.checkbox(
                "启用自我引用", 
                value=smart_conv.get('enable_self_reference', True),
                key="self_ref_smart"
            )
        
        with col2:
            smart_conv['enable_topic_extension'] = st.checkbox(
                "启用话题扩展", 
                value=smart_conv.get('enable_topic_extension', True),
                key="topic_ext_smart"
            )
            
            smart_conv['enable_semantic_rhythm_detection'] = st.checkbox(
                "启用语义节奏检测", 
                value=smart_conv.get('enable_semantic_rhythm_detection', True),
                key="semantic_rhythm_detection"
            )
            
            smart_conv['enable_intelligent_response'] = st.checkbox(
                "启用智能响应", 
                value=smart_conv.get('enable_intelligent_response', True),
                key="intelligent_response"
            )
            
            smart_conv['contextual_memory_weight'] = st.slider(
                "上下文记忆权重", 
                min_value=0.0,
                max_value=1.0,
                value=smart_conv.get('contextual_memory_weight', 0.4),
                step=0.1,
                key="memory_weight"
            )
        
        # 高级功能设置
        st.subheader("🚀 高级功能")
        col1, col2 = st.columns(2)
        
        with col1:
            advanced_features['enable_advanced_emotion'] = st.checkbox(
                "启用高级情绪引擎", 
                value=advanced_features.get('enable_advanced_emotion', True),
                key="advanced_emotion"
            )
            
            advanced_features['enable_semantic_splitting'] = st.checkbox(
                "启用语义分割", 
                value=advanced_features.get('enable_semantic_splitting', True),
                key="semantic_splitting"
            )
            
            advanced_features['enable_logic_detection'] = st.checkbox(
                "启用逻辑检测", 
                value=advanced_features.get('enable_logic_detection', True),
                key="logic_detection"
            )
            
            advanced_features['enable_async_queue'] = st.checkbox(
                "启用异步队列", 
                value=advanced_features.get('enable_async_queue', True),
                key="async_queue"
            )
        
        with col2:
            advanced_features['enable_busy_state'] = st.checkbox(
                "启用忙碌状态", 
                value=advanced_features.get('enable_busy_state', True),
                key="busy_state"
            )
            
            advanced_features['enable_text_sanitization'] = st.checkbox(
                "启用文本净化", 
                value=advanced_features.get('enable_text_sanitization', True),
                key="text_sanitization"
            )
            
            advanced_features['enable_semantic_rhythm'] = st.checkbox(
                "启用语义节奏", 
                value=advanced_features.get('enable_semantic_rhythm', True),
                key="semantic_rhythm_adv"
            )
            
            advanced_features['enable_intelligent_coordination'] = st.checkbox(
                "启用智能协调", 
                value=advanced_features.get('enable_intelligent_coordination', True),
                key="intelligent_coordination"
            )
        
        # 新增：增强引用设置
        st.subheader("💬 增强引用管理")
        col1, col2 = st.columns(2)
        
        with col1:
            enhanced_quoting['enable_user_recent_quoting'] = st.checkbox(
                "启用用户最近消息引用", 
                value=enhanced_quoting.get('enable_user_recent_quoting', True),
                key="user_recent_quoting"
            )
            
            enhanced_quoting['enable_ai_self_quoting'] = st.checkbox(
                "启用AI自我引用", 
                value=enhanced_quoting.get('enable_ai_self_quoting', True),
                key="ai_self_quoting"
            )
            
            enhanced_quoting['enable_topic_continuation'] = st.checkbox(
                "启用话题延续引用", 
                value=enhanced_quoting.get('enable_topic_continuation', True),
                key="topic_continuation"
            )
        
        with col2:
            enhanced_quoting['enable_clarification_quoting'] = st.checkbox(
                "启用澄清请求引用", 
                value=enhanced_quoting.get('enable_clarification_quoting', True),
                key="clarification_quoting"
            )
            
            enhanced_quoting['enable_emotional_continuation'] = st.checkbox(
                "启用情感延续引用", 
                value=enhanced_quoting.get('enable_emotional_continuation', True),
                key="emotional_continuation"
            )
            
            enhanced_quoting['similarity_threshold'] = st.slider(
                "引用相似度阈值", 
                min_value=0.0,
                max_value=1.0,
                value=enhanced_quoting.get('similarity_threshold', 0.6),
                step=0.1,
                key="similarity_threshold"
            )
        
        # 新增：情绪优先覆盖设置
        st.subheader("🎭 情绪优先覆盖")
        col1, col2 = st.columns(2)
        
        with col1:
            emotional_override['enable_urgent_override'] = st.checkbox(
                "启用紧急消息覆盖", 
                value=emotional_override.get('enable_urgent_override', True),
                key="urgent_override"
            )
            
            emotional_override['enable_emotional_override'] = st.checkbox(
                "启用情感消息覆盖", 
                value=emotional_override.get('enable_emotional_override', True),
                key="emotional_override_main"
            )
        
        with col2:
            emotional_override['enable_intimate_override'] = st.checkbox(
                "启用亲密消息覆盖", 
                value=emotional_override.get('enable_intimate_override', True),
                key="intimate_override"
            )
            
            emotional_override['enable_crisis_override'] = st.checkbox(
                "启用危机消息覆盖", 
                value=emotional_override.get('enable_crisis_override', True),
                key="crisis_override"
            )
        
        # 新增：逐句发送设置
        st.subheader("💬 逐句发送")
        col1, col2 = st.columns(2)
        
        with col1:
            sentence_streaming['enable_streaming'] = st.checkbox(
                "启用逐句发送", 
                value=sentence_streaming.get('enable_streaming', True),
                key="enable_streaming"
            )
            
            sentence_streaming['min_length_for_streaming'] = st.number_input(
                "最小发送长度(字符)", 
                min_value=10,
                max_value=200,
                value=sentence_streaming.get('min_length_for_streaming', 50),
                key="min_streaming_length"
            )
            
            sentence_streaming['max_sentence_length'] = st.number_input(
                "最大句子长度(字符)", 
                min_value=50,
                max_value=200,
                value=sentence_streaming.get('max_sentence_length', 100),
                key="max_sentence_length"
            )
        
        with col2:
            sentence_streaming['sentence_delay_base'] = st.number_input(
                "基础句子延迟(秒)", 
                min_value=0.1,
                max_value=2.0,
                value=sentence_streaming.get('sentence_delay_base', 0.5),
                step=0.1,
                key="sentence_delay"
            )
            
            sentence_streaming['typing_delay_multiplier'] = st.number_input(
                "打字延迟倍数", 
                min_value=0.001,
                max_value=0.1,
                value=sentence_streaming.get('typing_delay_multiplier', 0.01),
                step=0.001,
                key="typing_delay"
            )
            
            sentence_streaming['enable_typing_simulation'] = st.checkbox(
                "启用打字模拟", 
                value=sentence_streaming.get('enable_typing_simulation', True),
                key="typing_simulation"
            )
        
        # 保存按钮
        if st.button("💾 保存回复设置", type="primary"):
            reply_settings['timing'] = timing
            reply_settings['behavior'] = behavior
            reply_settings['response_control'] = response_control
            reply_settings['smart_conversation'] = smart_conv
            reply_settings['advanced_features'] = advanced_features
            reply_settings['enhanced_quoting'] = enhanced_quoting
            reply_settings['emotional_override'] = emotional_override
            reply_settings['sentence_streaming'] = sentence_streaming
            
            if self.save_config('reply_settings', reply_settings):
                st.success("✅ 回复设置已保存！")
                time.sleep(1)
                st.rerun()
    
    def render_system_config(self):
        """渲染系统配置"""
        st.header("🔧 系统配置 v7.5")
        
        st.info("💡 配置系统级参数和功能开关")
        
        system_config = self.load_config('system_config')
        
        # 系统功能开关
        st.subheader("🔄 系统功能")
        col1, col2 = st.columns(2)
        
        with col1:
            system_config['PROACTIVE_CARE'] = st.checkbox(
                "主动关怀", 
                value=system_config.get('PROACTIVE_CARE', True),
                key="proactive_care"
            )
            
            system_config['EMOTION_ANALYSIS'] = st.checkbox(
                "情绪分析", 
                value=system_config.get('EMOTION_ANALYSIS', True),
                key="emotion_analysis"
            )
            
            system_config['RELATIONSHIP_TRACKING'] = st.checkbox(
                "关系追踪", 
                value=system_config.get('RELATIONSHIP_TRACKING', True),
                key="relationship_tracking"
            )
            
            system_config['REALTIME_UPDATE'] = st.checkbox(
                "实时更新", 
                value=system_config.get('REALTIME_UPDATE', True),
                key="realtime_update"
            )
        
        with col2:
            system_config['BUSINESS_MODE'] = st.checkbox(
                "商务模式", 
                value=system_config.get('BUSINESS_MODE', True),
                key="business_mode"
            )
            
            system_config['ENABLE_SMART_SCHEDULE'] = st.checkbox(
                "智能作息", 
                value=system_config.get('ENABLE_SMART_SCHEDULE', True),
                key="smart_schedule"
            )
            
            system_config['ENABLE_SHORT_MESSAGE'] = st.checkbox(
                "短消息模式", 
                value=system_config.get('ENABLE_SHORT_MESSAGE', True),
                key="short_message"
            )
            
            system_config['ENABLE_EMOTIONAL_QUOTING'] = st.checkbox(
                "情绪引用", 
                value=system_config.get('ENABLE_EMOTIONAL_QUOTING', True),
                key="emotional_quoting_sys"
            )
        
        # 高级功能开关
        st.subheader("🚀 高级功能")
        col1, col2 = st.columns(2)
        
        with col1:
            system_config['ENABLE_LIGHT_MEMORY'] = st.checkbox(
                "轻记忆系统", 
                value=system_config.get('ENABLE_LIGHT_MEMORY', True),
                key="light_memory"
            )
            
            system_config['ENABLE_ADVANCED_FEATURES'] = st.checkbox(
                "高级功能", 
                value=system_config.get('ENABLE_ADVANCED_FEATURES', True),
                key="advanced_features_sys"
            )
            
            system_config['ENABLE_SEMANTIC_RHYTHM'] = st.checkbox(
                "语义节奏检测", 
                value=system_config.get('ENABLE_SEMANTIC_RHYTHM', True),
                key="semantic_rhythm_sys"
            )
            
            system_config['ENABLE_CONTINUOUS_INPUT_PROCESSING'] = st.checkbox(
                "连续输入处理", 
                value=system_config.get('ENABLE_CONTINUOUS_INPUT_PROCESSING', True),
                key="continuous_processing_sys"
            )
        
        with col2:
            system_config['ENABLE_INTELLIGENT_COORDINATION'] = st.checkbox(
                "智能响应协调", 
                value=system_config.get('ENABLE_INTELLIGENT_COORDINATION', True),
                key="intelligent_coordination_sys"
            )
            
            system_config['ENABLE_ENHANCED_QUOTING'] = st.checkbox(
                "增强引用管理", 
                value=system_config.get('ENABLE_ENHANCED_QUOTING', True),
                key="enhanced_quoting_sys"
            )
            
            system_config['ENABLE_EMOTIONAL_OVERRIDE'] = st.checkbox(
                "情绪优先覆盖", 
                value=system_config.get('ENABLE_EMOTIONAL_OVERRIDE', True),
                key="emotional_override_sys"
            )
            
            system_config['ENABLE_SENTENCE_STREAMING'] = st.checkbox(
                "逐句发送", 
                value=system_config.get('ENABLE_SENTENCE_STREAMING', True),
                key="sentence_streaming_sys"
            )
        
        # 保存按钮
        if st.button("💾 保存系统配置", type="primary"):
            if self.save_config('system_config', system_config):
                st.success("✅ 系统配置已保存！")
                time.sleep(1)
                st.rerun()
    
    def render_api_config(self):
        """渲染API配置"""
        st.header("🔑 API配置")
        
        st.info("💡 配置API密钥和模型设置")
        
        api_config = self.load_config('api_config')
        
        col1, col2 = st.columns(2)
        
        with col1:
            api_config['OPENAI_API_KEY'] = st.text_input(
                "OpenAI API Key", 
                value=api_config.get('OPENAI_API_KEY', ''),
                type="password",
                key="openai_key"
            )
            
            api_config['USER_API_ID'] = st.text_input(
                "Telegram API ID", 
                value=api_config.get('USER_API_ID', ''),
                key="api_id"
            )
        
        with col2:
            api_config['USER_API_HASH'] = st.text_input(
                "Telegram API Hash", 
                value=api_config.get('USER_API_HASH', ''),
                type="password",
                key="api_hash"
            )
            
            api_config['USER_PHONE'] = st.text_input(
                "Telegram Phone", 
                value=api_config.get('USER_PHONE', ''),
                key="phone"
            )
        
        # AI模型选择
        model_options = ["deepseek-chat", "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-sonnet", "claude-3-opus"]
        api_config['AI_MODEL'] = st.selectbox(
            "AI模型", 
            options=model_options,
            index=model_options.index(api_config.get('AI_MODEL', 'deepseek-chat')) if api_config.get('AI_MODEL') in model_options else 0,
            key="ai_model"
        )
        
        # 保存按钮
        if st.button("💾 保存API配置", type="primary"):
            if self.save_config('api_config', api_config):
                st.success("✅ API配置已保存！")
                time.sleep(1)
                st.rerun()
    
    def render_relationships(self):
        """渲染关系管理"""
        st.header("👥 关系管理")
        
        relationships = self.load_config('relationships')
        
        if not relationships or not isinstance(relationships, dict):
            st.warning("暂无关系数据")
            relationships = {}
        
        # 关系列表
        for user_id, rel_data in relationships.items():
            with st.expander(f"用户 {user_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**关系等级**: {rel_data.get('relationship_level', 'N/A')}")
                    st.write(f"**信任度**: {rel_data.get('trust_level', 'N/A')}")
                    st.write(f"**亲密度**: {rel_data.get('intimacy_level', 'N/A')}")
                
                with col2:
                    st.write(f"**最后互动**: {rel_data.get('last_interaction', 'N/A')}")
                    st.write(f"**消息计数**: {rel_data.get('message_count', 0)}")
                    st.write(f"**互动频率**: {rel_data.get('interaction_frequency', 'N/A')}")
        
        # 关系统计
        if relationships:
            total_users = len(relationships)
            active_users = sum(1 for rel in relationships.values() if self.is_recent(rel.get('last_interaction', '')))
            
            st.info(f"**统计信息**: 总用户 {total_users} | 活跃用户 {active_users}")
        
        # 手动刷新按钮
        if st.button("🔄 刷新关系数据"):
            st.rerun()
    
    def render_enhanced_features(self):
        """渲染增强功能控制"""
        st.header("🚀 增强功能控制 v7.5")
        
        st.info("💡 控制高级AI功能的开关和参数")
        
        if not self.enhanced_modules_available:
            st.warning("⚠️ 增强功能模块未加载，部分功能可能不可用")
        
        # 语义节奏检测
        st.subheader("🎵 语义节奏检测")
        col1, col2 = st.columns(2)
        
        with col1:
            enable_semantic_rhythm = st.checkbox(
                "启用语义节奏检测", 
                value=self.enhanced_features.get('enable_semantic_rhythm', True),
                key="semantic_rhythm_control"
            )
            
            if enable_semantic_rhythm:
                rhythm_sensitivity = st.slider(
                    "节奏敏感度", 
                    min_value=0.1,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    key="rhythm_sensitivity"
                )
        
        with col2:
            if enable_semantic_rhythm and self.enhanced_modules_available:
                try:
                    from utils import SemanticRhythmDetector
                    detector = SemanticRhythmDetector()
                    rhythm_status = detector.get_status()
                    st.write(f"**检测器状态**: {rhythm_status}")
                except Exception as e:
                    st.write(f"**检测器状态**: 不可用 - {e}")
        
        # 连续输入处理
        st.subheader("📥 连续输入处理")
        col1, col2 = st.columns(2)
        
        with col1:
            enable_continuous_input = st.checkbox(
                "启用连续输入处理", 
                value=self.enhanced_features.get('enable_continuous_input_processing', True),
                key="continuous_input_control"
            )
            
            if enable_continuous_input:
                merge_threshold = st.slider(
                    "合并阈值(秒)", 
                    min_value=1,
                    max_value=30,
                    value=10,
                    key="merge_threshold"
                )
        
        with col2:
            if enable_continuous_input and self.enhanced_modules_available:
                try:
                    from utils import ContinuousInputProcessor
                    processor = ContinuousInputProcessor()
                    processor_status = processor.get_status()
                    st.write(f"**处理器状态**: {processor_status}")
                except Exception as e:
                    st.write(f"**处理器状态**: 不可用 - {e}")
        
        # 智能响应协调
        st.subheader("🤝 智能响应协调")
        col1, col2 = st.columns(2)
        
        with col1:
            enable_intelligent_coordination = st.checkbox(
                "启用智能响应协调", 
                value=self.enhanced_features.get('enable_intelligent_coordination', True),
                key="intelligent_coordination_control"
            )
            
            if enable_intelligent_coordination:
                coordination_level = st.slider(
                    "协调级别", 
                    min_value=1,
                    max_value=10,
                    value=7,
                    key="coordination_level"
                )
        
        with col2:
            if enable_intelligent_coordination and self.enhanced_modules_available:
                try:
                    from utils import IntelligentResponseCoordinator
                    coordinator = IntelligentResponseCoordinator()
                    coordinator_status = coordinator.get_status()
                    st.write(f"**协调器状态**: {coordinator_status}")
                except Exception as e:
                    st.write(f"**协调器状态**: 不可用 - {e}")
        
        # 性能监控
        st.subheader("📊 性能监控")
        col1, col2 = st.columns(2)
        
        with col1:
            enable_performance_monitoring = st.checkbox(
                "启用性能监控", 
                value=self.enhanced_features.get('enable_performance_monitoring', True),
                key="performance_monitoring_control"
            )
        
        with col2:
            if enable_performance_monitoring and self.enhanced_modules_available:
                try:
                    from utils import PerformanceMonitor
                    monitor = PerformanceMonitor()
                    health_status = monitor.get_health_status()
                    st.write(f"**系统健康**: {health_status}")
                    
                    report = monitor.get_performance_report()
                    st.write(f"**平均响应时间**: {report.get('avg_response_time', 'N/A')}秒")
                    st.write(f"**成功率**: {report.get('success_rate', 'N/A')}%")
                except Exception as e:
                    st.write(f"**监控状态**: 不可用 - {e}")
        
        # 保存增强功能设置
        if st.button("💾 保存增强功能设置", type="primary"):
            self.enhanced_features['enable_semantic_rhythm'] = enable_semantic_rhythm
            self.enhanced_features['enable_continuous_input_processing'] = enable_continuous_input
            self.enhanced_features['enable_intelligent_coordination'] = enable_intelligent_coordination
            self.enhanced_features['enable_performance_monitoring'] = enable_performance_monitoring
            
            # 更新系统配置
            system_config = self.load_config('system_config')
            system_config['ENABLE_SEMANTIC_RHYTHM'] = enable_semantic_rhythm
            system_config['ENABLE_CONTINUOUS_INPUT_PROCESSING'] = enable_continuous_input
            system_config['ENABLE_INTELLIGENT_COORDINATION'] = enable_intelligent_coordination
            
            if self.save_config('system_config', system_config):
                st.success("✅ 增强功能设置已保存！")
                time.sleep(1)
                st.rerun()
    
    def render_quick_actions(self):
        """渲染快速操作面板"""
        st.header("⚡ 快速操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 检查配置文件", use_container_width=True):
                if self._check_configs():
                    st.success("✅ 所有配置文件正常！")
                else:
                    st.error("❌ 配置文件存在问题，请检查！")
        
        with col2:
            if st.button("🔧 修复配置文件", use_container_width=True):
                self.run_fix_configs()
        
        with col3:
            if st.button("📊 刷新仪表板", use_container_width=True):
                st.rerun()
        
        # 程序控制
        st.subheader("🖥️ 程序控制")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ 启动主程序", type="primary", use_container_width=True):
                if not self._is_main_running():
                    try:
                        subprocess.Popen([sys.executable, "main_assistant.py"])
                        st.success("✅ 主程序已启动！")
                        time.sleep(2)
                    except Exception as e:
                        st.error(f"❌ 启动失败: {e}")
                else:
                    st.warning("⚠️ 主程序已在运行中")
        
        with col2:
            if st.button("⏹️ 停止主程序", type="secondary", use_container_width=True):
                if self._is_main_running():
                    try:
                        import psutil
                        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                            try:
                                cmdline = process.info.get('cmdline', [])
                                if cmdline and 'main_assistant.py' in ' '.join(cmdline):
                                    process.terminate()
                                    st.success("✅ 主程序已停止！")
                                    time.sleep(2)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                    except ImportError:
                        st.warning("⚠️ 需要 psutil 库来停止程序")
                else:
                    st.warning("⚠️ 主程序未在运行")
        
        # 快速设置预设
        st.subheader("🎯 快速预设")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💼 商务模式", use_container_width=True):
                self._apply_business_preset()
        
        with col2:
            if st.button("💬 社交模式", use_container_width=True):
                self._apply_social_preset()
        
        with col3:
            if st.button("🎭 情感模式", use_container_width=True):
                self._apply_emotional_preset()
    
    def _apply_business_preset(self):
        """应用商务模式预设"""
        try:
            # 更新系统配置
            system_config = self.load_config('system_config')
            system_config['BUSINESS_MODE'] = True
            system_config['PROACTIVE_CARE'] = True
            system_config['ENABLE_SHORT_MESSAGE'] = False
            
            # 更新回复设置
            reply_settings = self.load_config('reply_settings')
            behavior = reply_settings.get('behavior', {})
            behavior['use_emojis'] = False
            behavior['be_casual'] = False
            behavior['emotional_quoting_enabled'] = False
            
            timing = reply_settings.get('timing', {})
            timing['min_reply_interval'] = 3
            timing['max_reply_interval'] = 30
            
            self.save_config('system_config', system_config)
            self.save_config('reply_settings', reply_settings)
            
            st.success("✅ 商务模式已应用！")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ 应用预设失败: {e}")
    
    def _apply_social_preset(self):
        """应用社交模式预设"""
        try:
            # 更新系统配置
            system_config = self.load_config('system_config')
            system_config['BUSINESS_MODE'] = False
            system_config['PROACTIVE_CARE'] = True
            system_config['ENABLE_SHORT_MESSAGE'] = True
            
            # 更新回复设置
            reply_settings = self.load_config('reply_settings')
            behavior = reply_settings.get('behavior', {})
            behavior['use_emojis'] = True
            behavior['be_casual'] = True
            behavior['emotional_quoting_enabled'] = True
            
            timing = reply_settings.get('timing', {})
            timing['min_reply_interval'] = 1
            timing['max_reply_interval'] = 15
            
            self.save_config('system_config', system_config)
            self.save_config('reply_settings', reply_settings)
            
            st.success("✅ 社交模式已应用！")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ 应用预设失败: {e}")
    
    def _apply_emotional_preset(self):
        """应用情感模式预设"""
        try:
            # 更新系统配置
            system_config = self.load_config('system_config')
            system_config['EMOTION_ANALYSIS'] = True
            system_config['ENABLE_EMOTIONAL_QUOTING'] = True
            
            # 更新回复设置
            reply_settings = self.load_config('reply_settings')
            behavior = reply_settings.get('behavior', {})
            behavior['emotional_quoting_enabled'] = True
            behavior['use_emojis'] = True
            
            smart_conv = reply_settings.get('smart_conversation', {})
            smart_conv['contextual_memory_weight'] = 0.6
            
            self.save_config('system_config', system_config)
            self.save_config('reply_settings', reply_settings)
            
            st.success("✅ 情感模式已应用！")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ 应用预设失败: {e}")
    
    def run(self):
        """运行控制面板"""
        st.title("👑 Kiyomi AI Assistant 控制中心 v7.5")
        st.markdown("---")
        
        # 侧边栏导航
        st.sidebar.title("🎛️ 导航")
        
        pages = {
            "📊 系统仪表板": self.render_dashboard,
            "🎭 角色管理": self.render_character_editor,
            "⚙️ 回复设置": self.render_reply_settings,
            "🔧 系统配置": self.render_system_config,
            "🔑 API配置": self.render_api_config,
            "👥 关系管理": self.render_relationships,
            "🚀 增强功能": self.render_enhanced_features,
            "⚡ 快速操作": self.render_quick_actions
        }
        
        selected_page = st.sidebar.radio("选择页面", list(pages.keys()))
        
        # 显示选中的页面
        pages[selected_page]()
        
        # 底部信息
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **Kiyomi AI Assistant v7.5**
        
        基于田中清美的真实背景
        优化的情绪表达和智能对话
        """)

def main():
    """主函数"""
    try:
        control = BackendControl()
        control.run()
    except Exception as e:
        st.error(f"❌ 控制面板启动失败: {e}")
        st.info("💡 请确保所有依赖项已正确安装")

if __name__ == "__main__":
    main()
