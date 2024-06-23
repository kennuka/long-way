# Импорт библиотек

# Библиотека networkx (networkx.org) - библиотека для работы с графами
# Потребуется только для хранения графа
import networkx as nx

import pandas as pd
import heapq
import math
import random

# Будем рисовать анимации в Jupyter для понимания процесса работы алгоритма
import matplotlib.animation
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import HTML


# Получим данные по ссылке, указанной выше
df = pd.read_csv("https://paste.sr.ht/blob/8ce2a2a7668a09cd852bc59f3987ef126ffe4bc3")

# Соберём вершины графа
pub_dict = df.to_dict('index')
g = nx.Graph()
g.add_nodes_from(pub_dict)

# Создадим словарь с широтой и долготой вершин графа
pos_dict = { k: (v['lon'], v['lat']) for k,v in pub_dict.items() }

# Сколько всего вершин
len(g.nodes())


# Функция dist считает расстояние в градусах
# между вершинами с индексами idx1 и idx2
def dist(idx1: int, idx2: int) -> float:
  (p1x,p1y) = pos_dict.get(idx1)
  (p2x,p2y) = pos_dict.get(idx2)
  dx = p2x - p1x
  dy = p2y - p1y
  return math.sqrt(dx*dx + dy*dy)
# Сколько градусов можем пройти
WALK_DIST = 0.02

# Добавляем в граф наши рёбра
g.clear_edges()
for k, v in pub_dict.items():
  edges = set()
  min_edge = None
  for k2, v2 in pub_dict.items():
    if k != k2 and dist(k, k2) < WALK_DIST:
      edges.add((k, k2, dist(k, k2)))
    if k != k2 and (min_edge is None or min_edge[2] > dist(k, k2)):
      min_edge = (k, k2, dist(k, k2))
  if len(edges) == 0:
    edges.add(min_edge)
  g.add_weighted_edges_from(edges)

# Сколько всего получилось рёбер
len(g.edges())

def init_animation(g, pos):
  fig, ax = plt.subplots()
  return {'graph': g, 'pos': pos, 'fig': fig, 'ax': ax, 'frames': []}

def save_frame(an, title, visited, seen):
  an.get('frames').append({'title': title, 'visited': visited.copy(), 'seen': seen.copy()})

def draw_animation(an):
  G = an.get('graph')
  ax = an.get('ax')
  fig = an.get('fig')
  pos = an.get('pos')
  frames = an.get('frames')

  def update(num):
    ax.clear()

    frame = frames[num]
    title = frame.get('title')
    visited = frame.get('visited')
    seen = frame.get('seen')

    # Background nodes
    nx.draw_networkx_edges(G, pos=pos, ax=ax, edge_color="gray")
    null_nodes = nx.draw_networkx_nodes(G, pos=pos, nodelist=set(G.nodes()) - set(visited) - set(seen), node_color="white",  ax=ax)
    null_nodes.set_edgecolor("black")

    # Visited nodes
    vis_nodes = nx.draw_networkx_nodes(G, pos=pos, nodelist=set(visited), node_color="black",  ax=ax)
    vis_nodes.set_edgecolor("black")

    # Seen nodes
    seen_nodes = nx.draw_networkx_nodes(G, pos=pos, nodelist=set(seen), node_color="gray", ax=ax)
    seen_nodes.set_edgecolor("white")
    # nx.draw_networkx_labels(G, pos=pos, labels=dict(zip(path,path)),  font_color="white", ax=ax)
    # edgelist = [path[k:k+2] for k in range(len(path) - 1)]
    # nx.draw_networkx_edges(G, pos=pos, edgelist=edgelist, width=idx_weights[:len(path)], ax=ax)

    # Scale plot ax
    ax.set_title("Frame %d:    "%(num+1) + " - " + title, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])

  ani = matplotlib.animation.FuncAnimation(fig, update, frames=len(frames), interval=1000, repeat=True)
  return HTML(ani.to_jshtml())


# Просто нарисуем граф со всеми вершинами и их номерами
node_labels_dict = { k: k for k, _v in pub_dict.items() }
nx.draw(g, pos=pos_dict, labels=node_labels_dict, node_size=20)
# Можем использовать spring_layout, чтобы видеть лучше (правда, это не поможет)
#     nx.draw(g, pos=nx.spring_layout(g), labels=node_labels_dict, node_size=20)


FROM = 41
TO = 85

# Инициализируем анимацию. Если хотите реальные положения вершин, поменяйте на
#     an = init_animation(g, pos_dict)
an = init_animation(g, nx.spring_layout(g))

# Функция выполняет BFS из вершины start
def bfs(g, start):
  visited = {}
  visited[start] = True

  queue = [start]
  while queue:
    cur = queue.pop()

    # сохраняем кадр анимации
    save_frame(an, str(cur), visited, queue)

    # проходимся по соседям вершины cur
    for neighbour in g.neighbors(cur):
      if not visited.get(neighbour, False):
        visited[neighbour] = True
        queue.append(neighbour)

# Запустим BFS из исходной вершины
bfs(g, FROM)

# Нарисуем, что получилось
draw_animation(an)

an = init_animation(g, pos_dict)
