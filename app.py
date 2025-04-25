from flask import Flask, jsonify, request, render_template, redirect
import os
import json
import math
import numpy as np
from collections import defaultdict
import mysql.connector
from mysql.connector import Error
import getpass

app = Flask(__name__, static_url_path='/static', static_folder='static')

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
            if DatabaseManager._password is None:
                DatabaseManager._password = getpass.getpass("请输入数据库密码：")
            
            # 创建连接池
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="moviehunter",
                pool_size=5,
                host='localhost',
                database='moviehunter',
                user='root',
                password=DatabaseManager._password
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
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"执行更新时出错: {e}")
            return False
    
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
    
    def add_movie(self, title, year, director, genre, rating, poster_url, description):
        query = """
        INSERT INTO movies (title, year, director, genre, rating, poster_url, description) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (title, year, director, genre, rating, poster_url, description))
    
    def add_user(self, username, password, email):
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        return self.execute_update(query, (username, password, email))
    
    def add_rating(self, user_id, movie_id, rating, comment):
        query = "INSERT INTO ratings (user_id, movie_id, rating, comment) VALUES (%s, %s, %s, %s)"
        return self.execute_update(query, (user_id, movie_id, rating, comment))

    def get_movie_embedding(self, movie_id):
        query = "SELECT embedding FROM movie_embeddings WHERE movie_id = %s"
        result = self.execute_query(query, (movie_id,))
        return result[0]['embedding'] if result else None
    
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
            movie.rating = movie_data['rating']
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
                rating.score = rating_data['rating']
                rating.comment = rating_data['comment']
                rating.title = rating_data['title']
                rating.timestamp = rating_data['timestamp']
                
                user.add_rating(rating)
                
                if rating.movie_id in self.movie_map:
                    movie = self.movie_map[rating.movie_id]
                    movie.add_rating(rating)

    
    # def load_movie_data(self, movie_data_path):
    #     print(f"从 {movie_data_path} 加载电影数据...")
    #     with open(movie_data_path, 'r', encoding='utf-8') as file:
    #         reader = csv.reader(file)
    #         next(reader)
    #         for row in reader:
    #             if len(row) == 3:
    #                 movie = Movie()
    #                 movie.movie_id = int(row[0])
                    
    #                 title = row[1].strip()
    #                 release_year = self.parse_release_year(title)
    #                 if release_year == -1:
    #                     movie.title = title
    #                 else:
    #                     movie.release_year = release_year
    #                     movie.title = title[:-6].strip()
                    
    #                 genres = row[2]
    #                 if genres.strip():
    #                     for genre in genres.split('|'):
    #                         movie.genres.append(genre)
    #                         self.add_movie_to_genre_index(genre, movie)
                    
    #                 self.movie_map[movie.movie_id] = movie
        
    #     print(f"电影数据加载完成，共 {len(self.movie_map)} 部电影")
    
    # def load_link_data(self, link_data_path):
    #     print(f"从 {link_data_path} 加载链接数据...")
    #     count = 0
    #     with open(link_data_path, 'r', encoding='utf-8') as file:
    #         reader = csv.reader(file)
    #         next(reader)
    #         for row in reader:
    #             if len(row) == 3:
    #                 movie_id = int(row[0])
    #                 movie = self.movie_map.get(movie_id)
    #                 if movie:
    #                     count += 1
    #                     movie.imdb_id = row[1].strip()
    #                     movie.tmdb_id = row[2].strip()
    #     print(f"链接数据加载完成，共更新 {count} 部电影")
    
    # def load_rating_data(self, rating_data_path):
    #     print(f"从 {rating_data_path} 加载评分数据...")
    #     with open(rating_data_path, 'r', encoding='utf-8') as file:
    #         reader = csv.reader(file)
    #         next(reader)
    #         for row in reader:
    #             if len(row) == 4:
    #                 user_id = int(row[0])
    #                 movie_id = int(row[1])
    #                 score = float(row[2])
    #                 timestamp = int(row[3])
                    
    #                 if user_id not in self.user_map:
    #                     self.user_map[user_id] = User()
    #                     self.user_map[user_id].user_id = user_id
                    
    #                 movie = self.movie_map.get(movie_id)
    #                 if movie:
    #                     rating = Rating()
    #                     rating.user_id = user_id
    #                     rating.movie_id = movie_id
    #                     rating.score = score
    #                     rating.timestamp = timestamp
    #                     rating.title = movie.title
                        
    #                     self.user_map[user_id].add_rating(rating)
    #                     movie.add_rating(rating)
        
    #     print(f"评分数据加载完成，共 {len(self.user_map)} 个用户")
    
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

class Movie:
    def __init__(self):
        self.movie_id = 0
        self.title = ""
        self.release_year = 0
        self.imdb_id = ""
        self.tmdb_id = ""
        self.genres = []
        self.rating_number = 0
        self.average_rating = 0
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
        self.average_rating = 0
        self.highest_rating = 0
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
            
            return jsonify(movie.to_dict())
        else:
            return jsonify({})
    except Exception as e:
        print(f"获取电影信息出错: {e}")
        return jsonify({})

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
    return render_template('index.html', page_title="Latest Trailers", movies=latest_movies)

@app.route('/top-rated')
def top_rated():
    db = DatabaseManager.get_instance()
    top_movies = db.get_top_rated_movies(16)
    return render_template('index.html', page_title="Top Rated Movies", movies=top_movies)

@app.route('/most-commented')
def most_commented():
    db = DatabaseManager.get_instance()
    commented_movies = db.get_most_commented_movies(16)
    return render_template('index.html', page_title="Most Commented Movies", movies=commented_movies)

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return redirect('/')
    
    db = DatabaseManager.get_instance()
    search_results = db.search_movies(keyword)
    return render_template('index.html', 
                          page_title=f"Search Results for '{keyword}'", 
                          movies=search_results,
                          search_term=keyword)

if __name__ == '__main__':
    DataManager.get_instance()
    app.run(host='0.0.0.0', port=6010, debug=False) 