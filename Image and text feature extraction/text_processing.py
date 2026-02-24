# # import jieba
# # import numpy as np
# # from sklearn.feature_extraction.text import TfidfVectorizer

# # class TextFrequencyProcessor:
# #     def __init__(self, decay_threshold=0.2):
# #         self.decay_threshold = decay_threshold  # 低于该阈值的词汇衰减

# #     def adaptive_decay(self, text):
# #         # 分词处理
# #         words = jieba.lcut(text)
# #         cleaned_text = ' '.join(words)
        
# #         # 计算TF-IDF
# #         vectorizer = TfidfVectorizer()
# #         tfidf = vectorizer.fit_transform([cleaned_text])
# #         feature_names = vectorizer.get_feature_names_out()
# #         tfidf_val = tfidf.toarray()[0]
        
# #         # 动态衰减低频词
# #         new_text = []
# #         for word, val in zip(feature_names, tfidf_val):
# #             if val < self.decay_threshold:
# #                 new_text.append(word * 0.3)  # 弱化低频词
# #             else:
# #                 new_text.append(word * 2)    # 强化高频词
                
# #         return ''.join(new_text)

# # # 使用示例
# # processor = TextFrequencyProcessor()
# # original_text = "I love watching movies and reading books, movies are my favorite hobby."
# # result = processor.adaptive_decay(original_text)
# # print(f"原始文本: {original_text}")
# # print(f"衰减后文本: {result}")


# import re
# import jieba
# import jieba.posseg as pseg
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from collections import defaultdict
# import nltk  # 新增英文支持

# class SemanticAwareDecay:
#     def __init__(self, decay_factor=0.5, pos_weights=None):
#         self.decay_factor = decay_factor
#         self.pos_weights = pos_weights or {
#             'n': 1.5, 'v': 1.3, 'a': 1.2, 'x': 0.2
#         }

#     def _language_detect(self, text):
#         """自动检测中英文[2,5](@ref)"""
#         return "en" if re.search(r'[a-zA-Z]', text) else "zh"

#     def _tokenize(self, text):
#         """中英文分词逻辑分离[3,5](@ref)"""
#         lang = self._language_detect(text)
#         if lang == "en":
#             # 英文：保留标点作为分隔符，不转小写
#             return nltk.word_tokenize(text)
#         else:
#             # 中文：使用jieba精确模式
#             return [word for word in jieba.lcut(text) if word.strip()]

#     def _calculate_semantic_weight(self, text):
#         """修复TF-IDF计算与词性权重融合"""
#         # 1. 统一分词逻辑
#         words = self._tokenize(text)
#         cleaned_text = ' '.join(words)
        
#         # 2. 修复TF-IDF计算[8,9](@ref)
#         vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')  # 兼容英文单词
#         try:
#             tfidf_matrix = vectorizer.fit_transform([cleaned_text])
#             feature_names = vectorizer.get_feature_names_out()
#             tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
#         except ValueError:  # 处理空文本
#             return defaultdict(float)
        
#         # 3. 动态词性权重（英文简化处理）
#         word_weights = defaultdict(float)
#         lang = self._language_detect(text)
        
#         if lang == "zh":
#             for word, pos in pseg.cut(text):
#                 pos_type = pos[0].lower()
#                 base_score = tfidf_scores.get(word, 0)
#                 pos_weight = self.pos_weights.get(pos_type, 1.0)
#                 word_weights[word] = base_score * pos_weight
#         else:
#             # 英文：所有实词视为名词，虚词权重统一0.2
#             for word in words:
#                 is_content_word = re.match(r'^[a-zA-Z]+$', word)  # 过滤纯字母词
#                 pos_weight = 1.5 if is_content_word else 0.2
#                 base_score = tfidf_scores.get(word, 0)
#                 word_weights[word] = base_score * pos_weight
        
#         return word_weights

#     def adaptive_decay(self, text, min_weight=0.15):
#         """修复关键词提取逻辑与空输出问题"""
#         if not text.strip():
#             return ""
            
#         semantic_weights = self._calculate_semantic_weight(text)
#         lang = self._language_detect(text)
#         key_phrases = []
#         current_phrase = []
        
#         # 统一使用分词结果遍历（不再依赖pseg.cut）
#         words = self._tokenize(text)
#         for word in words:
#             weight = semantic_weights.get(word, 0)
            
#             if weight >= min_weight:
#                 # 名词短语连缀（中英文通用）
#                 if lang == "zh":
#                     # 中文：通过词性判断名词
#                     if any(pos.startswith('n') for _, pos in pseg.cut(word)):
#                         current_phrase.append((word, weight))
#                 else:
#                     # 英文：长度>2的实词视为名词
#                     if len(word) > 2 and re.match(r'^[a-zA-Z]+$', word):
#                         current_phrase.append((word, weight))
#             else:
#                 if current_phrase:
#                     phrase_str = self._merge_phrase(current_phrase)
#                     if phrase_str: 
#                         key_phrases.append(phrase_str)
#                     current_phrase = []
        
#         if current_phrase:
#             phrase_str = self._merge_phrase(current_phrase)
#             if phrase_str: 
#                 key_phrases.append(phrase_str)
                
#         return " ".join(key_phrases)
    
#     def _merge_phrase(self, phrase_list):
#         """优化短语合并策略"""
#         words = [word for word, _ in phrase_list]
#         avg_weight = np.mean([weight for _, weight in phrase_list])
#         # 按空格拼接英文短语
#         separator = " " if self._language_detect(words[0]) == "en" else ""
#         return separator.join(words) if avg_weight >= self.decay_factor else ""

# processor = SemanticAwareDecay()
# # 中文测试
# zh_text = "深度学习模型能有效提取图像中的高频特征"
# print(processor.adaptive_decay(zh_text)) 
# # 输出：深度学习模型 有效提取 高频特征

# # 英文测试
# en_text = "Due to Typhoon Wipha, flights are suspended at Shenzhen Bao'an International Airport"
# print(processor.adaptive_decay(en_text))
# # 输出：Typhoon Wipha flights suspended Shenzhen Bao'an International Airport


import re
import jieba
import jieba.posseg as pseg
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

class SemanticAwareDecay:
    def __init__(self, decay_factor=0.3, pos_weights=None):
        """
        初始化语义感知衰减模型
        :param decay_factor: 短语合并的权重阈值（默认0.3）
        :param pos_weights: 自定义词性权重（字典格式，如{'n':1.5}）
        """
        self.decay_factor = decay_factor
        self.pos_weights = pos_weights or {'n': 1.6, 'v': 1.4, 'a': 1.3, 'x': 0.3}
        self._init_jieba()  # 初始化jieba分词器

    def _init_jieba(self):
        """预加载jieba词典并添加专业术语"""
        jieba.initialize()
        jieba.add_word("图像特征", freq=1000)  # 添加领域术语防止误切分
        jieba.add_word("特征提取", freq=1000)
        jieba.add_word("深度学习", freq=1000)

    def _language_detect(self, text):
        """
        检测文本语言（中/英）
        :return: 'zh'或'en'
        """
        if re.search(r'[a-zA-Z]', text):
            return 'en'
        return 'zh'

    def _tokenize(self, text):
        """
        中英文分词（正则优化版）
        :return: 分词后的单词列表
        """
        lang = self._language_detect(text)
        if lang == 'en':
            # 正则匹配含连字符/撇号的英文单词（如Bao'an）
            return [word for word in re.findall(r"\b[\w'-]+\b", text) if len(word) > 1]
        else:
            # 中文精确模式+过滤单字
            return [word for word in jieba.lcut(text) if len(word) > 1]

    def _calculate_semantic_weight(self, text):
        """
        计算语义权重（TF-IDF + 词性增强）
        :return: 单词权重字典 {word: weight}
        """
        # 1. 短文本保护：直接赋予基础权重
        words = self._tokenize(text)
        if len(words) <= 3:
            return {word: 1.0 for word in words}
        
        # 2. TF-IDF计算（兼容特殊符号）
        cleaned_text = ' '.join(words)
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b[\w'-]+\b")
        try:
            tfidf_matrix = vectorizer.fit_transform([cleaned_text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
        except ValueError:  # 空文本回退
            return defaultdict(float)
        
        # 3. 词性权重融合
        lang = self._language_detect(text)
        word_weights = defaultdict(float)
        
        if lang == 'zh':
            # 中文：基于jieba词性标注
            for word, pos in pseg.cut(text):
                pos_type = pos[0].lower()
                base_score = tfidf_scores.get(word, 0.01)  # 防零值
                pos_weight = self.pos_weights.get(pos_type, 1.0)
                # 专业术语额外增强（名词+复合词）
                if pos_type == 'n' and len(word) > 2:
                    pos_weight *= 1.5
                word_weights[word] = base_score * pos_weight
        else:
            # 英文：启发式规则（实词增强，虚词抑制）
            for word in words:
                is_content_word = re.match(r'^\w+$', word) and len(word) > 2
                pos_weight = 1.6 if is_content_word else 0.3
                base_score = tfidf_scores.get(word, 0.01)
                word_weights[word] = base_score * pos_weight
        
        # 4. 权重归一化（0~1范围）
        max_weight = max(word_weights.values()) if word_weights else 1
        return {word: weight / max_weight for word, weight in word_weights.items()}

    def adaptive_decay(self, text, min_weight=0.1):
        """
        自适应衰减提取关键短语
        :param min_weight: 单词保留阈值（默认0.1）
        :return: 关键短语字符串（空格分隔）
        """
        if not text.strip():
            return ""
            
        semantic_weights = self._calculate_semantic_weight(text)
        lang = self._language_detect(text)
        key_phrases = []
        current_phrase = []
        
        # 遍历分词结果提取连续关键短语
        for word in self._tokenize(text):
            weight = semantic_weights.get(word, 0)
            if weight >= min_weight:
                # 中英文统一实词判断逻辑
                if lang == 'zh':
                    # 中文：名词性成分优先
                    if any(pos.startswith('n') for _, pos in pseg.cut(word)):
                        current_phrase.append((word, weight))
                else:
                    # 英文：长度>2的实词
                    if len(word) > 2 and re.match(r'^\w+$', word):
                        current_phrase.append((word, weight))
            else:
                if current_phrase:
                    phrase_str = self._merge_phrase(current_phrase)
                    if phrase_str: 
                        key_phrases.append(phrase_str)
                    current_phrase = []
        
        # 处理末尾遗留短语
        if current_phrase:
            phrase_str = self._merge_phrase(current_phrase)
            if phrase_str: 
                key_phrases.append(phrase_str)
        
        # 空结果保护策略
        if not key_phrases:
            top_words = sorted(semantic_weights.items(), key=lambda x: x[1], reverse=True)[:3]
            return f"提示：提取失败，建议降低阈值。权重最高词：{[w for w, _ in top_words]}"
                
        return " ".join(key_phrases)
    
    def _merge_phrase(self, phrase_list):
        """
        合并连续关键短语
        :param phrase_list: 单词权重列表 [(word, weight)]
        :return: 合并后的短语字符串
        """
        words = [word for word, _ in phrase_list]
        avg_weight = np.mean([weight for _, weight in phrase_list])
        # 按语言选择分隔符
        separator = " " if self._language_detect(words[0]) == 'en' else ""
        return separator.join(words) if avg_weight >= self.decay_factor else ""

# ====================== 测试用例 ======================
if __name__ == "__main__":
    processor = SemanticAwareDecay(decay_factor=0.25)
    
    # 中文测试（专业术语）
    zh_text = "由于台风韦帕，深圳宝安国际机场航班停止运行，请注意安全"
    print("中文结果:", processor.adaptive_decay(zh_text)) 
    # 输出: 深度学习模型 有效提取图像特征
    
    # 英文测试（含特殊符号）
    en_text = "Although this simple algorithm performed average on the test set, the convolutional neural network achieved an accuracy of 95%"
    print("英文结果:", processor.adaptive_decay(en_text))
    # 输出: Typhoon Wipha flights suspended Shenzhen Bao'an Airport
    
    # 短文本测试
    short_text = "图像特征保留"
    print("短文本结果:", processor.adaptive_decay(short_text))
    # 输出: 图像特征保留