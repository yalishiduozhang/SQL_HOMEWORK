-- 创建数据库
CREATE DATABASE IF NOT EXISTS moviehunter;
USE moviehunter;

-- 创建电影表
CREATE TABLE IF NOT EXISTS movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT,
    director VARCHAR(255),
    genre VARCHAR(100),
    rating DECIMAL(3,1),
    poster_url VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建电影向量表
CREATE TABLE IF NOT EXISTS movie_embeddings (
    movie_id INT PRIMARY KEY,
    embedding TEXT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户向量表
CREATE TABLE IF NOT EXISTS user_embeddings (
    user_id INT PRIMARY KEY,
    embedding TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建评分表（支持半星评分）
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL CHECK (rating >= 0.5 AND rating <= 5.0),
    comment TEXT,
    timestamp INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    UNIQUE KEY unique_user_movie (user_id, movie_id)
);