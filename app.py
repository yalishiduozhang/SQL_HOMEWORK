from flask import Flask, jsonify, request, render_template, redirect, session, url_for, flash
import os
import math
from collections import defaultdict
import mysql.connector
from mysql.connector import Error
import getpass
import hashlib
from datetime import datetime
import secrets
import decimal
from PIL import Image

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = secrets.token_hex(16)  # 生成随机密钥用于session
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 限制上传文件大小为5MB

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class DatabaseManager:
    _instance = None
    _password = None
    
    @staticmethod
    def get_instance():
        if DatabaseManager._instance is None:
            DatabaseManager._instance = DatabaseManager()
        return DatabaseManager._instance
    
    def __init__(self):
        self.connection = None
        self.pool = None
        self.connect()
    
    def connect(self):
        try:
            # 检查是否在 Docker 环境中
            if os.getenv('MYSQL_HOST'):
                # Docker 环境，使用环境变量
                host = os.getenv('MYSQL_HOST', 'mysql')
                port = int(os.getenv('MYSQL_PORT', '3306'))
                user = os.getenv('MYSQL_USER', 'moviehunter_user')
                password = os.getenv('MYSQL_PASSWORD', 'moviehunter_password')
                database = os.getenv('MYSQL_DATABASE', 'moviehunter')
                print(f"使用 Docker 环境连接到数据库: {host}:{port}")
            else:
                # 本地环境，使用交互式密码输入
                if DatabaseManager._password is None:
                    DatabaseManager._password = getpass.getpass("请输入数据库密码：")
                host = 'localhost'
                port = 3306
                user = 'root'
                password = DatabaseManager._password
                database = 'moviehunter'
                print("使用本地环境连接到数据库")
            
            # 创建连接池
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="moviehunter",
                pool_size=5,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            
            # 测试连接
            connection = self.pool.get_connection()
            if connection.is_connected():
                print("成功连接到MySQL数据库")
                connection.close()
                
        except Error as e:
            print(f"连接MySQL数据库时出错: {e}")
            self.pool = None
            DatabaseManager._password = None
            self.connect()
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("已断开与MySQL数据库的连接")
    
    def execute_query(self, query, params=None):
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            for row in result:
                for key, value in row.items():
                    if isinstance(value, decimal.Decimal):
                        row[key] = float(value)
            return result
        except Error as e:
            print(f"执行查询时出错: {e}")
            try:
                if 'connection' in locals() and connection and connection.is_connected():
                    connection.close()
            except:
                pass
            if self.pool is None:
                self.connect()
            return []
    
    def execute_update(self, query, params=None):
        try:
            connection = self.pool.get_connection()
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            affected_rows = cursor.rowcount
            last_insert_id = cursor.lastrowid
            cursor.close()
            connection.close()
            return True, last_insert_id
        except Error as e:
            print(f"执行更新时出错: {e}")
            return False, None
    
    def get_all_movies(self):
        query = "SELECT * FROM movies"
        return self.execute_query(query)
    
    def get_movie_by_id(self, movie_id):
        query = "SELECT * FROM movies WHERE id = %s"
        result = self.execute_query(query, (movie_id,))
        return result[0] if result else None
    
    def get_movies_by_genre(self, genre, limit=10, order_by='rating'):
        query = f"SELECT * FROM movies WHERE genre LIKE %s ORDER BY {order_by} DESC LIMIT %s"
        return self.execute_query(query, (f"%{genre}%", limit))
    
    def get_latest_movies(self, limit=16):
        query = "SELECT * FROM movies ORDER BY year DESC LIMIT %s"
        return self.execute_query(query, (limit,))
    
    def get_top_rated_movies(self, limit=16):
        query = "SELECT * FROM movies WHERE rating > 0 ORDER BY rating DESC LIMIT %s"
        return self.execute_query(query, (limit,))
    
    def get_most_commented_movies(self, limit=16):
        query = """
        SELECT m.*, COUNT(r.id) as comment_count 
        FROM movies m
        JOIN ratings r ON m.id = r.movie_id
        GROUP BY m.id
        ORDER BY comment_count DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def search_movies(self, keyword, limit=16):
        query = """
        SELECT * FROM movies 
        WHERE title LIKE %s OR genre LIKE %s 
        ORDER BY rating DESC 
        LIMIT %s
        """
        keyword_param = f"%{keyword}%"
        return self.execute_query(query, (keyword_param, keyword_param, limit))
    
    def get_all_users(self):
        query = "SELECT * FROM users"
        return self.execute_query(query)
    
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (username,))
        return result[0] if result else None
    
    def check_user_rating(self, user_id, movie_id):
        query = "SELECT * FROM ratings WHERE user_id = %s AND movie_id = %s"
        result = self.execute_query(query, (user_id, movie_id))
        return result[0] if result else None
    
    def update_rating(self, user_id, movie_id, rating, comment):
        # 确保评分是0.5的倍数
        rating = round(rating * 2) / 2
        query = """
        UPDATE ratings 
        SET rating = %s, comment = %s, timestamp = %s 
        WHERE user_id = %s AND movie_id = %s
        """
        timestamp = int(datetime.now().timestamp())
        success, _ = self.execute_update(query, (rating, comment, timestamp, user_id, movie_id))
        
        if success:
            # 更新电影的平均评分
            self.update_movie_rating(movie_id)
            
        return success
    
    def get_ratings_by_movie_id(self, movie_id, limit=10, offset=0):
        query = """
        SELECT r.*, u.username 
        FROM ratings r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.movie_id = %s
        ORDER BY r.timestamp DESC
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (movie_id, limit, offset))
    
    def _calculate_score_range(self, score):
        """计算评分范围"""
        score = float(score)
        decimal_part = score - int(score)
        if decimal_part == 0:  # 整数评分
            lower_bound = score - 0.25
            upper_bound = score + 0.25
        elif abs(decimal_part - 0.5) < 0.01:  # x.5评分
            lower_bound = int(score) + 0.25
            upper_bound = int(score) + 0.75
        else:  # 其他小数评分，使用±0.25
            lower_bound = score - 0.25
            upper_bound = score + 0.25
        return lower_bound, upper_bound
    
    def _map_score_to_db_score(self, score):
        """将用户界面上的评分映射到数据库中的评分"""
        score = float(score)
        decimal_part = score - int(score)
        
        if decimal_part == 0:  # 整数评分
            return score
        elif abs(decimal_part - 0.5) < 0.01:  # x.5评分
            return int(score)  # 向下取整
        else:  # 其他小数评分
            return round(score)  # 四舍五入
    
    def get_ratings_by_score(self, movie_id, score, limit=10, offset=0):
        """获取特定电影特定评分的所有用户评价"""
        score = float(score)
        
        # 设置匹配区间
        lower_bound = score - 0.5
        upper_bound = score + 0.5
        
        query = """
        SELECT r.*, u.username, ABS(r.rating - %s) as rating_diff
        FROM ratings r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.movie_id = %s AND r.rating BETWEEN %s AND %s
        ORDER BY rating_diff, r.timestamp DESC
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (score, movie_id, lower_bound, upper_bound, limit, offset))
    
    def get_ratings_count_by_movie_id(self, movie_id):
        query = """
        SELECT COUNT(*) as count
        FROM ratings
        WHERE movie_id = %s
        """
        result = self.execute_query(query, (movie_id,))
        return result[0]['count'] if result else 0
    
    def get_ratings_count_by_score(self, movie_id, score):
        """获取特定电影特定评分的评价总数"""
        score = float(score)
        
        # 设置匹配区间
        lower_bound = score - 0.5
        upper_bound = score + 0.5
        
        query = """
        SELECT COUNT(*) as count
        FROM ratings
        WHERE movie_id = %s AND rating BETWEEN %s AND %s
        """
        result = self.execute_query(query, (movie_id, lower_bound, upper_bound))
        return result[0]['count'] if result else 0
    
    def get_diverse_ratings_by_movie_id(self, movie_id, limit=10):
        """获取一个电影的多样化评分，包括高分和低分"""
        query = """
        (SELECT r.*, u.username 
        FROM ratings r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.movie_id = %s AND r.rating = 5
        ORDER BY r.timestamp DESC
        LIMIT 5)
        UNION
        (SELECT r.*, u.username 
        FROM ratings r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.movie_id = %s AND r.rating < 5
        ORDER BY r.rating DESC, r.timestamp DESC
        LIMIT 5)
        """
        return self.execute_query(query, (movie_id, movie_id))
    
    def get_ratings_by_user_id(self, user_id):
        query = """
        SELECT r.*, m.title , r.timestamp
        FROM ratings r 
        JOIN movies m ON r.movie_id = m.id 
        WHERE r.user_id = %s
        """
        return self.execute_query(query, (user_id,))
    
    def get_all_ratings(self):
        query = """
        SELECT r.*, m.title 
        FROM ratings r 
        JOIN movies m ON r.movie_id = m.id
        """
        return self.execute_query(query)   
    
    def add_movie(self, title, year, genre, rating=0, description=''):
        query = """
        INSERT INTO movies (title, year, genre, rating, description) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (title, year, genre, rating, description))
    
    def add_user(self, username, password, email):
        # 对密码进行MD5加密
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        return self.execute_update(query, (username, hashed_password, email))
    
    def add_rating(self, user_id, movie_id, rating, comment=''):
        # 确保评分是0.5的倍数
        rating = round(rating * 2) / 2
        timestamp = int(datetime.now().timestamp())
        query = "INSERT INTO ratings (user_id, movie_id, rating, comment, timestamp) VALUES (%s, %s, %s, %s, %s)"
        success, _ = self.execute_update(query, (user_id, movie_id, rating, comment, timestamp))
        
        if success:
            # 更新电影的平均评分
            self.update_movie_rating(movie_id)
        
        return success
    
    def update_movie_rating(self, movie_id):
        """更新电影的平均评分"""
        query = """
        UPDATE movies m
        SET rating = (
            SELECT AVG(rating)
            FROM ratings r
            WHERE r.movie_id = m.id
        )
        WHERE m.id = %s
        """
        return self.execute_update(query, (movie_id,))

    def get_rating_distribution(self, movie_id):
        """获取电影的评分分布"""
        query = """
        SELECT 
            CASE 
                WHEN rating = 0.5 THEN '0.5'
                WHEN rating = 1 THEN '1'
                WHEN rating = 1.5 THEN '1.5'
                WHEN rating = 2 THEN '2'
                WHEN rating = 2.5 THEN '2.5'
                WHEN rating = 3 THEN '3'
                WHEN rating = 3.5 THEN '3.5'
                WHEN rating = 4 THEN '4'
                WHEN rating = 4.5 THEN '4.5'
                WHEN rating = 5 THEN '5'
                ELSE CAST(rating AS CHAR)
            END as rating_level,
            COUNT(*) as count
        FROM ratings
        WHERE movie_id = %s
        GROUP BY rating
        ORDER BY rating DESC
        """
        results = self.execute_query(query, (movie_id,))
        
        # 初始化所有评分级别
        distribution = {
            '5': 0, '4.5': 0, '4': 0, '3.5': 0, '3': 0,
            '2.5': 0, '2': 0, '1.5': 0, '1': 0, '0.5': 0
        }
        
        # 填充实际数据
        for row in results:
            rating_level = row['rating_level']
            if rating_level in distribution:
                distribution[rating_level] = row['count']
        
        return distribution
    
    def get_user_embedding(self, user_id):
        query = "SELECT embedding FROM user_embeddings WHERE user_id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0]['embedding'] if result else None
    
    def get_all_movie_embeddings(self):
        try:
            query = "SELECT movie_id, embedding FROM movie_embeddings"
            return self.execute_query(query)
        except Exception as e:
            print(f"获取电影嵌入向量时出错: {e}")
            return []
    
    def get_all_user_embeddings(self):
        try:
            query = "SELECT user_id, embedding FROM user_embeddings"
            return self.execute_query(query)
        except Exception as e:
            print(f"获取用户嵌入向量时出错: {e}")
            return []

class DataManager:
    _instance = None
    
    @staticmethod
    def get_instance():
        if DataManager._instance is None:
            DataManager._instance = DataManager()
        return DataManager._instance
    
    def __init__(self):
        self.movie_map = {}
        self.user_map = {}
        self.genre_reverse_index_map = defaultdict(list)
        self.db_manager = DatabaseManager.get_instance()
        self.load_data_from_db()
    
    def load_data_from_db(self):
        print("正在从数据库加载数据...")
        self.load_movies_from_db()
        self.load_users_from_db()
        self.load_movie_emb_from_db()
        self.load_user_emb_from_db()
        print("数据加载完成")
    
    def load_movies_from_db(self):
        print("从数据库加载电影数据...")
        movies = self.db_manager.get_all_movies()
        for movie_data in movies:
            movie = Movie()
            movie.movie_id = movie_data['id']
            movie.title = movie_data['title']
            movie.release_year = movie_data['year']
            movie.director = movie_data['director']
            movie.genre = movie_data['genre']
            movie.genres = []
            if movie_data['genre']:
                movie.genres = [g.strip() for g in movie_data['genre'].split(',')]
            movie.rating = float(movie_data['rating']) if movie_data['rating'] else 0.0
            movie.average_rating = movie.rating
            movie.poster_url = movie_data['poster_url']
            movie.description = movie_data['description']
            
            self.movie_map[movie.movie_id] = movie
            
            if movie.genre:
                genres = movie.genre.split(',')
                for genre in genres:
                    genre = genre.strip()
                    self.add_movie_to_genre_index(genre, movie)
    
    def load_users_from_db(self):
        print("从数据库加载用户数据...")
        users = self.db_manager.get_all_users()

        all_ratings = self.db_manager.get_all_ratings()
        ratings_by_user = {}
        for rating in all_ratings:
            user_id = rating['user_id']
            if user_id not in ratings_by_user:
                ratings_by_user[user_id] = []
            ratings_by_user[user_id].append(rating)
        for user_data in users:
            user = User()
            user.user_id = user_data['id']
            user.username = user_data['username']
            user.email = user_data['email']
            
            self.user_map[user.user_id] = user
            
            user_ratings = ratings_by_user.get(user.user_id, [])
            for rating_data in user_ratings:
                rating = Rating()
                rating.user_id = rating_data['user_id']
                rating.movie_id = rating_data['movie_id']
                rating.score = float(rating_data['rating']) if rating_data['rating'] else 0.0
                rating.comment = rating_data['comment']
                rating.title = rating_data['title']
                rating.timestamp = rating_data['timestamp']
                
                user.add_rating(rating)
                
                if rating.movie_id in self.movie_map:
                    movie = self.movie_map[rating.movie_id]
                    movie.add_rating(rating)
    
    def load_movie_emb_from_db(self):
        print("从数据库加载电影嵌入向量...")
        try:
            movie_embeddings = self.db_manager.get_all_movie_embeddings()
            valid_emb_count = 0
            
            for emb_data in movie_embeddings:
                movie_id = emb_data['movie_id']
                movie = self.get_movie_by_id(movie_id)
                if movie:
                    emb_str = emb_data['embedding']
                    movie.emb = Embedding(self.parse_emb_str(emb_str))
                    valid_emb_count += 1
            
            print(f"电影嵌入向量加载完成，共 {valid_emb_count} 个嵌入向量")
        except Exception as e:
            print(f"加载电影嵌入向量时出错: {e}")
            print("将跳过电影嵌入向量加载")
    
    def load_user_emb_from_db(self):
        print("从数据库加载用户嵌入向量...")
        try:
            user_embeddings = self.db_manager.get_all_user_embeddings()
            valid_emb_count = 0
            
            for emb_data in user_embeddings:
                user_id = emb_data['user_id']
                user = self.get_user_by_id(user_id)
                if user:
                    emb_str = emb_data['embedding']
                    user.emb = Embedding(self.parse_emb_str(emb_str))
                    valid_emb_count += 1
            
            print(f"用户嵌入向量加载完成，共 {valid_emb_count} 个嵌入向量")
        except Exception as e:
            print(f"加载用户嵌入向量时出错: {e}")
            print("将跳过用户嵌入向量加载")
    
    def parse_release_year(self, raw_title):
        if not raw_title or len(raw_title.strip()) < 6:
            return -1
        
        try:
            year_string = raw_title.strip()[-5:-1]
            return int(year_string)
        except (ValueError, IndexError):
            return -1
    
    def add_movie_to_genre_index(self, genre, movie):
        if genre not in self.genre_reverse_index_map:
            self.genre_reverse_index_map[genre] = []
        self.genre_reverse_index_map[genre].append(movie)
    
    def get_movies_by_genre(self, genre, size, sort_by):
        if genre not in self.genre_reverse_index_map:
            return []
        
        movies = self.genre_reverse_index_map[genre].copy()
        
        if sort_by == "rating":
            movies.sort(key=lambda x: x.average_rating, reverse=True)
        elif sort_by == "year":
            movies.sort(key=lambda x: x.release_year, reverse=True)
        
        return movies[:size] if size < len(movies) else movies
    
    def get_movies(self, size, sort_by):
        movies = list(self.movie_map.values())
        
        if sort_by == "rating":
            movies.sort(key=lambda x: x.average_rating, reverse=True)
        elif sort_by == "year":
            movies.sort(key=lambda x: x.release_year, reverse=True)
        
        return movies[:size] if size < len(movies) else movies
    
    def get_movie_by_id(self, movie_id):
        return self.movie_map.get(movie_id)
    
    def get_user_by_id(self, user_id):
        return self.user_map.get(user_id)
    
    def parse_emb_str(self, emb_str):
        result = []
        for val in emb_str.split(','):
            try:
                result.append(float(val))
            except ValueError:
                continue
        return result
    
    def refresh_data(self):
        """刷新数据（用于添加新电影后）"""
        self.movie_map.clear()
        self.user_map.clear()
        self.genre_reverse_index_map.clear()
        self.load_data_from_db()

class Movie:
    def __init__(self):
        self.movie_id = 0
        self.title = ""
        self.release_year = 0
        self.imdb_id = ""
        self.tmdb_id = ""
        self.genres = []
        self.rating_number = 0
        self.average_rating = 0.0
        self.emb = None
        self.ratings = []
        self.top_ratings = []
        self.TOP_RATING_SIZE = 10
    
    def add_rating(self, rating):
        self.average_rating = (self.average_rating * self.rating_number + rating.score) / (self.rating_number + 1)
        self.rating_number += 1
        self.ratings.append(rating)
        self.add_top_rating(rating)
    
    def add_top_rating(self, rating):
        if not self.top_ratings:
            self.top_ratings.append(rating)
        else:
            index = 0
            for top_rating in self.top_ratings:
                if top_rating.score >= rating.score:
                    break
                index += 1
            
            self.top_ratings.insert(index, rating)
            if len(self.top_ratings) > self.TOP_RATING_SIZE:
                self.top_ratings.pop(0)
    
    def to_dict(self):
        return {
            'movieId': self.movie_id,
            'title': self.title,
            'releaseYear': self.release_year,
            'imdbId': self.imdb_id,
            'tmdbId': self.tmdb_id,
            'genres': self.genres,
            'ratingNumber': self.rating_number,
            'averageRating': self.average_rating,
            'topRatings': [rating.to_dict() for rating in self.top_ratings]
        }

class User:
    def __init__(self):
        self.user_id = 0
        self.average_rating = 0.0
        self.highest_rating = 0.0
        self.lowest_rating = 5.0
        self.rating_count = 0
        self.ratings = []
        self.emb = None
    
    def add_rating(self, rating):
        self.ratings.append(rating)
        self.average_rating = (self.average_rating * self.rating_count + rating.score) / (self.rating_count + 1)
        
        if rating.score > self.highest_rating:
            self.highest_rating = rating.score
        
        if rating.score < self.lowest_rating:
            self.lowest_rating = rating.score
        
        self.rating_count += 1
    
    def to_dict(self):
        return {
            'userId': self.user_id,
            'averageRating': self.average_rating,
            'highestRating': self.highest_rating,
            'lowestRating': self.lowest_rating,
            'ratingCount': self.rating_count,
            'ratings': [rating.to_dict() for rating in self.ratings]
        }

class Rating:
    def __init__(self):
        self.movie_id = 0
        self.user_id = 0
        self.score = 0.0
        self.timestamp = 0
        self.title = ""
    
    def to_dict(self):
        return {
            'movieId': self.movie_id,
            'userId': self.user_id,
            'score': self.score,
            'timestamp': self.timestamp,
            'title': self.title
        }

class Embedding:
    def __init__(self, emb_vector=None):
        self.emb_vector = emb_vector if emb_vector else []
    
    def add_dim(self, element):
        self.emb_vector.append(element)
    
    def calculate_similarity(self, other_emb):
        if not self.emb_vector or not other_emb or not other_emb.emb_vector or len(self.emb_vector) != len(other_emb.emb_vector):
            return -1
        
        dot_product = 0
        denominator1 = 0
        denominator2 = 0
        
        for i in range(len(self.emb_vector)):
            dot_product += self.emb_vector[i] * other_emb.emb_vector[i]
            denominator1 += self.emb_vector[i] * self.emb_vector[i]
            denominator2 += other_emb.emb_vector[i] * other_emb.emb_vector[i]
        
        return dot_product / (math.sqrt(denominator1) * math.sqrt(denominator2))

class SimilarMovieProcess:
    @staticmethod
    def get_rec_list(movie_id, size, model):
        movie = DataManager.get_instance().get_movie_by_id(movie_id)
        if not movie:
            return []
        
        candidates = SimilarMovieProcess.candidate_generator(movie)
        ranked_list = SimilarMovieProcess.ranker(movie, candidates, model)
        
        return ranked_list[:size] if size < len(ranked_list) else ranked_list
    
    @staticmethod
    def candidate_generator(movie):
        candidate_map = {}
        for genre in movie.genres:
            candidates = DataManager.get_instance().get_movies_by_genre(genre, 100, "rating")
            for candidate in candidates:
                candidate_map[candidate.movie_id] = candidate
        
        if movie.movie_id in candidate_map:
            del candidate_map[movie.movie_id]
        
        return list(candidate_map.values())
    
    @staticmethod
    def ranker(movie, candidates, model):
        candidate_score_map = {}
        for candidate in candidates:
            similarity = 0
            if model == "emb":
                similarity = SimilarMovieProcess.calculate_emb_similar_score(movie, candidate)
            else:
                similarity = SimilarMovieProcess.calculate_similar_score(movie, candidate)
            
            candidate_score_map[candidate.movie_id] = similarity
        
        sorted_candidates = sorted(candidates, key=lambda x: candidate_score_map.get(x.movie_id, 0), reverse=True)
        return sorted_candidates
    
    @staticmethod
    def calculate_similar_score(movie, candidate):
        same_genre_count = 0
        for genre in movie.genres:
            if genre in candidate.genres:
                same_genre_count += 1
        
        genre_similarity = same_genre_count / (len(movie.genres) + len(candidate.genres)) / 2
        rating_score = candidate.average_rating / 5
        
        similarity_weight = 0.7
        rating_score_weight = 0.3
        
        return genre_similarity * similarity_weight + rating_score * rating_score_weight
    
    @staticmethod
    def calculate_emb_similar_score(movie, candidate):
        if not movie or not candidate or not movie.emb or not candidate.emb:
            return -1
        
        return movie.emb.calculate_similarity(candidate.emb)

# 登录注册相关路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
        
        db = DatabaseManager.get_instance()
        user = db.get_user_by_username(username)
        
        if user:
            # 验证密码
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            if user['password'] == hashed_password:
                session['user_id'] = user['id']
                session['username'] = user['username']
                return jsonify({'success': True, 'message': '登录成功'})
            else:
                return jsonify({'success': False, 'message': '密码错误'})
        else:
            return jsonify({'success': False, 'message': '用户不存在'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        if not username or not password or not email:
            return jsonify({'success': False, 'message': '所有字段都必须填写'})
        
        db = DatabaseManager.get_instance()
        
        # 检查用户名是否已存在
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        # 添加新用户
        success, user_id = db.add_user(username, password, email)
        if success:
            # 刷新数据
            DataManager.get_instance().refresh_data()
            return jsonify({'success': True, 'message': '注册成功，请登录'})
        else:
            return jsonify({'success': False, 'message': '注册失败，请重试'})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        genre = request.form.get('genre')
        description = request.form.get('description', '')
        
        if not title or not year or not genre:
            return jsonify({'success': False, 'message': '电影名称、年份和类型为必填项'})
        
        try:
            year = int(year)
        except ValueError:
            return jsonify({'success': False, 'message': '年份必须是数字'})
        
        # 验证类型是否合法
        ALLOWED_GENRES = {
            'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 
            'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 
            'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 
            'Thriller', 'War', 'Western'
        }
        
        # 分割并验证每个类型
        genres = [g.strip() for g in genre.split(',')]
        invalid_genres = [g for g in genres if g not in ALLOWED_GENRES]
        
        if invalid_genres:
            return jsonify({
                'success': False, 
                'message': f'不支持的电影类型: {", ".join(invalid_genres)}'
            })
        
        # 重新组合类型字符串
        genre = ','.join(genres)
        
        db = DatabaseManager.get_instance()
        success, movie_id = db.add_movie(title, year, genre, 0, description)
        
        if success:
            # 处理图片上传
            if 'poster' in request.files:
                file = request.files['poster']
                if file and allowed_file(file.filename):
                    try:
                        # 创建posters目录（如果不存在）
                        posters_dir = os.path.join(app.static_folder, 'posters')
                        if not os.path.exists(posters_dir):
                            os.makedirs(posters_dir)
                        
                        # 保存并处理图片
                        filename = f"{movie_id}.jpg"
                        filepath = os.path.join(posters_dir, filename)
                        
                        # 使用PIL处理图片
                        img = Image.open(file.stream)
                        
                        # 转换为RGB（如果是PNG或其他格式）
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # 调整大小（保持纵横比，宽度最大300px）
                        max_width = 300
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        
                        # 保存为JPEG
                        img.save(filepath, 'JPEG', quality=85, optimize=True)
                        
                    except Exception as e:
                        print(f"保存图片时出错: {e}")
                        # 图片保存失败不影响电影添加
            
            # 刷新数据
            DataManager.get_instance().refresh_data()
            return jsonify({'success': True, 'message': '电影添加成功', 'movieId': movie_id})
        else:
            return jsonify({'success': False, 'message': '添加失败，请重试'})
    
    return render_template('add_movie.html')

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    data = request.get_json()
    movie_id = data.get('movieId')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not movie_id or not rating:
        return jsonify({'success': False, 'message': '电影ID和评分不能为空'})
    
    try:
        movie_id = int(movie_id)
        rating = float(rating)
        # 确保评分在0.5-5.0之间，且是0.5的倍数
        if rating < 0.5 or rating > 5:
            return jsonify({'success': False, 'message': '评分必须在0.5-5之间'})
        if (rating * 2) % 1 != 0:  # 检查是否是0.5的倍数
            return jsonify({'success': False, 'message': '评分必须是0.5的倍数'})
    except ValueError:
        return jsonify({'success': False, 'message': '无效的数据格式'})
    
    user_id = session['user_id']
    db = DatabaseManager.get_instance()
    
    # 检查是否已经评分
    existing_rating = db.check_user_rating(user_id, movie_id)
    
    if existing_rating:
        # 更新评分
        success = db.update_rating(user_id, movie_id, rating, comment)
        message = '评分更新成功' if success else '更新失败，请重试'
    else:
        # 添加新评分
        success = db.add_rating(user_id, movie_id, rating, comment)
        message = '评分成功' if success else '评分失败，请重试'
    
    if success:
        # 刷新数据
        DataManager.get_instance().refresh_data()
    
    return jsonify({'success': success, 'message': message})

@app.route('/get_user_rating')
def get_user_rating():
    if 'user_id' not in session:
        return jsonify({'hasRated': False})
    
    movie_id = request.args.get('movieId')
    if not movie_id:
        return jsonify({'hasRated': False})
    
    try:
        movie_id = int(movie_id)
    except ValueError:
        return jsonify({'hasRated': False})
    
    user_id = session['user_id']
    db = DatabaseManager.get_instance()
    
    rating = db.check_user_rating(user_id, movie_id)
    if rating:
        return jsonify({
            'hasRated': True,
            'rating': rating['rating'],
            'comment': rating.get('comment', '')
        })
    else:
        return jsonify({'hasRated': False})

@app.route('/get_session_info')
def get_session_info():
    if 'user_id' in session:
        return jsonify({
            'loggedIn': True,
            'userId': session['user_id'],
            'username': session['username']
        })
    else:
        return jsonify({'loggedIn': False})

# 原有路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getmovie')
def get_movie():
    try:
        movie_id = int(request.args.get('id'))
        movie = DataManager.get_instance().get_movie_by_id(movie_id)
        if movie:
            # 尝试获取多样化的评分
            db = DatabaseManager.get_instance()
            diverse_ratings = db.get_diverse_ratings_by_movie_id(movie_id)
            if diverse_ratings:
                # 将多样化评分转换为Rating对象并添加到movie对象
                movie.top_ratings = []
                for rating_data in diverse_ratings:
                    rating = Rating()
                    rating.user_id = rating_data['user_id']
                    rating.movie_id = rating_data['movie_id']
                    rating.score = rating_data['rating']
                    rating.timestamp = rating_data.get('timestamp', 0)
                    movie.top_ratings.append(rating)
            
            # 获取真实的评分分布
            rating_distribution = db.get_rating_distribution(movie_id)
            movie_dict = movie.to_dict()
            movie_dict['ratingDistribution'] = rating_distribution
            
            return jsonify(movie_dict)
        else:
            return jsonify({})
    except Exception as e:
        print(f"获取电影信息出错: {e}")
        return jsonify({})

@app.route('/get_rating_distribution')
def get_rating_distribution():
    try:
        movie_id = int(request.args.get('movieId'))
        db = DatabaseManager.get_instance()
        distribution = db.get_rating_distribution(movie_id)
        
        # 计算总数和百分比
        total = sum(distribution.values())
        if total > 0:
            distribution_percentage = {k: (v / total * 100) for k, v in distribution.items()}
        else:
            distribution_percentage = distribution
            
        return jsonify({
            'success': True,
            'distribution': distribution,
            'distributionPercentage': distribution_percentage,
            'total': total
        })
    except Exception as e:
        print(f"获取评分分布出错: {e}")
        return jsonify({'success': False, 'message': '获取评分分布失败'})

@app.route('/getuser')
def get_user():
    try:
        user_id = int(request.args.get('id'))
        user = DataManager.get_instance().get_user_by_id(user_id)
        if user:
            return jsonify(user.to_dict())
        else:
            return jsonify({})
    except Exception as e:
        print(f"获取用户信息出错: {e}")
        return jsonify({})

@app.route('/getsimilarmovie')
def get_similar_movie():
    try:
        movie_id = int(request.args.get('movieId'))
        size = int(request.args.get('size', 6))
        model = request.args.get('model', 'default')
        
        similar_movies = SimilarMovieProcess.get_rec_list(movie_id, size, model)
        return jsonify([movie.to_dict() for movie in similar_movies])
    except Exception as e:
        print(f"获取相似电影出错: {e}")
        return jsonify([])

@app.route('/getmovieratings')
def get_movie_ratings():
    try:
        movie_id = int(request.args.get('id'))
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('size', 10))
        
        offset = (page - 1) * page_size
        
        db = DatabaseManager.get_instance()
        ratings = db.get_ratings_by_movie_id(movie_id, page_size, offset)
        total_count = db.get_ratings_count_by_movie_id(movie_id)
        
        return jsonify({
            'ratings': ratings,
            'total': total_count,
            'page': page,
            'pages': math.ceil(total_count / page_size)
        })
    except Exception as e:
        print(f"获取电影评分出错: {e}")
        return jsonify({'ratings': [], 'total': 0, 'page': 1, 'pages': 0})

@app.route('/getmovieratingsbyscore')
def get_movie_ratings_by_score():
    try:
        movie_id = int(request.args.get('id'))
        score = float(request.args.get('score'))
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('size', 10))
        
        offset = (page - 1) * page_size
        
        db = DatabaseManager.get_instance()
        ratings = db.get_ratings_by_score(movie_id, score, page_size, offset)
        total_count = db.get_ratings_count_by_score(movie_id, score)
        
        return jsonify({
            'ratings': ratings,
            'total': total_count,
            'page': page,
            'pages': math.ceil(total_count / page_size),
            'score': score
        })
    except Exception as e:
        print(f"获取电影特定评分出错: {e}")
        return jsonify({'ratings': [], 'total': 0, 'page': 1, 'pages': 0, 'score': 0})

@app.route('/getrecommendation')
def get_recommendation():
    try:
        genre = request.args.get('genre')
        size = int(request.args.get('size', 8))
        sort_by = request.args.get('sortby', 'rating')
        
        movies = DataManager.get_instance().get_movies_by_genre(genre, size, sort_by)
        return jsonify([movie.to_dict() for movie in movies])
    except Exception as e:
        print(f"获取电影推荐出错: {e}")
        return jsonify([])

@app.route('/movie.html')
def movie_page():
    return render_template('movie.html')

@app.route('/user.html')
def user_page():
    return render_template('user.html')

@app.route('/latest')
def latest_trailers():
    db = DatabaseManager.get_instance()
    latest_movies = db.get_latest_movies(16)
    return render_template('index.html', page_title="最新电影", movies=latest_movies)

@app.route('/top-rated')
def top_rated():
    db = DatabaseManager.get_instance()
    top_movies = db.get_top_rated_movies(16)
    return render_template('index.html', page_title="高分电影", movies=top_movies)

@app.route('/most-commented')
def most_commented():
    db = DatabaseManager.get_instance()
    commented_movies = db.get_most_commented_movies(16)
    return render_template('index.html', page_title="热门评论", movies=commented_movies)

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return redirect('/')
    
    db = DatabaseManager.get_instance()
    search_results = db.search_movies(keyword)
    return render_template('index.html', 
                          page_title=f"搜索结果：'{keyword}'", 
                          movies=search_results,
                          search_term=keyword)

if __name__ == '__main__':
    DataManager.get_instance()
    app.run(host='0.0.0.0', port=6010, debug=False)