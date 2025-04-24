import os
import csv
import mysql.connector
from mysql.connector import Error
import hashlib
import getpass

def connect_to_database():
    try:
        password = getpass.getpass("请输入数据库密码：")
        
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password
        )
        if connection.is_connected():
            print("成功连接到MySQL服务器")
            
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS moviehunter")
            cursor.close()
            
            connection.close()
            
            connection = mysql.connector.connect(
                host='localhost',
                database='moviehunter',
                user='root',
                password=password
            )
            if connection.is_connected():
                print("成功连接到moviehunter数据库")
                return connection
    except Error as e:
        print(f"连接MySQL数据库时出错: {e}")
        return None

def execute_sql_file(connection, sql_file_path):
    try:
        cursor = connection.cursor()
        print(f"正在执行SQL文件: {sql_file_path}")
        
        if not os.path.exists(sql_file_path):
            print(f"错误: SQL文件 {sql_file_path} 不存在")
            return False
            
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read().split(';')
            for command in sql_commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                        print(f"执行SQL命令成功: {command[:50]}...")
                    except Error as e:
                        print(f"执行SQL命令出错: {e}")
                        print(f"出错的命令: {command}")
                        return False
                        
        connection.commit()
        print("成功执行SQL文件")
        return True
    except Error as e:
        print(f"执行SQL文件时出错: {e}")
        return False

def import_movie_data(connection, movie_data_path):
    try:
        cursor = connection.cursor()
        print(f"正在导入电影数据: {movie_data_path}")
        
        if not os.path.exists(movie_data_path):
            print(f"错误: 电影数据文件 {movie_data_path} 不存在")
            return False
            
        batch_size = 100
        movie_batch = []
        count = 0
        successful_count = 0
            
        with open(movie_data_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:
                if len(row) == 3:
                    try:
                        movie_id = int(row[0])
                        title = row[1].strip()
                        
                        release_year = -1
                        if '(' in title and ')' in title:
                            year_str = title[title.rindex('(')+1:title.rindex(')')]
                            try:
                                release_year = int(year_str)
                                title = title[:title.rindex('(')].strip()
                            except ValueError:
                                pass
                        
                        genres = row[2].split('|')
                        genre_str = ','.join(genres)
                        
                        movie_batch.append((movie_id, title, release_year, genre_str, 0, ''))
                        count += 1
                        
                        if len(movie_batch) >= batch_size:
                            inserted = batch_insert_movies(cursor, movie_batch)
                            successful_count += inserted
                            movie_batch = []
                            print(f"已处理 {count} 部电影，成功导入 {successful_count} 部")
                            
                    except Exception as e:
                        print(f"处理电影数据出错: {e}")
                        print(f"出错的电影: {row}")
                        continue
        
        if movie_batch:
            inserted = batch_insert_movies(cursor, movie_batch)
            successful_count += inserted
        
        connection.commit()
        print(f"成功导入电影数据，共 {successful_count}/{count} 部电影")
        return True
    except Error as e:
        print(f"导入电影数据时出错: {e}")
        return False

def batch_insert_movies(cursor, movie_batch):
    try:
        query = """
        INSERT IGNORE INTO movies (id, title, year, genre, rating, description) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, movie_batch)
        return cursor.rowcount
    except Error as e:
        print(f"批量插入电影出错: {e}")
        successful = 0
        for movie in movie_batch:
            try:
                cursor.execute("""
                INSERT IGNORE INTO movies (id, title, year, genre, rating, description) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """, movie)
                if cursor.rowcount > 0:
                    successful += 1
            except Error as inner_e:
                print(f"插入单条电影出错: {inner_e}")
        return successful

def import_rating_data(connection, rating_data_path):
    try:
        cursor = connection.cursor()
        print(f"正在导入评分数据: {rating_data_path}")
        
        if not os.path.exists(rating_data_path):
            print(f"错误: 评分数据文件 {rating_data_path} 不存在")
            return False
        
        user_query = "INSERT IGNORE INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)"
        
        try:
            cursor.execute(user_query, (1, "user_1", hashlib.md5("password".encode()).hexdigest(), "user_1@example.com"))
            connection.commit()
        except Error as e:
            print(f"创建初始用户出错: {e}")
        
        batch_size = 1000
        rating_batch = []
        count = 0
        
        with open(rating_data_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:
                if len(row) == 4:
                    try:
                        user_id = int(row[0])
                        movie_id = int(row[1])
                        rating = float(row[2])
                        
                        cursor.execute(user_query, (
                            user_id, 
                            f"user_{user_id}", 
                            hashlib.md5("password".encode()).hexdigest(), 
                            f"user_{user_id}@example.com"
                        ))
                        
                        rating_batch.append((user_id, movie_id, rating))
                        count += 1
                        
                        if len(rating_batch) >= batch_size:
                            try:
                                rating_query = "INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)"
                                cursor.executemany(rating_query, rating_batch)
                                connection.commit()
                                print(f"已导入 {count} 条评分")
                                rating_batch = []
                            except Error as e:
                                print(f"批量插入评分出错: {e}")
                                connection.rollback()
                                
                                for rating_data in rating_batch:
                                    try:
                                        cursor.execute("INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)", rating_data)
                                        connection.commit()
                                    except Error as inner_e:
                                        print(f"插入单条评分出错: {inner_e}")
                                        connection.rollback()
                                
                                rating_batch = []
                                
                    except Error as e:
                        print(f"处理评分数据出错: {e}")
                        print(f"出错的评分: {row}")
                        connection.rollback()
                        continue
        
        if rating_batch:
            try:
                rating_query = "INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)"
                cursor.executemany(rating_query, rating_batch)
                connection.commit()
            except Error as e:
                print(f"批量插入评分出错: {e}")
                connection.rollback()
                
                for rating_data in rating_batch:
                    try:
                        cursor.execute("INSERT INTO ratings (user_id, movie_id, rating) VALUES (%s, %s, %s)", rating_data)
                        connection.commit()
                    except Error as inner_e:
                        print(f"插入单条评分出错: {inner_e}")
                        connection.rollback()
        
        print(f"成功导入评分数据，共 {count} 条评分")
        return True
    except Error as e:
        print(f"导入评分数据时出错: {e}")
        connection.rollback()
        return False

def update_movie_ratings(connection):
    try:
        cursor = connection.cursor()
        print("正在更新电影的平均评分...")
        
        query = """
        UPDATE movies m
        SET rating = (
            SELECT AVG(rating)
            FROM ratings r
            WHERE r.movie_id = m.id
        )
        """
        cursor.execute(query)
        connection.commit()
        print("成功更新电影评分")
        return True
    except Error as e:
        print(f"更新电影评分时出错: {e}")
        return False

def main():
    print("开始初始化数据库...")
    
    connection = connect_to_database()
    if not connection:
        print("无法连接到数据库，初始化失败")
        return
    
    try:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not execute_sql_file(connection, schema_path):
            print("执行schema.sql文件失败，初始化失败")
            return
        
        movie_data_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.csv')
        if os.path.exists(movie_data_path):
            if not import_movie_data(connection, movie_data_path):
                print("导入电影数据失败")
        else:
            print(f"电影数据文件不存在: {movie_data_path}")
        
        rating_data_path = os.path.join(os.path.dirname(__file__), 'data', 'ratings.csv')
        if os.path.exists(rating_data_path):
            if not import_rating_data(connection, rating_data_path):
                print("导入评分数据失败")
        else:
            print(f"评分数据文件不存在: {rating_data_path}")
        
        update_movie_ratings(connection)
        
        print("数据库初始化完成")
    except Exception as e:
        print(f"初始化过程中出错: {e}")
    finally:
        if connection.is_connected():
            connection.close()
            print("已断开与MySQL数据库的连接")

if __name__ == "__main__":
    main() 