import spacy
import os
from py2neo import Graph
from goujianzhishitupu import preprocess_data, build_knowledge_graph
from question import classify_question

# 定义数据文件路径
data_file_path = r"C:\Users\86187\Desktop\知识图谱\nba球星.xlsx"
nlp_sm = spacy.load("zh_core_web_sm")
nlp_custom = spacy.load("./model")

# 预处理数据并构建知识图谱
def main():
    # 调试路径
    print(f"Trying to access file at: {data_file_path}")
    if not os.path.exists(data_file_path):
        print(f"File not found: {data_file_path}")
        return

    # 预处理数据
    df = preprocess_data(data_file_path)

    # 构建知识图谱
    build_knowledge_graph(df)

    # 连接到 Neo4j 数据库
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "wsng030610"))

    while True:
        # 输入问题并分类
        question = input("请输入您的问题（或输入 '退出' 以结束）: ")
        if question.lower() == '退出':
            break
        matched_categories = classify_question(question)
        if not matched_categories:
            print("对不起，我无法回答你的问题，请使用规范的语言提问")
            continue
        responses = []
        processed_players = set()
        for category in matched_categories:
            if category in ["duogeqiuxing", "dangeqiu", "qiuxingbiaoqian"]:
                responses.extend(handle_player_questions(question, category, processed_players, graph))
            elif category == "zuigaofen":
                responses.append(handle_highest_score(graph))
            elif category == "zuidifen":
                responses.append(handle_lowest_score(graph))
            elif category == "biaoqianxiaqiuxing":
                responses.extend(handle_tagged_player_questions(question, graph))

        if responses:
            for response in responses:
                print(response)
        else:
            print("对不起，我不明白你的问题。")

def handle_player_questions(question, category, processed_players, graph):
    responses = []
    for ent in nlp_sm(question).ents:
        if ent.label_ == "PERSON" and ent.text not in processed_players:
            player_name = ent.text
            query = "MATCH (p:Player {name: $name}) RETURN p"
            result = graph.run(query, name=player_name).data()
            if result:
                player = result[0]['p']
                response = generate_player_response(player, category, question)
                responses.append(response)
                processed_players.add(player_name)
            else:
                responses.append(f"没有找到关于 {player_name} 的信息。")
    return responses

def generate_player_response(player, category, question):
    if category == "qiuxingbiaoqian":
        if "位置" in question:
            return f"{player['name']} 是一名 {player['position']} 球员。"
        elif "球队" in question:
            return f"{player['name']} 效力于 {player['team']}。"
        elif "号" in question or "号码" in question:
            return f"{player['name']} 身穿 {player['number']} 号球衣。"
        elif "场均得分" in question or "均分" in question:
            return f"{player['name']} 的场均得分是 {player['points_per_game']}。"
    else:
        return (
            f"{player['name']} 是一名 {player['position']} 球员，效力于 {player['team']}。"
            f"他身穿 {player['number']} 号球衣，场均得分 {player['points_per_game']}。"
        )

def handle_highest_score(graph):
    query = "MATCH (p:Player) RETURN p ORDER BY p.points_per_game DESC LIMIT 1"
    result = graph.run(query).data()
    if result:
        player = result[0]['p']
        return f"场均得分最高的球员是 {player['name']}，他的得分是 {player['points_per_game']}。"
    else:
        return "没有找到相关信息。"
def handle_lowest_score(graph):
    query = "MATCH (p:Player) RETURN p ORDER BY p.points_per_game ASC LIMIT 1"
    result = graph.run(query).data()
    if result:
        player = result[0]['p']
        return f"场均得分最低的球员是 {player['name']}，他的得分是 {player['points_per_game']}。"
    else:
        return "没有找到相关信息。"
def handle_tagged_player_questions(question, graph):
    responses = []
    team_found = False
    position_found = False
    number_found = False
    team_name = None
    position = None
    number = None

    for ent in nlp_custom(question).ents:
        if ent.label_ == "team":
            team_found = True
            team_name = ent.text
        elif ent.label_ == "position":
            position_found = True
            position = ent.text
        elif ent.label_ == "number":
            number_found = True
            number = ent.text

    # 设定参数X
    X = f"{int(team_found)}{int(position_found)}{int(number_found)}"
    print(X)
    if X == "000":
        responses.append("没有找到任何实体信息。")
    elif X == "001":  # 只有号码
        query = "MATCH (p:Player {number: $number}) RETURN p"
        result = graph.run(query, number=int(number)).data()
        if result:
            player_names = [player['p']['name'] for player in result]
            response = f"号码为 {number} 的球星有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到号码为 {number} 的信息。")
    elif X == "010":  # 只有位置
        query = "MATCH (p:Player)-[:PLAYS_IN]->(pos:Position {name: $position}) RETURN p.name AS player_name"
        result = graph.run(query, position=position).data()
        if result:
            player_names = [player['player_name'] for player in result]
            response = f"{position} 有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到位置为 {position} 的信息。")
    elif X == "011":  # 位置和号码
        query = "MATCH (p:Player {number: $number})-[:PLAYS_IN]->(pos:Position {name: $position}) RETURN p.name AS player_name"
        result = graph.run(query, position=position, number=int(number)).data()
        if result:
            player_names = [player['player_name'] for player in result]
            response = f"号码为 {number} 的 {position} 有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到号码为 {number} 的 {position}。")
    elif X == "100":  # 只有球队
        query = "MATCH (t:Team {name: $team_name})<-[:PLAYS_FOR]-(p:Player) RETURN p.name AS player_name"
        result = graph.run(query, team_name=team_name).data()
        if result:
            player_names = [player['player_name'] for player in result]
            response = f"效力于 {team_name} 的球星有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到关于 {team_name} 的信息。")
    elif X == "101":  # 球队和号码
        query = "MATCH (t:Team {name: $team_name})<-[:PLAYS_FOR]-(p:Player {number: $number}) RETURN p.name AS player_name"
        result = graph.run(query, team_name=team_name, number=int(number)).data()
        if result:
            player_names = [player['player_name'] for player in result]
            response = f"效力于 {team_name} 的号码为 {number} 的球星有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到效力于 {team_name} 的号码为 {number} 的球星。")
    elif X == "110":  # 球队和位置
        query = "MATCH (t:Team {name: $team_name})<-[:PLAYS_FOR]-(p:Player)-[:PLAYS_IN]->(pos:Position {name: $position}) RETURN p.name AS player_name"
        result = graph.run(query, team_name=team_name, position=position).data()
        if result:
            player_names = [player['player_name'] for player in result]
            response = f"效力于 {team_name} 的 {position} 有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到效力于 {team_name} 的 {position}。")
    elif X == "111":  # 球队、位置和号码
        query = "MATCH (t:Team {name: $team_name})<-[:PLAYS_FOR]-(p:Player {number: $number})-[:PLAYS_IN]->(pos:Position {name: $position}) RETURN p.name AS player_name"
        result = graph.run(query, team_name=team_name, position=position, number=int(number)).data()
        if result:
            player_names = [player['player_name'] for player in result]
            response = f"效力于 {team_name} 的号码为 {number} 的 {position} 有 {', '.join(player_names)}。"
            responses.append(response)
        else:
            responses.append(f"没有找到效力于 {team_name} 的号码为 {number} 的 {position}。")

    return responses

if __name__ == "__main__":
    main()
