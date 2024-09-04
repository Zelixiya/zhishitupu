import pandas as pd
from py2neo import Graph, Node, Relationship
import spacy
def preprocess_data(file_path):
    df = pd.read_excel(file_path)
    df['number'] = df['number'].astype(int)
    df['Points Per Game'] = df['Points Per Game'].astype(float)
    return df
def build_knowledge_graph(df):
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "wsng030610"))
    graph.delete_all()
    for index, row in df.iterrows():
        player = Node("Player", name=row['name'], number=row['number'],
                      team=row['team'], position=row['position'],
                      points_per_game=row['Points Per Game'])
        graph.create(player)
        team = Node("Team", name=row['team'])
        graph.merge(team, "Team", "name")
        plays_for = Relationship(player, "PLAYS_FOR", team)
        graph.create(plays_for)
        position = Node("Position", name=row['position'])
        graph.merge(position, "Position", "name")
        plays_in = Relationship(player, "PLAYS_IN", position)
        graph.create(plays_in)
# 问答机器人
def answer_question(question):
    nlp = spacy.load("zh_core_web_sm")  # 使用更强大的模型
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "wsng030610"))
    doc = nlp(question)
    responses = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            player_name = ent.text
            query = "MATCH (p:Player {name: $name}) RETURN p"
            result = graph.run(query, name=player_name).data()
            if result:
                player = result[0]['p']
                response = f"{player['name']} 是一名 {player['position']} 球员，效力于 {player['team']}。" \
                           f"他身穿 {player['number']} 号球衣，场均得分 {player['points_per_game']}。"
                responses.append(response)
            else:
                responses.append(f"没有找到关于 {player_name} 的信息。")
    if "最高" in question or "最低" in question:
        order = "DESC" if "最高" in question else "ASC"
        query = f"MATCH (p:Player) RETURN p ORDER BY p.points_per_game {order} LIMIT 1"
        result = graph.run(query).data()
        if result:
            player = result[0]['p']
            response = f"场均得分{order.lower()}的球员是 {player['name']}，他效力于 {player['team']}，" \
                       f"身穿 {player['number']} 号球衣，场均得分 {player['points_per_game']}。"
            responses.append(response)
        else:
            responses.append("没有找到相关信息。")
    if not responses:
        responses.append("对不起，我不明白你的问题。")
    return "\n".join(responses)
if __name__ == "__main__":
    file_path = 'C:/Users/86187/Desktop/知识图谱/nba球星.xlsx'
    df = preprocess_data(file_path)
    build_knowledge_graph(df)

    print("问答机器人已启动，输入 'exit' 或 'quit' 退出。")
    while True:
        question = input("你: ")
        if question.lower() in ["exit", "quit"]:
            break
        response = answer_question(question)
        print(f"机器人: {response}")
