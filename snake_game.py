import tkinter as tk
import random
import time

# 游戏配置
WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE
FPS = 10

COLOR_BG = "#1a1a2e"
COLOR_GRID = "#16213e"
COLOR_SNAKE_HEAD = "#00d4aa"
COLOR_SNAKE_BODY = "#00a896"
COLOR_FOOD = "#ff6b6b"
COLOR_TEXT = "#eaeaea"
COLOR_SCORE = "#f5a623"


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 贪吃蛇小游戏")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        self._build_ui()
        self._init_game()
        self.root.bind("<KeyPress>", self._on_key)
        self._game_loop()

    def _build_ui(self):
        # 顶部信息栏
        top_frame = tk.Frame(self.root, bg=COLOR_BG, pady=8)
        top_frame.pack(fill=tk.X)

        self.score_label = tk.Label(
            top_frame, text="得分: 0", font=("Arial", 14, "bold"),
            fg=COLOR_SCORE, bg=COLOR_BG
        )
        self.score_label.pack(side=tk.LEFT, padx=16)

        self.best_label = tk.Label(
            top_frame, text="最高: 0", font=("Arial", 14, "bold"),
            fg="#aaaaaa", bg=COLOR_BG
        )
        self.best_label.pack(side=tk.RIGHT, padx=16)

        # 画布
        self.canvas = tk.Canvas(
            self.root, width=WIDTH, height=HEIGHT,
            bg=COLOR_BG, highlightthickness=2,
            highlightbackground="#00d4aa"
        )
        self.canvas.pack(padx=10, pady=(0, 10))

        # 底部提示
        hint = tk.Label(
            self.root,
            text="方向键 / WASD 控制  |  P 暂停  |  R 重新开始",
            font=("Arial", 10), fg="#666688", bg=COLOR_BG
        )
        hint.pack(pady=(0, 8))

    def _init_game(self):
        self.snake = [(COLS // 2, ROWS // 2)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.best = getattr(self, "best", 0)
        self.running = True
        self.paused = False
        self.game_over = False
        self._place_food()

    def _place_food(self):
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in self.snake:
                self.food = pos
                break

    def _on_key(self, event):
        key = event.keysym.lower()
        moves = {
            "up": (0, -1), "w": (0, -1),
            "down": (0, 1), "s": (0, 1),
            "left": (-1, 0), "a": (-1, 0),
            "right": (1, 0), "d": (1, 0),
        }
        if key in moves:
            nd = moves[key]
            # 禁止反向移动
            if (nd[0] + self.direction[0], nd[1] + self.direction[1]) != (0, 0):
                self.next_dir = nd
        elif key == "p":
            if not self.game_over:
                self.paused = not self.paused
        elif key == "r":
            self._init_game()

    def _update(self):
        if self.paused or self.game_over:
            return

        self.direction = self.next_dir
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = ((hx + dx) % COLS, (hy + dy) % ROWS)

        # 撞到自身
        if new_head in self.snake:
            self.game_over = True
            self.running = False
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            if self.score > self.best:
                self.best = self.score
            self._place_food()
        else:
            self.snake.pop()

    def _draw(self):
        c = self.canvas
        c.delete("all")

        # 绘制网格
        for i in range(COLS):
            for j in range(ROWS):
                x1, y1 = i * CELL_SIZE, j * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                c.create_rectangle(x1, y1, x2, y2, fill=COLOR_BG, outline=COLOR_GRID, width=1)

        # 绘制食物（带光晕）
        fx, fy = self.food
        fx1, fy1 = fx * CELL_SIZE + 2, fy * CELL_SIZE + 2
        fx2, fy2 = fx1 + CELL_SIZE - 4, fy1 + CELL_SIZE - 4
        c.create_oval(fx1 - 3, fy1 - 3, fx2 + 3, fy2 + 3, fill="#ff3333", outline="", stipple="gray50")
        c.create_oval(fx1, fy1, fx2, fy2, fill=COLOR_FOOD, outline="#ff9999", width=1)

        # 绘制蛇身
        for idx, (sx, sy) in enumerate(self.snake):
            x1, y1 = sx * CELL_SIZE + 1, sy * CELL_SIZE + 1
            x2, y2 = x1 + CELL_SIZE - 2, y1 + CELL_SIZE - 2
            color = COLOR_SNAKE_HEAD if idx == 0 else COLOR_SNAKE_BODY
            radius = 6 if idx == 0 else 4
            c.create_rectangle(x1, y1, x2, y2, fill=color, outline="", width=0)
            # 圆角效果
            c.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, fill=color, outline="")

        # 蛇眼睛
        hx, hy = self.snake[0]
        ex1 = hx * CELL_SIZE + CELL_SIZE // 2 - 4 + self.direction[0] * 4
        ey1 = hy * CELL_SIZE + CELL_SIZE // 2 - 4 + self.direction[1] * 4
        c.create_oval(ex1, ey1, ex1 + 5, ey1 + 5, fill="white", outline="")
        c.create_oval(ex1 + 2, ey1 + 2, ex1 + 4, ey1 + 4, fill="black", outline="")

        # 更新分数
        self.score_label.config(text=f"得分: {self.score}")
        self.best_label.config(text=f"最高: {self.best}")

        # 暂停提示
        if self.paused:
            self._draw_overlay("⏸ 已暂停", "按 P 继续")

        # 游戏结束提示
        if self.game_over:
            self._draw_overlay(f"💀 游戏结束", f"得分: {self.score}  |  按 R 重新开始")

    def _draw_overlay(self, title, subtitle):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple="gray50")
        c.create_text(WIDTH // 2, HEIGHT // 2 - 24,
                      text=title, font=("Arial", 28, "bold"),
                      fill="#00d4aa")
        c.create_text(WIDTH // 2, HEIGHT // 2 + 20,
                      text=subtitle, font=("Arial", 14),
                      fill="#eaeaea")

    def _game_loop(self):
        self._update()
        self._draw()
        self.root.after(1000 // FPS, self._game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
