import pygame
import random
import sys
import copy

# 画面サイズとブロックサイズの設定
SCREEN_WIDTH = 600  # 画面幅をさらに広げる
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GAME_AREA_WIDTH = 10 * BLOCK_SIZE  # ゲームエリアの幅

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)  # 初期配置のブロック用の色
DARK_GRAY = (30, 30, 30)  # 背景用の暗い灰色
LIGHT_BLUE = (100, 180, 255)  # ボタン用の色

# テトリミノの形状定義
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

# テトリミノの色
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]
# 初期配置のブロック用の特別な色
INITIAL_BLOCK_COLOR = (100, 100, 200)  # 青みがかった色

# ゲームの状態
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAMEOVER = 2
GAME_STATE_WIN = 3
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
    
    def draw(self, screen):
        # ボタンの背景
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)  # 白い枠線
        
        # ボタンのテキスト
        font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        # マウスがボタン上にあるかチェック
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_click):
        # ボタンがクリックされたかチェック
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Tetris:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.width = 10
        self.height = 20
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.initial_blocks_count = 0  # 初期配置されたブロックの数
        self.setup_initial_blocks()  # 初期ブロックを配置
        self.next_pieces = [self.generate_piece() for _ in range(5)]  # 次の5つのテトリミノを生成
        self.current_piece = self.get_next_piece()
        self.hold_piece = None
        self.can_hold = True  # ホールドが使用可能かどうか
        self.game_over = False
        self.game_won = False  # 勝利フラグ
        self.score = 0
    def generate_piece(self):
        # 新しいテトリミノを生成
        shape_idx = random.randint(0, len(SHAPES) - 1)
        piece = {
            'shape': SHAPES[shape_idx],
            'color': SHAPE_COLORS[shape_idx],
            'x': self.width // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }
        return piece
    
    def get_next_piece(self):
        # 次のテトリミノを取得し、新しいテトリミノを追加
        next_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.generate_piece())
        return next_piece
    
    def new_piece(self):
        # 次のテトリミノを取得
        return self.get_next_piece()
    
    def setup_initial_blocks(self):
        # 画面の下部にブロックを配置
        start_row = self.height - 6  # 下から6行分のエリアに配置
        
        # ブロックの塊を作成するためのパラメータ
        cluster_count = 3  # 塊の数
        cluster_size = 3   # 塊の大きさ
        
        # 塊の中心点をランダムに選択
        cluster_centers = []
        for _ in range(cluster_count):
            cx = random.randint(1, self.width - 2)
            cy = random.randint(start_row + 1, self.height - 2)
            cluster_centers.append((cx, cy))
        
        # 各塊の周りにブロックを配置
        for cx, cy in cluster_centers:
            for dy in range(-cluster_size//2, cluster_size//2 + 1):
                for dx in range(-cluster_size//2, cluster_size//2 + 1):
                    x, y = cx + dx, cy + dy
                    # グリッド内かつ中心に近いほど配置確率が高い
                    if (0 <= x < self.width and start_row <= y < self.height and 
                        random.random() < 0.6 - 0.15 * (abs(dx) + abs(dy))):
                        self.grid[y][x] = INITIAL_BLOCK_COLOR
                        self.initial_blocks_count += 1
        
        # 少なくとも12個のブロックを確保
        if self.initial_blocks_count < 12:
            additional_needed = 12 - self.initial_blocks_count
            empty_cells = [(x, y) for y in range(start_row, self.height) 
                          for x in range(self.width) if self.grid[y][x] == 0]
            
            if empty_cells:
                # ランダムに追加のブロックを配置
                for _ in range(min(additional_needed, len(empty_cells))):
                    x, y = random.choice(empty_cells)
                    empty_cells.remove((x, y))
                    self.grid[y][x] = INITIAL_BLOCK_COLOR
                    self.initial_blocks_count += 1
        
        # 初期ブロック数を確認
        actual_count = sum(1 for y in range(self.height) for x in range(self.width) if self.grid[y][x] == INITIAL_BLOCK_COLOR)
        if actual_count != self.initial_blocks_count:
            print(f"警告: 初期ブロック数の不一致 - カウント: {self.initial_blocks_count}, 実際: {actual_count}")
            self.initial_blocks_count = actual_count
        
        print(f"初期ブロック数: {self.initial_blocks_count}")
    def place_bomb_blocks(self):
        # 初期配置されたブロックの中からランダムに爆弾ブロックを配置
        initial_blocks = [(x, y) for y in range(self.height) for x in range(self.width) 
                         if self.grid[y][x] == INITIAL_BLOCK_COLOR]
        
        # 爆弾の数を決定（初期ブロックの約15%、最低1個）
        bomb_count = max(1, self.initial_blocks_count // 7)
        
        # ランダムに爆弾ブロックを選択
        if initial_blocks:
            for _ in range(min(bomb_count, len(initial_blocks))):
                x, y = random.choice(initial_blocks)
                initial_blocks.remove((x, y))
                self.grid[y][x] = BOMB_BLOCK_COLOR
                self.bomb_positions.append((x, y))
                # 爆弾ブロックも初期ブロックの一部なので、カウントは減らさない
    
    def explode_bomb(self, row_idx):
        # 爆弾が消去された時の処理
        # 爆弾のある行とその下の行を消去（計2行）
        rows_to_clear = []
        for r in range(row_idx, min(self.height, row_idx + 2)):
            rows_to_clear.append(r)
        
        # 爆発エフェクトを設定
        self.explosion_effect = {
            'center': (row_idx, 5),  # 爆発の中心（行, 列の中央）
            'radius': 2,             # 爆発の半径（小さくする）
            'frames': 8,             # エフェクトの表示フレーム数（短くする）
            'current_frame': 0       # 現在のフレーム
        }
        
        # 初期ブロックのカウントを更新
        initial_blocks_cleared = 0
        
        for r in rows_to_clear:
            for c in range(self.width):
                if self.grid[r][c] == INITIAL_BLOCK_COLOR:
                    initial_blocks_cleared += 1
        
        # 初期ブロックの数を更新
        self.initial_blocks_count -= initial_blocks_cleared
        print(f"爆弾処理による初期ブロック消去: {initial_blocks_cleared}, 残り: {self.initial_blocks_count}")
        
        # 行を消去
        for r in sorted(rows_to_clear, reverse=True):
            del self.grid[r]
            self.grid.insert(0, [0 for _ in range(self.width)])
        
        # スコアを加算（通常の2倍）
        self.score += len(rows_to_clear) * 200
        
        # すべての初期ブロックが消えたら勝利
        if self.initial_blocks_count <= 0:
            self.game_won = True
            print("爆弾処理で勝利!")
        
        return len(rows_to_clear)
        
        # 初期ブロックのカウントを更新
        initial_blocks_cleared = 0
        
        for r in rows_to_clear:
            for c in range(self.width):
                if self.grid[r][c] == INITIAL_BLOCK_COLOR:
                    initial_blocks_cleared += 1
        
        # 初期ブロックの数を更新
        self.initial_blocks_count -= initial_blocks_cleared
        
        # 行を消去
        for r in sorted(rows_to_clear, reverse=True):
            del self.grid[r]
            self.grid.insert(0, [0 for _ in range(self.width)])
        
        # スコアを加算（通常の2倍）
        self.score += len(rows_to_clear) * 200
        
        # すべての初期ブロックが消えたら勝利
        if self.initial_blocks_count <= 0:
            self.game_won = True
        
        return len(rows_to_clear)
    def valid_position(self, shape, x, y):
        # 指定された位置にテトリミノを配置できるか確認
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= self.width or
                        y + i >= self.height or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True

    def add_to_grid(self):
        # 現在のテトリミノをグリッドに固定
        for i, row in enumerate(self.current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']

    def clear_rows(self):
        # 完成した行を消去
        full_rows = []
        
        for i, row in enumerate(self.grid):
            if all(row):
                full_rows.append(i)
        
        # 通常の行消去処理
        initial_blocks_cleared = 0
        
        for row_idx in full_rows:
            # 行を消去する前に、その行にある初期ブロックの数をカウント
            for c, cell in enumerate(self.grid[row_idx]):
                if cell == INITIAL_BLOCK_COLOR:
                    initial_blocks_cleared += 1
                    print(f"初期ブロックを消去: 行 {row_idx}, 列 {c}")
            
            del self.grid[row_idx]
            self.grid.insert(0, [0 for _ in range(self.width)])
        
        # 初期ブロックの数を更新
        if initial_blocks_cleared > 0:
            self.initial_blocks_count -= initial_blocks_cleared
            print(f"通常処理後の初期ブロック数: {self.initial_blocks_count}")
        
        # すべての初期ブロックが消えたら勝利
        if self.initial_blocks_count <= 0:
            print("すべての初期ブロックを消去しました！勝利！")
            self.game_won = True
        
        return len(full_rows)
    def rotate(self, clockwise=True):
        # テトリミノを回転
        shape = self.current_piece['shape']
        
        if clockwise:
            # 時計回り
            rotated = [[shape[j][i] for j in range(len(shape)-1, -1, -1)] for i in range(len(shape[0]))]
        else:
            # 反時計回り
            rotated = [[shape[j][i] for j in range(len(shape))] for i in range(len(shape[0])-1, -1, -1)]
        
        if self.valid_position(rotated, self.current_piece['x'], self.current_piece['y']):
            self.current_piece['shape'] = rotated

    def move(self, dx, dy):
        # テトリミノを移動
        if self.valid_position(self.current_piece['shape'], self.current_piece['x'] + dx, self.current_piece['y'] + dy):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
            return True
        return False

    def hold(self):
        # ホールド機能
        if not self.can_hold:
            return
        
        if self.hold_piece is None:
            # 初めてホールドする場合
            self.hold_piece = {
                'shape': copy.deepcopy(self.current_piece['shape']),
                'color': self.current_piece['color']
            }
            self.current_piece = self.new_piece()
        else:
            # ホールドを交換する場合
            temp_shape = copy.deepcopy(self.current_piece['shape'])
            temp_color = self.current_piece['color']
            
            self.current_piece = {
                'shape': self.hold_piece['shape'],
                'color': self.hold_piece['color'],
                'x': self.width // 2 - len(self.hold_piece['shape'][0]) // 2,
                'y': 0
            }
            
            self.hold_piece = {
                'shape': temp_shape,
                'color': temp_color
            }
        
        self.can_hold = False  # 一度ホールドしたら、次のテトリミノが落ちるまで使えない

    def drop(self):
        # テトリミノを下に落とす
        if not self.move(0, 1):
            self.add_to_grid()
            cleared_rows = self.clear_rows()
            self.score += cleared_rows * 100
            
            # 残りの初期ブロックを確認
            remaining_blocks = sum(1 for y in range(self.height) for x in range(self.width) if self.grid[y][x] == INITIAL_BLOCK_COLOR)
            if remaining_blocks != self.initial_blocks_count:
                print(f"警告: 初期ブロック数の不一致 - カウント: {self.initial_blocks_count}, 実際: {remaining_blocks}")
                self.initial_blocks_count = remaining_blocks
            
            # 勝利判定を追加
            if self.initial_blocks_count <= 0:
                print("勝利判定: すべての初期ブロックを消去しました！")
                self.game_won = True
                return True
            
            # 新しいテトリミノを生成
            self.current_piece = self.new_piece()
            self.can_hold = True  # 新しいテトリミノが来たらホールドを再度使用可能に
            
            # ゲームオーバー判定
            if not self.valid_position(self.current_piece['shape'], self.current_piece['x'], self.current_piece['y']):
                self.game_over = True
                
            return True
        return False
def draw_grid(screen, grid):
    # グリッドを描画
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, 
                                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, 
                                (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_piece(screen, piece):
    # 現在のテトリミノを描画
    for i, row in enumerate(piece['shape']):
        for j, cell in enumerate(row):
            if cell:
                color = piece['color']
                pygame.draw.rect(screen, color, 
                                ((piece['x'] + j) * BLOCK_SIZE, 
                                 (piece['y'] + i) * BLOCK_SIZE, 
                                 BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, 
                                ((piece['x'] + j) * BLOCK_SIZE, 
                                 (piece['y'] + i) * BLOCK_SIZE, 
                                 BLOCK_SIZE, BLOCK_SIZE), 1)
def draw_hold_piece(screen, piece):
    # ホールドエリアの背景
    hold_x = GAME_AREA_WIDTH + 30
    hold_y = 70  # 下に移動して、スコア表示と重ならないようにする
    
    pygame.draw.rect(screen, DARK_GRAY, (hold_x - 10, hold_y - 10, 100, 100))
    pygame.draw.rect(screen, WHITE, (hold_x - 10, hold_y - 10, 100, 100), 1)
    
    # ホールドテキスト
    font = pygame.font.SysFont(None, 24)
    hold_text = font.render('HOLD', True, WHITE)
    screen.blit(hold_text, (hold_x + 25, hold_y - 30))
    
    # ホールドしているテトリミノを描画
    if piece is not None:
        # I型テトリミノの場合は特別に調整
        scale = 15 if len(piece['shape'][0]) == 4 else 20
        offset_x = 15 if len(piece['shape'][0]) == 4 else 20
        
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'], 
                                   (hold_x + j * scale + offset_x, hold_y + i * scale + 30, scale, scale))
                    pygame.draw.rect(screen, WHITE, 
                                   (hold_x + j * scale + offset_x, hold_y + i * scale + 30, scale, scale), 1)

def draw_next_pieces(screen, next_pieces):
    # 次のテトリミノを描画
    next_x = GAME_AREA_WIDTH + 30
    next_y = 200  # ホールドの下に配置、さらに下に移動
    
    # 次のテトリミノのテキスト
    font = pygame.font.SysFont(None, 24)
    next_text = font.render('NEXT', True, WHITE)
    screen.blit(next_text, (next_x + 25, next_y - 30))
    
    # 表示する次のテトリミノの数を制限（5→3）
    display_count = min(3, len(next_pieces))
    
    # 次のテトリミノを描画（サイズを小さく）
    for idx in range(display_count):
        piece = next_pieces[idx]
        # 背景（サイズを小さく）
        bg_y = next_y + idx * 70  # 間隔を調整して小さく
        pygame.draw.rect(screen, DARK_GRAY, (next_x - 10, bg_y - 10, 90, 60))
        pygame.draw.rect(screen, WHITE, (next_x - 10, bg_y - 10, 90, 60), 1)
        
        # I型テトリミノの場合は特別に調整
        scale = 12 if len(piece['shape'][0]) == 4 else 15  # サイズを小さく
        offset_x = 15 if len(piece['shape'][0]) == 4 else 20
        
        # テトリミノ
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece['color'], 
                                   (next_x + j * scale + offset_x, bg_y + i * scale + 15, scale, scale))
                    pygame.draw.rect(screen, WHITE, 
                                   (next_x + j * scale + offset_x, bg_y + i * scale + 15, scale, scale), 1)
def draw_grid_lines(screen):
    # グリッドの線を描画
    for x in range(0, GAME_AREA_WIDTH, BLOCK_SIZE):  # ゲームエリアのみに線を引く
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (GAME_AREA_WIDTH, y))

def draw_score_area(screen, score, blocks_left):
    # スコア表示エリア
    score_x = GAME_AREA_WIDTH + 30
    score_y = 10
    
    # スコアエリアの背景
    pygame.draw.rect(screen, DARK_GRAY, (GAME_AREA_WIDTH + 10, 0, SCREEN_WIDTH - GAME_AREA_WIDTH - 20, 40))
    pygame.draw.rect(screen, WHITE, (GAME_AREA_WIDTH + 10, 0, SCREEN_WIDTH - GAME_AREA_WIDTH - 20, 40), 1)
    
    # スコアとブロック残数の表示
    font = pygame.font.SysFont(None, 24)
    score_text = font.render(f'Score: {score}', True, WHITE)
    
    # 初期ブロックの残数を表示
    blocks_text = font.render(f'Blocks: {blocks_left}', True, WHITE)
    
    # 表示位置を調整
    screen.blit(score_text, (score_x, score_y))
    screen.blit(blocks_text, (score_x + 110, score_y))

def draw_controls(screen):
    # 操作方法表示エリア - 右下に配置
    controls_x = GAME_AREA_WIDTH + 30
    controls_y = SCREEN_HEIGHT - 150  # さらに上に移動
    
    # 操作方法エリアの背景
    pygame.draw.rect(screen, DARK_GRAY, (GAME_AREA_WIDTH + 10, SCREEN_HEIGHT - 160, 
                                        SCREEN_WIDTH - GAME_AREA_WIDTH - 20, 150))
    pygame.draw.rect(screen, WHITE, (GAME_AREA_WIDTH + 10, SCREEN_HEIGHT - 160, 
                                    SCREEN_WIDTH - GAME_AREA_WIDTH - 20, 150), 1)
    
    # 操作方法のテキスト
    font = pygame.font.SysFont(None, 24)
    title_text = font.render('CONTROLS', True, WHITE)
    screen.blit(title_text, (controls_x + 50, controls_y))
    
    # 操作方法を2列に分けて表示
    controls_left = [
        "<- -> : Move",
        "Down : Soft Drop",
        "Up : Hard Drop"
    ]
    
    controls_right = [
        "A : Rotate Left",
        "D : Rotate Right",
        "S : Hold"
    ]
    
    # 左側の操作方法
    for i, text in enumerate(controls_left):
        ctrl_text = font.render(text, True, WHITE)
        screen.blit(ctrl_text, (controls_x, controls_y + 30 + i * 25))
    
    # 右側の操作方法
    for i, text in enumerate(controls_right):
        ctrl_text = font.render(text, True, WHITE)
        screen.blit(ctrl_text, (controls_x + 120, controls_y + 30 + i * 25))
def draw_explosion(screen, game):
    # 爆発エフェクトを描画
    if game.explosion_effect is None:
        return
    
    effect = game.explosion_effect
    center_y, center_x = effect['center']
    radius = effect['radius'] * (effect['current_frame'] / effect['frames'] + 1)
    
    # 爆発の中心座標（ピクセル単位）
    center_x_px = center_x * BLOCK_SIZE + BLOCK_SIZE // 2
    center_y_px = center_y * BLOCK_SIZE + BLOCK_SIZE // 2
    
    # 爆発の色（フレームによって変化）
    colors = [
        (255, 255, 0),  # 黄色
        (255, 165, 0),  # オレンジ
        (255, 0, 0)     # 赤
    ]
    color_idx = effect['current_frame'] % len(colors)
    
    # 爆発の円を描画
    pygame.draw.circle(screen, colors[color_idx], (center_x_px, center_y_px), radius * BLOCK_SIZE, 3)
    
    # フレームカウントを更新
    effect['current_frame'] += 1
    
    # エフェクトの終了判定
    if effect['current_frame'] >= effect['frames']:
        game.explosion_effect = None
        # 爆発エフェクトが終わったら新しいテトリミノを生成
        game.current_piece = game.new_piece()
        game.can_hold = True
        
        # 勝利判定を追加
        if game.initial_blocks_count <= 0:
            game.game_won = True

def draw_start_screen(screen, font, large_font):
    # 背景
    screen.fill(BLACK)
    
    # タイトル
    title_text = large_font.render("TETRIMINO BREAK", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title_text, title_rect)
    
    # サブタイトル
    subtitle_text = font.render("Clear all initial blocks to win!", True, INITIAL_BLOCK_COLOR)
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
    screen.blit(subtitle_text, subtitle_rect)
    
    # 操作方法
    controls = [
        "Controls:",
        "<- -> : Move",
        "Down : Soft Drop",
        "Up : Hard Drop",
        "A : Rotate Left",
        "D : Rotate Right",
        "S : Hold"
    ]
    
    for i, text in enumerate(controls):
        control_text = font.render(text, True, WHITE)
        control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * 30))
        screen.blit(control_text, control_rect)
    
    # スタートボタン
    start_button = Button(SCREEN_WIDTH // 2 - 100, 500, 200, 50, "START", DARK_GRAY, LIGHT_BLUE)
    start_button.draw(screen)
    
    return start_button
def draw_game_over_screen(screen, font, large_font, score, is_win=False):
    # 半透明のオーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # 半透明の黒
    screen.blit(overlay, (0, 0))
    
    # タイトル
    if is_win:
        title_text = large_font.render("YOU WIN!", True, GREEN)
    else:
        title_text = large_font.render("GAME OVER", True, RED)
    
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    screen.blit(title_text, title_rect)
    
    # スコア
    score_text = font.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 270))
    screen.blit(score_text, score_rect)
    
    # リトライボタン
    retry_button = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "RETRY", DARK_GRAY, LIGHT_BLUE)
    retry_button.draw(screen)
    
    # 終了ボタン
    quit_button = Button(SCREEN_WIDTH // 2 - 100, 420, 200, 50, "QUIT", DARK_GRAY, RED)
    quit_button.draw(screen)
    
    return retry_button, quit_button
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetrimino Break')
    
    # フォントの設定
    try:
        # システムのデフォルトフォント
        font = pygame.font.SysFont(None, 24)
        large_font = pygame.font.SysFont(None, 48)
    except:
        # フォールバック
        font = pygame.font.Font(None, 24)
        large_font = pygame.font.Font(None, 48)
    
    clock = pygame.time.Clock()
    game = Tetris()
    
    # 落下速度の設定
    fall_time = 0
    fall_speed = 1.0  # 秒 (0.5から1.0に変更して半分の速度に)
    
    # ゲームの状態
    game_state = GAME_STATE_START
    
    # ボタン
    start_button = None
    retry_button = None
    quit_button = None
    
    running = True
    while running:
        # マウス位置とクリック状態を取得
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        # 経過時間を計測
        delta_time = clock.tick(60) / 1000
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    mouse_click = True
            
            if game_state == GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_UP:
                        # ハードドロップ
                        while game.move(0, 1):
                            pass
                        game.drop()
                    elif event.key == pygame.K_a:
                        game.rotate(False)  # 反時計回り
                    elif event.key == pygame.K_d:
                        game.rotate(True)   # 時計回り
                    elif event.key == pygame.K_s:
                        game.hold()         # ホールド
        
        # ゲーム状態に応じた処理
        if game_state == GAME_STATE_START:
            # スタート画面
            start_button = draw_start_screen(screen, font, large_font)
            start_button.update(mouse_pos)
            
            if start_button.is_clicked(mouse_pos, mouse_click):
                game_state = GAME_STATE_PLAYING
                game.reset_game()
        
        elif game_state == GAME_STATE_PLAYING:
            # 通常のゲームプレイ
            fall_time += delta_time
            
            # 一定時間ごとにテトリミノを落下
            if fall_time >= fall_speed:
                game.drop()
                fall_time = 0
            
            # ゲームオーバー判定
            if game.game_over:
                game_state = GAME_STATE_GAMEOVER
                print("ゲームオーバー")
            
            # 勝利判定
            if game.game_won:
                game_state = GAME_STATE_WIN
                print("勝利！ゲームクリア画面に移行")
            
            # 描画
            screen.fill(BLACK)
            
            # ゲームエリアの背景
            pygame.draw.rect(screen, DARK_GRAY, (0, 0, GAME_AREA_WIDTH, SCREEN_HEIGHT))
            
            draw_grid_lines(screen)
            draw_grid(screen, game.grid)
            
            # 現在のテトリミノを描画
            draw_piece(screen, game.current_piece)
                
            draw_hold_piece(screen, game.hold_piece)
            draw_next_pieces(screen, game.next_pieces)
            draw_score_area(screen, game.score, game.initial_blocks_count)
            draw_controls(screen)
        
        elif game_state == GAME_STATE_GAMEOVER or game_state == GAME_STATE_WIN:
            # ゲームオーバー/勝利画面
            retry_button, quit_button = draw_game_over_screen(
                screen, font, large_font, game.score, game_state == GAME_STATE_WIN
            )
            
            retry_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            if retry_button.is_clicked(mouse_pos, mouse_click):
                game_state = GAME_STATE_PLAYING
                game.reset_game()
                fall_time = 0
            
            if quit_button.is_clicked(mouse_pos, mouse_click):
                running = False
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
