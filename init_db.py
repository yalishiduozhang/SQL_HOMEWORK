import os
import csv
import mysql.connector
from mysql.connector import Error
import hashlib
import getpass

def connect_to_database():
    try:
        password = getpass.getpass("请输入MySQL数据库密码：")
        
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=password
        )
        if connection.is_connected():
            print("✓ 成功连接到MySQL服务器")
            
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS moviehunter")
            cursor.close()
            print("✓ 数据库moviehunter已准备就绪")
            
            connection.close()
            
            connection = mysql.connector.connect(
                host='localhost',
                database='moviehunter',
                user='root',
                password=password
            )
            if connection.is_connected():
                print("✓ 成功连接到moviehunter数据库")
                return connection
    except Error as e:
        print(f"✗ 连接MySQL数据库时出错: {e}")
        return None

def execute_sql_file(connection, sql_file_path):
    try:
        cursor = connection.cursor()
        print(f"→ 正在执行SQL文件: {sql_file_path}")
        
        if not os.path.exists(sql_file_path):
            print(f"✗ 错误: SQL文件 {sql_file_path} 不存在")
            return False
            
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read().split(';')
            for command in sql_commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                    except Error as e:
                        print(f"✗ 执行SQL命令出错: {e}")
                        print(f"  出错的命令: {command[:50]}...")
                        return False
                        
        connection.commit()
        print("✓ 成功执行SQL文件")
        return True
    except Error as e:
        print(f"✗ 执行SQL文件时出错: {e}")
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
            next(reader)  # 跳过标题行
            
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
                            print(f"  已处理 {count} 部电影，成功导入 {successful_count} 部")
                            
                    except Exception as e:
                        print(f"✗ 处理电影数据出错: {e}")
                        print(f"  出错的数据行: {row}")
                        continue
        
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
            except Error as inner_e:
                print(f"✗ 插入单条电影出错: {inner_e}")
        return successful

def import_rating_data(connection, rating_data_path):
    try:
        cursor = connection.cursor()
        print(f"\n→ 正在导入评分数据: {rating_data_path}")

        if not os.path.exists(rating_data_path):
            print(f"✗ 错误: 评分数据文件 {rating_data_path} 不存在")
            return False

        # 创建测试用户账号
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

        # --- 优化开始 ---
        user_batch_size = 2000
        rating_batch_size = 10000  # 增大批处理大小以提高效率

        user_batch = []
        rating_batch = []
        
        processed_users = set()  # 跟踪已处理的用户，避免重复添加
        
        total_ratings_processed = 0
        total_users_created = 0
        
        user_query = "INSERT IGNORE INTO users (id, username, password, email) VALUES (%s, %s, %s, %s)"
        # 使用 INSERT IGNORE 忽略外键约束失败等错误，提高导入速度
        rating_query = "INSERT IGNORE INTO ratings (user_id, movie_id, rating, timestamp) VALUES (%s, %s, %s, %s)"
        default_password = hashlib.md5("password".encode()).hexdigest()

        print("\n→ 开始逐行处理和批量导入...")
        with open(rating_data_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 跳过标题行
            
            for row in reader:
                if len(row) == 4:
                    try:
                        user_id = int(row[0])
                        movie_id = int(row[1])
                        rating = float(row[2])
                        if rating < 0.5: rating = 0.5
                        elif rating > 5.0: rating = 5.0
                        timestamp = int(row[3])
                        
                        # 如果是新用户，则添加到用户批处理中
                        if user_id not in processed_users:
                            user_batch.append((
                                user_id, 
                                f"user_{user_id}", 
                                default_password, 
                                f"user_{user_id}@example.com"
                            ))
                            processed_users.add(user_id)
                        
                        # 添加评分到批处理中
                        rating_batch.append((user_id, movie_id, rating, timestamp))
                        total_ratings_processed += 1
                        
                        # 当用户批处理达到规模时，执行插入
                        if len(user_batch) >= user_batch_size:
                            cursor.executemany(user_query, user_batch)
                            total_users_created += cursor.rowcount
                            connection.commit()
                            user_batch = []
                            print(f"  已创建 {total_users_created} 个用户...")
                        
                        # 当评分批处理达到规模时，执行插入
                        if len(rating_batch) >= rating_batch_size:
                            cursor.executemany(rating_query, rating_batch)
                            connection.commit()
                            print(f"  已导入 {total_ratings_processed} 条评分...")
                            rating_batch = []

                    except (ValueError, IndexError) as e:
                        print(f"⚠ 跳过格式错误的行: {row} - {e}")
                        continue
        
        # 插入剩余的用户
        if user_batch:
            cursor.executemany(user_query, user_batch)
            total_users_created += cursor.rowcount
            connection.commit()

        # 插入剩余的评分
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
    except Exception as e:
        print(f"✗ 处理评分文件时发生未知错误: {e}")
        return False

def import_embeddings(connection, movie_emb_path, user_emb_path):
    try:
        cursor = connection.cursor()
        print("\n→ 正在导入嵌入向量数据...")
        
        # 导入电影嵌入向量
        if os.path.exists(movie_emb_path):
            movie_count = 0
            with open(movie_emb_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        movie_id = int(parts[0])
                        embedding = parts[1]
                        try:
                            cursor.execute(
                                "INSERT IGNORE INTO movie_embeddings (movie_id, embedding) VALUES (%s, %s)",
                                (movie_id, embedding)
                            )
                            if cursor.rowcount > 0:
                                movie_count += 1
                        except Error as e:
                            print(f"✗ 插入电影嵌入向量出错: {e}")
            print(f"✓ 成功导入 {movie_count} 个电影嵌入向量")
        else:
            print(f"⚠ 电影嵌入向量文件不存在: {movie_emb_path}")
        
        # 导入用户嵌入向量
        if os.path.exists(user_emb_path):
            user_count = 0
            with open(user_emb_path, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        user_id = int(parts[0])
                        embedding = parts[1]
                        try:
                            cursor.execute(
                                "INSERT IGNORE INTO user_embeddings (user_id, embedding) VALUES (%s, %s)",
                                (user_id, embedding)
                            )
                            if cursor.rowcount > 0:
                                user_count += 1
                        except Error as e:
                            print(f"✗ 插入用户嵌入向量出错: {e}")
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
    print("MOVIE HUNTER数据库初始化程序")
    print("=" * 50)
    
    connection = connect_to_database()
    if not connection:
        print("\n✗ 无法连接到数据库，初始化失败")
        return
    
    try:
        # 执行数据库结构脚本
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not execute_sql_file(connection, schema_path):
            print("\n✗ 执行schema.sql文件失败，初始化失败")
            return
        
        # 导入电影数据
        movie_data_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.csv')
        if os.path.exists(movie_data_path):
            if not import_movie_data(connection, movie_data_path):
                print("⚠ 导入电影数据失败，但继续执行...")
        else:
            print(f"⚠ 电影数据文件不存在: {movie_data_path}")
        
        # 导入评分数据
        rating_data_path = os.path.join(os.path.dirname(__file__), 'data', 'ratings.csv')
        if os.path.exists(rating_data_path):
            if not import_rating_data(connection, rating_data_path):
                print("⚠ 导入评分数据失败，但继续执行...")
        else:
            print(f"⚠ 评分数据文件不存在: {rating_data_path}")

        # 导入嵌入向量数据
        movie_emb_path = os.path.join(os.path.dirname(__file__), 'data', 'item2vecEmb.csv')
        user_emb_path = os.path.join(os.path.dirname(__file__), 'data', 'userEmb.csv')
        
        if not os.path.exists(movie_emb_path):
            print(f"⚠ 电影嵌入向量文件不存在: {movie_emb_path}")
        
        if not os.path.exists(user_emb_path):
            print(f"⚠ 用户嵌入向量文件不存在: {user_emb_path}")
            
        import_embeddings(connection, movie_emb_path, user_emb_path)
        
        # 更新电影评分
        update_movie_ratings(connection)
        
        print("\n" + "=" * 50)
        print("✓ 数据库初始化完成！")
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
    finally:
        if connection.is_connected():
            connection.close()
            print("\n✓ 已断开与MySQL数据库的连接")

if __name__ == "__main__":
    main()