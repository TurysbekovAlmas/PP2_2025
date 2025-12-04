import os
import sys

os.environ['PGCLIENTENCODING'] = 'UTF8'

import pygame
import random
import psycopg2
from datetime import datetime
import json


pygame.init()


WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

class SnakeGameDB:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        """Initialize database connection"""
        try:
            os.environ['PGHOST'] = host
            os.environ['PGPORT'] = str(port)
            os.environ['PGDATABASE'] = dbname
            os.environ['PGUSER'] = user
            os.environ['PGPASSWORD'] = password
            os.environ['PGCLIENTENCODING'] = 'UTF8'
            
            self.conn = psycopg2.connect('')
            
            self.conn.set_client_encoding('UTF8')
            self.cursor = self.conn.cursor()
            self.cursor.execute("SET client_encoding TO 'UTF8';")
            self.conn.commit()
            
            print("Database connection established")
            
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    # ... остальные методы класса без изменений ...

    def create_tables(self):
        """Create user and user_score tables"""
        create_user_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_score_table = """
        CREATE TABLE IF NOT EXISTS user_scores (
            score_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            level INTEGER DEFAULT 1,
            score INTEGER DEFAULT 0,
            high_score INTEGER DEFAULT 0,
            game_state TEXT,
            last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.cursor.execute(create_user_table)
            self.cursor.execute(create_score_table)
            self.conn.commit()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()

    def get_or_create_user(self, username):
        """Get existing user or create new one"""
        try:
            # Check if user exists
            select_query = "SELECT user_id FROM users WHERE username = %s;"
            self.cursor.execute(select_query, (username,))
            result = self.cursor.fetchone()
            
            if result:
                user_id = result[0]
                print(f"Welcome back, {username}!")
            else:
                # Create new user
                insert_query = """
                INSERT INTO users (username) VALUES (%s) RETURNING user_id;
                """
                self.cursor.execute(insert_query, (username,))
                user_id = self.cursor.fetchone()[0]
                
                # Create initial score record
                score_query = """
                INSERT INTO user_scores (user_id, level, score, high_score)
                VALUES (%s, 1, 0, 0);
                """
                self.cursor.execute(score_query, (user_id,))
                self.conn.commit()
                print(f"New user created: {username}")
            
            return user_id
        except Exception as e:
            print(f"Error getting/creating user: {e}")
            self.conn.rollback()
            return None

    def get_user_stats(self, user_id):
        """Get user's current level and high score"""
        try:
            query = """
            SELECT level, high_score, game_state 
            FROM user_scores WHERE user_id = %s;
            """
            self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'level': result[0],
                    'high_score': result[1],
                    'game_state': result[2]
                }
            return {'level': 1, 'high_score': 0, 'game_state': None}
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {'level': 1, 'high_score': 0, 'game_state': None}

    def save_game_state(self, user_id, level, score, game_state):
        """Save current game state"""
        try:
            update_query = """
            UPDATE user_scores 
            SET level = %s, score = %s, game_state = %s, last_played = %s
            WHERE user_id = %s;
            """
            self.cursor.execute(update_query, 
                              (level, score, json.dumps(game_state), 
                               datetime.now(), user_id))
            self.conn.commit()
            print("Game state saved successfully")
        except Exception as e:
            print(f"Error saving game state: {e}")
            self.conn.rollback()

    def update_high_score(self, user_id, score):
        """Update high score if current score is higher"""
        try:
            query = """
            UPDATE user_scores 
            SET high_score = GREATEST(high_score, %s)
            WHERE user_id = %s;
            """
            self.cursor.execute(query, (score, user_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating high score: {e}")
            self.conn.rollback()

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        self.speed = 8 + (level_num - 1) * 2  # Increase speed with level
        self.walls = self.generate_walls()
    
    def generate_walls(self):
        """Generate walls based on level"""
        walls = []
        
        if self.level_num == 1:
            # No walls
            pass
        
        elif self.level_num == 2:
            # Border walls
            for x in range(GRID_WIDTH):
                walls.append((x, 0))
                walls.append((x, GRID_HEIGHT - 1))
            for y in range(GRID_HEIGHT):
                walls.append((0, y))
                walls.append((GRID_WIDTH - 1, y))
        
        elif self.level_num == 3:
            # Cross pattern
            mid_x = GRID_WIDTH // 2
            mid_y = GRID_HEIGHT // 2
            for i in range(5, GRID_WIDTH - 5):
                walls.append((i, mid_y))
            for i in range(5, GRID_HEIGHT - 5):
                walls.append((mid_x, i))
        
        elif self.level_num >= 4:
            # Random obstacles
            num_walls = 20 + (self.level_num - 4) * 5
            for _ in range(num_walls):
                x = random.randint(2, GRID_WIDTH - 3)
                y = random.randint(2, GRID_HEIGHT - 3)
                if (x, y) not in walls:
                    walls.append((x, y))
        
        return walls


class SnakeGame:
    def __init__(self, db, user_id, username):
        self.db = db
        self.user_id = user_id
        self.username = username
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Snake Game - {username}")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Get user stats
        stats = db.get_user_stats(user_id)
        self.current_level = stats['level']
        self.high_score = stats['high_score']
        
        # Load saved game state if available
        if stats['game_state']:
            try:
                saved_state = json.loads(stats['game_state'])
                self.load_game_state(saved_state)
            except:
                self.init_game()
        else:
            self.init_game()
        
        self.paused = False

    def init_game(self):
        """Initialize new game"""
        self.level = Level(self.current_level)
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        """Generate food at random position"""
        while True:
            food = (random.randint(0, GRID_WIDTH - 1),
                   random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake and food not in self.level.walls:
                return food

    def move_snake(self):
        """Move snake in current direction"""
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check collision with walls
        if new_head in self.level.walls:
            self.game_over = True
            return
        
        # Check collision with boundaries (level 1 only wraps)
        if self.current_level == 1:
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        else:
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                self.game_over = True
                return
        
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            
            # Level up every 50 points
            if self.score % 50 == 0:
                self.current_level += 1
                self.level = Level(self.current_level)
                self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                self.direction = (1, 0)
                self.next_direction = (1, 0)
        else:
            self.snake.pop()

    def draw(self):
        """Draw game elements"""
        self.screen.fill(BLACK)
        
        # Draw walls
        for wall in self.level.walls:
            rect = pygame.Rect(wall[0] * GRID_SIZE, wall[1] * GRID_SIZE,
                             GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, GRAY, rect)
        
        # Draw snake
        for segment in self.snake:
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                             GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(self.screen, GREEN, rect)
        
        # Draw food
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE,
                               GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(self.screen, RED, food_rect)
        
        # Draw score and level
        score_text = self.small_font.render(
            f"Score: {self.score} | Level: {self.current_level} | High: {self.high_score}",
            True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw pause message
        if self.paused:
            pause_text = self.font.render("PAUSED", True, WHITE)
            rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(pause_text, rect)
            
            help_text = self.small_font.render("Press P to resume, S to save & quit", 
                                              True, WHITE)
            rect2 = help_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            self.screen.blit(help_text, rect2)
        
        # Draw game over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(game_over_text, rect)
            
            restart_text = self.small_font.render("Press R to restart, Q to quit",
                                                  True, WHITE)
            rect2 = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            self.screen.blit(restart_text, rect2)
        
        pygame.display.flip()

    def get_game_state(self):
        """Get current game state for saving"""
        return {
            'snake': self.snake,
            'direction': self.direction,
            'food': self.food,
            'score': self.score,
            'level': self.current_level
        }

    def load_game_state(self, state):
        """Load saved game state"""
        try:
            self.current_level = state.get('level', 1)
            self.level = Level(self.current_level)
            self.snake = [tuple(pos) for pos in state.get('snake', [(GRID_WIDTH // 2, GRID_HEIGHT // 2)])]
            self.direction = tuple(state.get('direction', [1, 0]))
            self.next_direction = self.direction
            self.food = tuple(state.get('food', self.generate_food()))
            self.score = state.get('score', 0)
            self.game_over = False
        except:
            self.init_game()

    def save_and_quit(self):
        """Save game state and quit"""
        game_state = self.get_game_state()
        self.db.save_game_state(self.user_id, self.current_level, 
                               self.score, game_state)
        self.db.update_high_score(self.user_id, self.score)
        return True

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_and_quit()
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    
                    elif event.key == pygame.K_s and self.paused:
                        if self.save_and_quit():
                            print("Game saved successfully!")
                            running = False
                    
                    elif self.game_over:
                        if event.key == pygame.K_r:
                            self.init_game()
                        elif event.key == pygame.K_q:
                            self.db.update_high_score(self.user_id, self.score)
                            running = False
                    
                    elif not self.paused:
                        if event.key == pygame.K_UP and self.direction != (0, 1):
                            self.next_direction = (0, -1)
                        elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                            self.next_direction = (0, 1)
                        elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                            self.next_direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                            self.next_direction = (1, 0)
            
            if not self.paused and not self.game_over:
                self.move_snake()
            
            self.draw()
            self.clock.tick(self.level.speed)
        
        return True


def main():
    # Initialize database
    db = SnakeGameDB(
        dbname='snake_game_db',
        user='postgres',
        password='your_password',
        host='localhost'
    )
    
    # Create tables
    db.create_tables()
    
    # Get username
    username = input("Enter your username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    user_id = db.get_or_create_user(username)
    if not user_id:
        print("Failed to create/get user")
        return
    
    # Show user stats
    stats = db.get_user_stats(user_id)
    print(f"\nCurrent Level: {stats['level']}")
    print(f"High Score: {stats['high_score']}")
    if stats['game_state']:
        print("Saved game found! It will be loaded.")
    print("\nControls:")
    print("- Arrow keys: Move")
    print("- P: Pause/Resume")
    print("- S (while paused): Save and quit")
    print("\nPress any key to start...")
    input()
    
    # Start game
    game = SnakeGame(db, user_id, username)
    game.run()
    
    # Close database
    db.close()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()