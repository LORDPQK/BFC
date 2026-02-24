import re
import math
import numpy as np
import torch
# from transformers import BertTokenizer, BertForMaskedLM
from collections import defaultdict
# from sklearn.feature_extraction.text import TfidfVectorizer

# 1. 定义文本中的“高频信息”量化指标（信息熵+TF-IDF加权）
def calculate_word_entropy(corpus):
    """
    计算每个词在语料中的信息熵（作为抗衰减能力的量化指标）
    :param corpus: 文本列表，如 ["这是一个示例句子", "这是另一个例子"]
    :return: 字典{词: 信息熵}
    """
    left_contexts = defaultdict(lambda: defaultdict(int))  # 左邻接字统计
    right_contexts = defaultdict(lambda: defaultdict(int))  # 右邻接字统计
    word_freq = defaultdict(int)  # 词频统计
    
    # 遍历语料构建统计信息
    for text in corpus:
        words = re.findall(r'\w+', text.lower())  # 简单分词
        for i, word in enumerate(words):
            # 统计左邻接字（前一个词）
            if i > 0:
                left_word = words[i-1]
                left_contexts[word][left_word] += 1
            # 统计右邻接字（后一个词）
            if i < len(words)-1:
                right_word = words[i+1]
                right_contexts[word][right_word] += 1
            word_freq[word] += 1
    
    # 计算每个词的信息熵（左右邻接熵均值）
    word_entropy = {}
    for word, total_count in word_freq.items():
        entropy = 0
        # 计算左邻接熵
        left_total = sum(left_contexts[word].values())
        for count in left_contexts[word].values():
            p = count / left_total
            entropy -= p * math.log(p + 1e-10)  # 避免log(0)
        # 计算右邻接熵
        right_total = sum(right_contexts[word].values())
        for count in right_contexts[word].values():
            p = count / right_total
            entropy -= p * math.log(p + 1e-10)
        word_entropy[word] = entropy / 2  # 取左右熵均值[1,2](@ref)
    
    return word_entropy

# 2. 动态降噪滤波器（模拟图像衰减）
def adaptive_noise_filter(text, entropy_scores, decay_ratio=0.5):
    """
    基于信息熵的文本降噪：保留高频信息（高熵词），衰减低频信息
    :param text: 输入文本
    :param entropy_scores: 词信息熵字典
    :param decay_ratio: 衰减比例（0-1）
    :return: 降噪后文本（保留核心信息）
    """
    words = re.findall(r'\w+|\S', text.lower())  # 保留标点用于重建
    word_scores = [entropy_scores.get(word, 0) for word in words]
    
    # 确定保留阈值（按信息熵分位数）
    threshold = np.quantile(word_scores, decay_ratio)  
    
    # 动态掩码低熵词（模拟低频信息衰减）
    filtered_text = []
    for word, score in zip(words, word_scores):
        if score >= threshold or not word.isalnum():  # 保留高熵词和标点
            filtered_text.append(word)
        else:
            filtered_text.append("[MASK]")  # 衰减低熵词[6](@ref)
    
    return " ".join(filtered_text)

# 3. 关键信息重建（模拟高频信息复原）
def reconstruct_text(masked_text, model_name="bert-base-chinese"):
    """
    用BERT重建被衰减的文本（模拟高频信息引导复原）
    :param masked_text: 被掩码的文本
    :param model_name: BERT模型名
    :return: 重建后的完整文本
    """
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForMaskedLM.from_pretrained(model_name)
    
    inputs = tokenizer(masked_text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 解码重建结果
    predicted_indices = torch.argmax(outputs.logits, dim=-1)
    reconstructed_tokens = []
    for i, token_id in enumerate(predicted_indices[0]):
        token = tokenizer.convert_ids_to_tokens([token_id])[0]
        # 跳过特殊标记
        if token not in ["[CLS]", "[SEP]", "[PAD]"]:
            if token.startswith("##"):
                reconstructed_tokens[-1] += token[2:]  # 合并子词
            else:
                reconstructed_tokens.append(token)
    
    return "".join(reconstructed_tokens)

# 4. 完整流程演示
if __name__ == "__main__":
    # 示例语料（等待压缩文本）
    corpus = ["Due to Typhoon Wipha, takeoff at Shenzhen International Airport has been suspended. Passengers are advised to pay attention to safety and arrange their travel time reasonably"]
    
    # 步骤1：计算词级信息熵（定义高频信息）
    entropy_scores = calculate_word_entropy(corpus)
    
    # 步骤2：模拟文本衰减（随机选一条文本处理）
    # original_text = "I am a student studying at the university. The weather is nice today, and I plan to go for a walk in the park."
    original_text = "we love the big and sweet apple"
    decayed_text = adaptive_noise_filter(original_text, entropy_scores, decay_ratio=0.6)
    print(f"\n衰减后文本：\n{decayed_text}")
    
    # 步骤3：高频信息引导重建
    # reconstructed_text = reconstruct_text(decayed_text)
    # print(f"\n重建后文本：\n{reconstructed_text}")
    
    # 步骤4：评估重建效果
    # from difflib import SequenceMatcher
    # similarity = SequenceMatcher(None, original_text, reconstructed_text).ratio()
    # print(f"\n语义相似度：{similarity:.2%}")