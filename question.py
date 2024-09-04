import ahocorasick
import os
# 定义关键词文件夹路径
keyword_folder = r"C:\Users\86187\Desktop\知识图谱\问题分类"
# 创建自动机
automaton = ahocorasick.Automaton()
# 读取关键词文件并添加到自动机
categories = {}
for filename in os.listdir(keyword_folder):
    category = filename.split('.')[0]  # 从文件名中提取分类名称
    categories[category] = []  # 初始化分类列表
    file_path = os.path.join(keyword_folder, filename)  # 构建文件路径
    with open(file_path, 'r', encoding='utf-8') as file:  # 打开文件，打开方式为读，编码为utf-8
        for line in file:  # 遍历文件每一行
            keyword = line.strip()  # 去除行末的空白字符
            if keyword:  # 如果关键词不为空
                automaton.add_word(keyword, (category, keyword))  # 将关键词添加到自动机
                categories[category].append(keyword)  # 将关键词添加到分类列表
automaton.make_automaton()  # 构建Aho-Corasick自动机
def classify_question(question):
    matched_categories = set()  # 用于存储匹配到的分类
    for end_index, (category, keyword) in automaton.iter(question):  # 遍历自动机匹配结果
        matched_categories.add(category)  # 将匹配到的分类添加到集合中
    return matched_categories  # 返回匹配到的分类集合
# 测试
question = ("11号的球员有哪些")
matched_categories = classify_question(question)
print(f"问题: '{question}' 被分类为: {matched_categories}")
