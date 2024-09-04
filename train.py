import spacy
from spacy.training import Example
import json
import random
import os
# 指定pkuseg模型的路径
pkuseg_model_path = "D:\\python\\Lib\\site-packages\\zh_core_web_sm\\zh_core_web_sm-3.7.0\\tokenizer\\pkuseg_model"
# 加载中文模型
nlp = spacy.load('zh_core_web_sm')
# 创建一个Chinese对象并设置pkuseg模型路径，使用pkuseg作为分词器
zh = spacy.lang.zh.Chinese()
zh.pkuseg_model_path = pkuseg_model_path
# 设置nlp对象的tokenizer为自定义的Chinese对象
nlp.tokenizer = zh.tokenizer
# 读取训练数据
with open('train_data.json', 'r', encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
# 添加NER管道和标签
if 'ner' not in nlp.pipe_names:
    ner = nlp.add_pipe('ner')
else:
    ner = nlp.get_pipe('ner')
# 添加自定义实体标签
for _, annotations in TRAIN_DATA:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])  # 修正这里，使用ent[2]而不是ent['label']
# 开始训练
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):  # 只训练NER
    optimizer = nlp.begin_training()
    for itn in range(30):  # 训练迭代次数
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.15, losses=losses, sgd=optimizer)
        print(itn, losses)
# 保存模型
output_dir = './model'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
nlp.to_disk(output_dir)
print("模型已保存到", output_dir)
# 测试模型的函数
def test_model(text):
    nlp = spacy.load(output_dir)  # 加载训练好的模型
    doc = nlp(text)  # 对文本进行解析
    print("测试文本:", text)
    print("识别的实体:")
    for ent in doc.ents:
        print(ent.text, ent.label_)
# 测试语句
test_text = "凯里·欧文是凯尔特人队的后卫，身穿11号球衣"
# 调用测试函数
if __name__ == "__main__":
    test_model(test_text)