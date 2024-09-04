import spacy
# 加载预训练模型
#nlp = spacy.load("zh_core_web_sm")
nlp = spacy.load("./model")
# 测试文本
test_texts = [
    "凯里·欧文是独行侠的后卫，身穿11号球衣",
]
# 定义实体类型
entity_types = ["number", "position", "team", "PERSON"]
# 测试每个文本
for text in test_texts:
    doc = nlp(text)
    print(f"测试文本: {text}")
    for ent in doc.ents:
        if  ent.label_ in entity_types:
            print(f"识别到的实体: {ent.text}, 实体类型: {ent.label_}")
