import os
import csv
import hashlib
import mysql.connector
from mysql.connector import Error
import time
import sys

def wait_for_mysql(host, port, user, password, database, max_retries=30):
    print("等待 MySQL 服务启动...")
    retries = 0
    while retries < max_retries:
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            if connection.is_connected():
                print("✓ 成功连接到 MySQL 数据库")
                connection.close()
                return True
        except Error:
            retries += 1
            print(f"等待 MySQL 启动... ({retries}/{max_retries})")
            time.sleep(2)
    
    print("✗ 无法连接到 MySQL 数据库")
    return False

def connect_to_database():
    host = os.getenv('MYSQL_HOST', 'mysql')
    port = int(os.getenv('MYSQL_PORT', '3306'))
    user = os.getenv('MYSQL_USER', 'moviehunter_user')
    password = os.getenv('MYSQL_PASSWORD', 'moviehunter_password')
    database = os.getenv('MYSQL_DATABASE', 'moviehunter')
    
    if not wait_for_mysql(host, port, user, password, database):
        return None
    
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("✓ 成功连接到 moviehunter 数据库")
            return connection
    except Error as e:
        print(f"✗ 连接 MySQL 数据库时出错: {e}")
        return None

def check_data_exists(connection):
    try:
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM movies")
        movie_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ratings")
        rating_count = cursor.fetchone()[0]
        
        cursor.close()
        
        print(f"当前数据库状态：")
        print(f"- 电影数量: {movie_count}")
        print(f"- 用户数量: {user_count}")
        print(f"- 评分数量: {rating_count}")
        
        if movie_count > 0 or user_count > 0 or rating_count > 0:
            return True
        return False
        
    except Error as e:
        print(f"✗ 检查数据时出错: {e}")
        return False

def import_movie_data(connection, movie_data_path):
    try:
        cursor = connection.cursor()
        print(f"\n→ 正在导入电影数据: {movie_data_path}")
        
        if not os.path.exists(movie_data_path):
            print(f"✗ 错误: 电影数据文件 {movie_data_path} 不存在")
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
                            year_start = title.rfind('(')
                            year_end = title.rfind(')')
                            if year_start < year_end:
                                year_str = title[year_start+1:year_end]
                                try:
                                    release_year = int(year_str)
                                    title = title[:year_start].strip()
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
                            
                    except Exception as e:
                        print(f"处理电影数据出错: {e}")
        
        if movie_batch:
            inserted = batch_insert_movies(cursor, movie_batch)
            successful_count += inserted
        
        connection.commit()
        print(f"✓ 成功导入电影数据，共 {successful_count}/{count} 部电影")
        return True
    except Error as e:
        print(f"✗ 导入电影数据时出错: {e}")
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
        print(f"✗ 批量插入电影出错: {e}")
        successful = 0
        for movie in movie_batch:
            try:
                cursor.execute("""
                INSERT IGNORE INTO movies (id, title, year, genre, rating, description) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """, movie)
                if cursor.rowcount > 0:
                    successful += 1
            except Error:
                pass
        return successful

def import_rating_data(connection, rating_data_path):
    try:
        cursor = connection.cursor()
        print(f"\n→ 正在导入评分数据: {rating_data_path}")

        if not os.path.exists(rating_data_path):
            print(f"✗ 错误: 评分数据文件 {rating_data_path} 不存在")
            return False

        test_accounts = [
            (999999, "test", "123456", "test@example.com")
        ]
        print("\n→ 创建测试账号...")
        try:
            user_query = "INSERT IGNORE INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)"
            for user_id, username, password, email in test_accounts:
                hashed_password = hashlib.md5(password.encode()).hexdigest()
                cursor.execute(user_query, (user_id, username, hashed_password, email))
            connection.commit()
            print("✓ 创建账号 - 用户名: test, 密码: 123456")
        except Error as e:
            print(f"✗ 创建测试用户出错: {e}")

        user_batch_size = 2000
        rating_batch_size = 10000

        user_batch = []
        rating_batch = []
        
        processed_users = set()
        
        total_ratings_processed = 0
        total_users_created = 0
        
        user_query = "INSERT IGNORE INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)"
        rating_query = "INSERT IGNORE INTO ratings (user_id, movie_id, rating, timestamp) VALUES (%s, %s, %s, %s)"
        default_password = hashlib.md5("password".encode()).hexdigest()

        print("\n→ 开始逐行处理和批量导入...")
        with open(rating_data_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) == 4:
                    try:
                        user_id = int(row[0])
                        movie_id = int(row[1])
                        rating = float(row[2])
                        timestamp = int(row[3])
                        
                        if user_id not in processed_users:
                            username = f"user_{user_id}"
                            email = f"user_{user_id}@example.com"
                            user_batch.append((user_id, username, default_password, email))
                            processed_users.add(user_id)
                            
                            if len(user_batch) >= user_batch_size:
                                cursor.executemany(user_query, user_batch)
                                total_users_created += cursor.rowcount
                                connection.commit()
                                user_batch = []
                        
                        rating_batch.append((user_id, movie_id, rating, timestamp))
                        total_ratings_processed += 1
                        
                        if len(rating_batch) >= rating_batch_size:
                            cursor.executemany(rating_query, rating_batch)
                            connection.commit()
                            rating_batch = []
                            if total_ratings_processed % 50000 == 0:
                                print(f"已处理 {total_ratings_processed} 条评分记录...")

                    except (ValueError, IndexError) as e:
                        print(f"处理评分数据出错: {e}")
        
        if user_batch:
            cursor.executemany(user_query, user_batch)
            total_users_created += cursor.rowcount
            connection.commit()

        if rating_batch:
            cursor.executemany(rating_query, rating_batch)
            connection.commit()
        
        print(f"\n✓ 成功处理 {total_ratings_processed} 条评分记录")
        print(f"✓ 创建了 {total_users_created} 个新用户账号（默认密码: password）")
        return True
    except Error as e:
        print(f"✗ 导入评分数据时出错: {e}")
        if connection and connection.is_connected():
            connection.rollback()
        return False

def import_embeddings(connection, movie_emb_path, user_emb_path):
    try:
        cursor = connection.cursor()
        print("\n→ 正在导入嵌入向量数据...")
        
        if os.path.exists(movie_emb_path):
            movie_count = 0
            with open(movie_emb_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        try:
                            movie_id = int(parts[0])
                            embedding = parts[1]
                            cursor.execute(
                                "INSERT IGNORE INTO movie_embeddings (movie_id, embedding) VALUES (%s, %s)",
                                (movie_id, embedding)
                            )
                            movie_count += 1
                        except (ValueError, Error):
                            pass
            print(f"✓ 成功导入 {movie_count} 个电影嵌入向量")
        else:
            print(f"⚠ 电影嵌入向量文件不存在: {movie_emb_path}")
        
        if os.path.exists(user_emb_path):
            user_count = 0
            with open(user_emb_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        try:
                            user_id = int(parts[0])
                            embedding = parts[1]
                            cursor.execute(
                                "INSERT IGNORE INTO user_embeddings (user_id, embedding) VALUES (%s, %s)",
                                (user_id, embedding)
                            )
                            user_count += 1
                        except (ValueError, Error):
                            pass
            print(f"✓ 成功导入 {user_count} 个用户嵌入向量")
        else:
            print(f"⚠ 用户嵌入向量文件不存在: {user_emb_path}")
        
        connection.commit()
        return True
    except Error as e:
        print(f"✗ 导入嵌入向量数据时出错: {e}")
        return False

def update_movie_ratings(connection):
    try:
        cursor = connection.cursor()
        print("\n→ 正在更新电影的平均评分...")
        
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
        print("✓ 成功更新电影评分")
        return True
    except Error as e:
        print(f"✗ 更新电影评分时出错: {e}")
        return False

def main():
    print("=" * 50)
    print("MOVIE HUNTER Docker 数据库初始化程序")
    print("=" * 50)
    
    connection = connect_to_database()
    if not connection:
        print("\n✗ 无法连接到数据库，初始化失败")
        sys.exit(1)
    
    try:
        data_exists = check_data_exists(connection)
        
        if data_exists:
            print("\n数据已存在，跳过初始化...")
            return
        
        movie_data_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.csv')
        if os.path.exists(movie_data_path):
            if not import_movie_data(connection, movie_data_path):
                print("⚠ 导入电影数据失败，但继续执行...")
        else:
            print(f"⚠ 电影数据文件不存在: {movie_data_path}")
        
        rating_data_path = os.path.join(os.path.dirname(__file__), 'data', 'ratings.csv')
        if os.path.exists(rating_data_path):
            if not import_rating_data(connection, rating_data_path):
                print("⚠ 导入评分数据失败，但继续执行...")
        else:
            print(f"⚠ 评分数据文件不存在: {rating_data_path}")

        movie_emb_path = os.path.join(os.path.dirname(__file__), 'data', 'item2vecEmb.csv')
        user_emb_path = os.path.join(os.path.dirname(__file__), 'data', 'userEmb.csv')
        
        import_embeddings(connection, movie_emb_path, user_emb_path)
        
        update_movie_ratings(connection)
        
        print("\n" + "=" * 50)
        print("✓ Docker 数据库初始化完成！")
        print("\n可用的账号：")
        print("\n【测试账号】（全新账号，无历史评分）")
        print("- 用户名: test    密码: 123456")
        print("\n【历史用户】（包含历史评分数据）")
        print("- 用户名: user_1  密码: password")
        print("- 用户名: user_2  密码: password")
        print("- 用户名: user_3  密码: password")
        print("- ... 更多用户格式: user_[ID]，密码都是 password")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 初始化过程中出错: {e}")
        sys.exit(1)
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ 已断开与 MySQL 数据库的连接")

if __name__ == "__main__":
    main()
