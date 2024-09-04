import json
# 读取txt文件中的实体词
with open('number.txt', 'r', encoding='utf-8') as f:
    numbers = [line.strip() for line in f]
with open('position.txt', 'r', encoding='utf-8') as f:
    positions = [line.strip() for line in f]
with open('team.txt', 'r', encoding='utf-8') as f:
    teams = [line.strip() for line in f]
# 生成训练数据
train_data = []
# 生成包含number的句子
text = f"凯里·欧文是凯尔特人队的后卫，身穿11号球衣"
entities = [(6, 6 + len("凯尔特人"), "team")]
entities.append((12, 12 + len("后卫"), "position"))
entities.append((17, 17 + len("11"), "number"))
train_data.append((text, {"entities": entities}))
for number in numbers:
    text = f"谁的球衣号码是{number}号"
    entities = [(7, 7 + len(number), "number")]
    train_data.append((text, {"entities": entities}))
    text = f"球衣号码是{number}号的球星有谁？"
    entities = [(5, 5 + len(number), "number")]
    train_data.append((text, {"entities": entities}))
    text = f"{number}号的球星有"
    entities = [(0, len(number), "number")]
    train_data.append((text, {"entities": entities}))
    text = f"{number}号都有谁？"
    entities = [(0, len(number), "number")]
    train_data.append((text, {"entities": entities}))
    text = f"谁身穿{number}号球衣？"
    entities = [(3, 3 + len(number), "number")]
    train_data.append((text, {"entities": entities}))
# 生成包含team的句子
for team in teams:
    text = f"{team}队有哪些球星？"
    entities = [(0, len(team), "team")]
    train_data.append((text, {"entities": entities}))
    text = f"{team}的球员有哪些？"
    entities = [(0, len(team), "team")]
    train_data.append((text, {"entities": entities}))
    text = f"哪些球员是{team}队的？"
    entities = [(5, 5 + len(team), "team")]
    train_data.append((text, {"entities": entities}))
    text = f"谁效力于{team}队？"
    entities = [(4, 4 + len(team), "team")]
    train_data.append((text, {"entities": entities}))
# 生成包含position的句子
for position in positions:
    text = f"哪些球员是{position}"
    entities = [(5, 5 + len(position), "position")]
    train_data.append((text, {"entities": entities}))
    text = f"{position}有哪些球员？"
    entities = [(0, len(position), "position")]
    train_data.append((text, {"entities": entities}))
    text = f"{position}的球员有"
    entities = [(0, len(position), "position")]
    train_data.append((text, {"entities": entities}))
# 保存训练数据到train_data.json
with open('train_data.json', 'w', encoding='utf-8') as f:
    json.dump(train_data, f, ensure_ascii=False, indent=4)
