import pandas as pd
from py2neo import Graph, Node, Relationship

# 数据预处理
def preprocess_data(file_path):
    df = pd.read_excel(file_path)  # 读取Excel文件
    # 进行必要的数据清洗和格式化
    df['number'] = df['number'].astype(int)  # 将'number'列转换为整数类型
    df['Points Per Game'] = df['Points Per Game'].astype(float)  # 将'Points Per Game'列转换为浮点数类型
    return df


# 构建知识图谱
# 构建知识图谱
def build_knowledge_graph(df):
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "wsng030610"))  # 连接到Neo4j数据库
    graph.delete_all()  # 清空数据库中的所有节点和关系

    tx = graph.begin()  # 开始一个事务
    try:
        for index, row in df.iterrows():
            player = Node("Player", name=row['name'], number=row['number'],
                          team=row['team'], position=row['position'],
                          points_per_game=row['Points Per Game'])  # 创建一个Player节点
            tx.merge(player, "Player", "name")  # 合并Player节点，确保节点唯一性

            team = Node("Team", name=row['team'])  # 创建一个Team节点
            tx.merge(team, "Team", "name")  # 合并Team节点，确保节点唯一性
            plays_for = Relationship(player, "PLAYS_FOR", team)  # 创建Player和Team之间的关系
            tx.create(plays_for)  # 创建PLAYS_FOR关系

            position = Node("Position", name=row['position'])  # 创建一个Position节点
            tx.merge(position, "Position", "name")  # 合并Position节点，确保节点唯一性
            plays_in = Relationship(player, "PLAYS_IN", position)  # 创建Player和Position之间的关系
            tx.create(plays_in)  # 创建PLAYS_IN关系

        tx.commit()  # 提交事务
    except Exception as e:
        print(f"Error occurred: {e}")  # 打印错误信息
        tx.rollback()  # 回滚事务

