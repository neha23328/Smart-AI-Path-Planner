import tkinter as tk
import random, time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- CONFIG ----------------
GRID_SIZE = 20
CELL_SIZE = 28
COLOR_EMPTY, COLOR_WALL = "black", "#444"
COLOR_START, COLOR_GOAL = "red", "green"
COLOR_VISITED, COLOR_PATH = "#00FFFF", "yellow"
DELAY_VISIT, DELAY_PATH = 0.01, 0.02

# ---------------- PATHFINDING HELPERS ----------------
def is_valid(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and grid[y][x] != 1

def neighbors(x, y):
    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx, ny = x+dx, y+dy
        if is_valid(nx, ny):
            yield nx, ny

def reconstruct(came_from, start, goal):
    if goal not in came_from: return []
    path, cur = [], goal
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    return path[::-1]

def visualize_cell(x, y, color=COLOR_VISITED, delay=DELAY_VISIT):
    draw_cell(x, y, color)
    root.update()
    time.sleep(delay)

# ---------------- ALGORITHMS ----------------
def bfs(start, goal):
    from collections import deque
    q, came = deque([start]), {start: None}
    visited = 0
    while q:
        cur = q.popleft(); visited += 1
        if cur == goal: break
        for nxt in neighbors(*cur):
            if nxt not in came:
                came[nxt] = cur; q.append(nxt)
                visualize_cell(*nxt)
    return reconstruct(came, start, goal), visited

def dfs(start, goal):
    st, came = [start], {start: None}
    visited = 0
    while st:
        cur = st.pop(); visited += 1
        if cur == goal: break
        for nxt in neighbors(*cur):
            if nxt not in came:
                came[nxt] = cur; st.append(nxt)
                visualize_cell(*nxt)
    return reconstruct(came, start, goal), visited

def heuristic(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

def astar(start, goal):
    open_set, came, g = [(0,start)], {start:None}, {start:0}
    visited = 0
    while open_set:
        open_set.sort(); _,cur=open_set.pop(0); visited += 1
        if cur==goal: break
        for nxt in neighbors(*cur):
            tmp = g[cur] + 1
            if nxt not in g or tmp < g[nxt]:
                g[nxt] = tmp
                open_set.append((tmp + heuristic(nxt,goal), nxt))
                came[nxt] = cur
                visualize_cell(*nxt)
    return reconstruct(came,start,goal),visited

def best_first(start,goal):
    open_set, came = [(heuristic(start,goal),start)], {start:None}
    visited = 0
    while open_set:
        open_set.sort(); _,cur=open_set.pop(0); visited += 1
        if cur==goal: break
        for nxt in neighbors(*cur):
            if nxt not in came:
                came[nxt] = cur
                open_set.append((heuristic(nxt,goal),nxt))
                visualize_cell(*nxt)
    return reconstruct(came,start,goal),visited

# ---------------- DRAWING ----------------
def draw_cell(x, y, color):
    canvas.create_rectangle(
        x*CELL_SIZE, y*CELL_SIZE, (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
        fill=color, outline="gray"
    )

def draw_grid():
    canvas.delete("all")
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color = (
                COLOR_WALL if grid[y][x]==1 else
                COLOR_START if (x,y)==start else
                COLOR_GOAL if (x,y)==goal else
                COLOR_EMPTY
            )
            draw_cell(x,y,color)

def generate_grid():
    global grid, start, goal
    grid = [[0 if random.random()>0.2 else 1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    start, goal = (0,0), (GRID_SIZE-1, GRID_SIZE-1)
    grid[0][0]=grid[-1][-1]=0
    draw_grid()
    update_insights("🧠 Grid generated. Choose an algorithm to find path!")
    update_charts(0,0,0,0)

# ---------------- RUN ----------------
def run_algorithm(name):
    algos = {"BFS":bfs,"DFS":dfs,"A*":astar,"Best-First":best_first}
    draw_grid()
    start_time=time.time()
    path,visited=algos[name](start,goal)
    elapsed=round(time.time()-start_time,2)

    for x,y in path:
        visualize_cell(x,y,COLOR_PATH,DELAY_PATH)

    results[name]=visited
    update_charts(
        results.get("BFS",0),results.get("DFS",0),
        results.get("A*",0),results.get("Best-First",0)
    )
    update_insights(f"{name} finished!\n🧩 Nodes: {visited}\n⏱ Time: {elapsed}s\n📏 Path: {len(path)}")

# ---------------- UI ELEMENTS ----------------
def update_insights(text):
    text_ai.config(state="normal")
    text_ai.delete(1.0,tk.END)
    text_ai.insert(tk.END,text)
    text_ai.config(state="disabled")

def update_charts(bfs_n,dfs_n,a_n,best_n):
    vals=[bfs_n,dfs_n,a_n,best_n]
    labels=["BFS","DFS","A*","Best-First"]

    ax1.clear()
    ax1.bar(labels,vals,color=["#FF9999","#66B2FF","#99FF99","#FFCC99"])
    ax1.set_title("Nodes Explored",color="white")
    ax1.tick_params(colors="white")
    canvas_bar.draw()

    ax2.clear()
    if sum(vals)>0:
        ax2.pie(vals,labels=labels,autopct="%1.1f%%",
                colors=["#FF9999","#66B2FF","#99FF99","#FFCC99"],
                textprops={"color":"white"})
    ax2.set_title("Exploration Share",color="white")
    canvas_pie.draw()

# ---------------- MAIN UI ----------------
root = tk.Tk()
root.title("🤖 Smart AI Path Planner")
root.state('zoomed')
root.configure(bg="black")

tk.Label(root,text="SMART AI PATH PLANNER",font=("Arial",22,"bold"),fg="#4CAF50",bg="black").pack(pady=10)

frame_top = tk.Frame(root,bg="black")
frame_top.pack()

# Maze Canvas
canvas = tk.Canvas(frame_top,width=GRID_SIZE*CELL_SIZE,height=GRID_SIZE*CELL_SIZE,bg="black")
canvas.pack(side="left",padx=20)

# Charts beside maze
chart_frame = tk.Frame(frame_top,bg="black")
chart_frame.pack(side="left",padx=20)

fig1,ax1=plt.subplots(figsize=(4.5,3.2),facecolor="black")
fig2,ax2=plt.subplots(figsize=(4.5,3.2),facecolor="black")

canvas_bar=FigureCanvasTkAgg(fig1,master=chart_frame)
canvas_bar.get_tk_widget().pack(pady=5)
canvas_pie=FigureCanvasTkAgg(fig2,master=chart_frame)
canvas_pie.get_tk_widget().pack(pady=5)

# Buttons
btn_frame = tk.Frame(root,bg="black")
btn_frame.pack(pady=10)
for name in ["BFS","DFS","A*","Best-First"]:
    tk.Button(btn_frame,text=f"Run {name}",font=("Arial",12),
              bg="#4CAF50",fg="white",command=lambda n=name: run_algorithm(n)).pack(side="left",padx=10)
tk.Button(btn_frame,text="Generate Grid",font=("Arial",12),
          bg="#2196F3",fg="white",command=generate_grid).pack(side="left",padx=10)

# AI Insights
tk.Label(root,text="AI Insights:",font=("Arial",14,"bold"),fg="white",bg="black").pack(anchor="w",padx=30)
text_ai=tk.Text(root,height=6,width=80,font=("Arial",12),bg="black",fg="white",state="disabled")
text_ai.pack(pady=5,padx=30,anchor="w")

# ---------------- INIT ----------------
results={}
generate_grid()
root.mainloop()
