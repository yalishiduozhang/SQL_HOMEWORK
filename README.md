# MovieHunter 电影推荐系统

MovieHunter是一个功能完善的基于Flask和MySQL的电影推荐系统，能够根据用户对电影的评分和喜好提供个性化的电影推荐。系统结合了协同过滤和基于内容的推荐算法，为用户提供精准的电影建议。

## 目前实现的功能

- 浏览电影列表与详情
- 按类型筛选电影
- 基于用户历史评分的个性化电影推荐
- 发现与特定电影相似的其他影片
- 浏览最新上映的电影（LATEST TRAILERS）
- 查看评分最高的电影（TOP RATED）
- 查看评论最多的热门电影（MOST COMMENTED）
- 用户个人资料页面，包括个性化头像和评分历史
- 完整的导航菜单，支持全站快速访问
- 搜索功能，允许用户根据关键词查找电影（SEARCH）
- 实现获取特定电影特定评分的用户评价
- 用户注册和登录系统，支持密码MD5加密
- 半星评分系统（0.5-5.0分），支持评分修改
- 电影添加功能，支持海报图片上传和自动压缩
- 评分分布可视化，显示每个评分级别的统计数据
- 双重推荐算法：传统类型匹配 + 智能嵌入向量相似度
- 会话管理和用户状态跟踪
- 多样化评分展示，同时显示高分和低分评价
- 实时评分统计和电影平均分自动更新
- 数据库连接池优化，提高系统性能

## 我们目前用到的技术

- **后端**: Python 3.6+, Flask
- **数据库**: MySQL 5.7+, mysql-connector-python (连接池)
- **数据处理**: NumPy, Pandas
- **前端**: HTML, CSS, JavaScript, jQuery
- **图像处理**: PIL (Pillow) - 海报图片压缩和格式转换
- **安全**: hashlib (MD5密码加密), secrets (会话密钥生成)
- **数据分析**: 协同过滤算法, 基于内容的推荐算法, item2vec嵌入向量
- **架构模式**: 单例模式, MVC架构, 数据访问对象模式

## 环境要求

- Python 3.6+
- MySQL 5.7+
- Flask (Web框架)
- NumPy (数值计算)
- Pandas (数据处理)
- mysql-connector-python (8.0.22+) - 数据库连接和连接池
- Pillow (PIL) - 图像处理
- hashlib (内置) - 密码加密
- secrets (内置) - 安全随机数生成
- datetime (内置) - 时间处理
- math (内置) - 数学计算

## 安装步骤

### 1. 安装MySQL

#### Windows
1. 下载并安装MySQL：https://dev.mysql.com/downloads/installer/
2. 安装过程中设置root用户密码（请记住此密码）
3. 确保MySQL服务已启动

#### macOS
```bash
# macOS
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql

# Windows
下载并安装 MySQL：https://dev.mysql.com/downloads/installer/
```

#### 2. 安装 Python 依赖
```bash
# 创建虚拟环境（推荐）
python -m venv moviehunter-env
source moviehunter-env/bin/activate  # Windows: moviehunter-env\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 初始化数据库
```bash
# 运行初始化脚本
python init_db.py

# 按提示输入 MySQL root 密码
# 等待数据导入完成（约2-5分钟）
```

#### 4. 启动应用
```bash
python app.py
# 输入 MySQL 密码
# 访问 http://localhost:6010
```

## 🐳 Docker 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs web
docker-compose logs mysql

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 完全清理（包括数据卷）
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache
```

## 🔧 配置说明

### Docker 环境变量
可以通过环境变量自定义配置：

```env
# 数据库配置
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=moviehunter_user
MYSQL_PASSWORD=moviehunter_password
MYSQL_DATABASE=moviehunter

# 应用配置
FLASK_ENV=production
```

### 端口配置
- **Web 应用**: 6010 (可在 docker-compose.yml 中修改)
- **MySQL**: 3306 (可在 docker-compose.yml 中修改)

### 数据持久化
- MySQL 数据存储在 Docker 卷 `mysql_data` 中
- 静态文件（图片等）映射到 `./static` 目录
- 数据文件映射到 `./data` 目录

## 💾 数据库架构

### 核心数据表

#### movies (电影表)
```sql
CREATE TABLE movies (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INT,
    director VARCHAR(255),
    genre VARCHAR(255),
    rating DECIMAL(3,2) DEFAULT 0,
    poster_url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### users (用户表)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(32) NOT NULL,  -- MD5加密
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### ratings (评分表)
```sql
CREATE TABLE ratings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating DECIMAL(2,1) NOT NULL,  -- 0.5-5.0
    comment TEXT,
    timestamp INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);
```

#### movie_embeddings (电影向量表)
```sql
CREATE TABLE movie_embeddings (
    movie_id INT PRIMARY KEY,
    embedding TEXT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);
```

#### user_embeddings (用户向量表)
```sql
CREATE TABLE user_embeddings (
    user_id INT PRIMARY KEY,
    embedding TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 数据文件说明

系统支持以下CSV数据文件的自动导入：

- **movies.csv**: 电影基础信息（必需）
- **ratings.csv**: 用户评分数据（必需）
- **links.csv**: 电影外部链接信息（可选）
- **item2vecEmb.csv**: 电影向量嵌入（推荐算法）
- **userEmb.csv**: 用户向量嵌入（推荐算法）

### 数据导入特性

- ✅ **批量处理**: 采用批处理技术，提高导入效率
- ✅ **错误处理**: 多级错误处理和智能回退机制
- ✅ **自动创建**: 自动创建历史用户账号
- ✅ **数据验证**: 评分范围验证和数据格式检查
- ✅ **进度显示**: 实时显示导入进度和统计信息

## 📁 项目结构

```
MovieHunter/
├── app.py                    # 🔥 Flask主应用（1200+行核心代码）
├── init_db.py               # 📊 数据库初始化脚本
├── docker-init.py           # 🐳 Docker环境初始化
├── schema.sql               # 🗄️ 数据库表结构定义
├── requirements.txt         # 📦 Python依赖清单
├── deploy.sh               # 🚀 一键部署脚本（已优化）
├── test_docker_check.sh    # 🧪 Docker环境检测脚本
├── 
├── 🐳 Docker配置
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # 生产环境编排
├── docker-compose.dev.yml  # 开发环境编排
├── 
├── 📂 数据目录
├── data/
│   ├── movies.csv          # 电影基础数据
│   ├── ratings.csv         # 用户评分数据
│   ├── links.csv           # 电影链接数据
│   ├── item2vecEmb.csv     # 电影向量嵌入
│   ├── userEmb.csv         # 用户向量嵌入
│   └── modelSamples.csv    # 模型样本数据
├── 
├── 🎨 前端资源
├── static/
│   ├── css/
│   │   └── my-css.css      # 主样式文件（900+行）
│   ├── js/
│   │   ├── jquery-3.2.1.min.js
│   │   └── recsys.js       # 核心交互脚本（500+行）
│   ├── images/
│   │   ├── avatar/         # 用户头像图片
│   │   ├── logo.gif        # 网站Logo
│   │   └── default-poster.jpg
│   └── posters/            # 电影海报存储（300+张）
│       ├── 1.jpg
│       ├── 2.jpg
│       └── ...
├── 
└── 📄 页面模板
    └── templates/
        ├── index.html      # 🏠 首页（电影列表）
        ├── movie.html      # 🎬 电影详情页
        ├── user.html       # 👤 用户中心页
        ├── login.html      # 🔐 登录页面
        ├── register.html   # ✍️ 注册页面
        └── add_movie.html  # ➕ 添加电影页面
```

### 核心文件说明

#### 🔥 app.py (主应用)
- **1216行**核心代码
- 完整的MVC架构
- 20+个路由接口
- 用户认证系统
- 推荐算法实现
- 图片上传处理

#### 🎨 前端文件
- **my-css.css**: 900+行响应式样式
- **recsys.js**: 500+行交互逻辑
- **6个HTML模板**: 完整的用户界面

#### 🐳 Docker配置
- **Dockerfile**: 多阶段构建优化
- **docker-compose.yml**: 生产环境配置
- **deploy.sh**: 智能部署脚本（已优化错误检查）

## 🎯 功能特性详解

### 👤 用户认证系统
- **安全注册**: 用户名唯一性检查、邮箱验证、密码加密
- **会话管理**: Flask Session支持的安全登录状态
- **权限控制**: 登录后才能评分、添加电影等操作

### 🎬 电影管理系统
- **智能搜索**: 支持电影标题、类型关键词搜索
- **分类浏览**: 18种电影类型分类筛选
- **电影添加**: 
  - 用户可添加新电影
  - 支持海报图片上传（自动优化）
  - 类型多选验证
  - 图片格式检查和大小限制

### ⭐ 评分系统
- **精细评分**: 支持0.5-5.0分，0.5分为最小单位
- **评论功能**: 文字评论与数字评分结合
- **评分统计**: 
  - 用户个人评分统计（平均分、最高分、最低分）
  - 电影评分分布图表
  - 评分历史时间线

### � 推荐算法
- **协同过滤**: 基于用户历史行为的推荐
- **内容推荐**: 基于电影特征的相似度推荐
- **混合推荐**: 多算法结合提升推荐精度
- **实时更新**: 用户新评分后立即更新推荐结果

### 🎨 用户界面
- **响应式设计**: 支持桌面和移动设备
- **现代化UI**: Bootstrap风格，美观易用
- **个性化头像**: 自动分配用户头像
- **加载动画**: 提升用户体验的交互反馈

## 🔧 技术亮点

### 🏗️ 架构设计
- **MVC模式**: 清晰的代码结构分离
- **单例模式**: 数据库连接池管理
- **工厂模式**: 数据管理器统一接口

### 🚀 性能优化
- **数据库连接池**: MySQL连接复用，提升并发性能
- **批量数据处理**: 大数据量导入优化
- **图片压缩**: 自动优化上传图片尺寸和质量
- **静态资源**: CDN友好的静态文件组织

### �️ 安全特性
- **密码加密**: MD5哈希存储（可升级为bcrypt）
- **SQL注入防护**: 参数化查询
- **文件上传安全**: 类型检查和大小限制
- **会话安全**: 随机Session密钥

### � DevOps
- **容器化部署**: Docker + Docker Compose
- **环境隔离**: 开发/生产环境分离
- **健康检查**: 服务状态自动监控
- **日志管理**: 结构化日志输出
- **一键部署**: 自动化部署脚本

## 🚨 故障排除

### Docker 环境问题

#### 1. 端口冲突
```bash
# 检查端口占用
lsof -i :6010  # Web应用端口
lsof -i :3306  # MySQL端口

# 解决方案：修改 docker-compose.yml 中的端口映射
# 或停止占用端口的服务
```

#### 2. Docker 守护进程未运行
```bash
# 错误信息：Cannot connect to the Docker daemon
# 解决方案：
# macOS: 启动 Docker Desktop 应用
# Linux: sudo systemctl start docker
# Windows: 启动 Docker Desktop
```

#### 3. MySQL 初始化失败
```bash
# 查看详细错误日志
docker-compose logs mysql

# 常见解决方案：
docker-compose down -v  # 清理数据卷
docker-compose up -d mysql  # 重新启动MySQL
```

#### 4. 数据导入超时
```bash
# 增加等待时间或手动重试
docker-compose --profile init run --rm init-data

# 检查数据文件是否存在
ls -la data/movies.csv
ls -la data/ratings.csv
```

### 传统部署问题

#### 1. MySQL 连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# 检查防火墙设置
sudo ufw status  # Ubuntu
```

#### 2. Python 依赖问题
```bash
# 重新安装依赖
pip uninstall mysql-connector-python
pip install mysql-connector-python>=8.0.22

# 或使用虚拟环境
python -m venv moviehunter-env
source moviehunter-env/bin/activate
pip install -r requirements.txt
```

#### 3. 权限问题
```bash
# 给脚本执行权限
chmod +x deploy.sh
chmod +x test_docker_check.sh

# 检查目录权限
ls -la static/posters/
```

### 性能优化

#### 1. 大数据量导入优化
- 分批导入大型CSV文件
- 调整MySQL配置参数
- 使用SSD存储改善I/O性能

#### 2. 应用性能调优
```bash
python app.py
```

5. 按提示输入MySQL数据库密码
6. 然后在浏览器中访问：http://localhost:6010

## 数据导入说明

系统使用CSV文件作为数据源，支持以下数据文件：

- `movies.csv`: 包含电影基本信息（ID、标题、类型等）
- `ratings.csv`: 包含用户对电影的评分数据
- `links.csv`: 包含电影外部链接信息
- `item2vecEmb.csv`: 电影向量嵌入数据（用于相似性计算）
- `userEmb.csv`: 用户向量嵌入数据（用于个性化推荐）

数据导入过程中采用了批量处理技术，大幅提高了导入效率。系统还实现了多级错误处理和智能回退机制，确保数据导入的稳定性和可靠性。

## 数据库结构

MovieHunter使用MySQL数据库存储数据，包含以下表：

### movies表
- id: 电影ID（主键）
- title: 电影标题
- year: 发行年份
- director: 导演
- genre: 类型（逗号分隔的多个类型）
- rating: 平均评分
- poster_url: 海报图片URL
- description: 电影描述
- created_at: 创建时间

### users表
- id: 用户ID（主键）
- username: 用户名（唯一）
- password: 密码（MD5加密）
- email: 邮箱（唯一）
- created_at: 创建时间

### ratings表
- id: 评分ID（主键）
- user_id: 用户ID（外键）
- movie_id: 电影ID（外键）
- rating: 评分（0.5-5.0分，支持半星）
- comment: 评论
- timestamp: 时间戳（用于排序）
- created_at: 创建时间
- 约束: 每个用户对每部电影只能评分一次

### movie_embeddings表
- movie_id: 电影ID（主键，外键）
- embedding: 电影嵌入向量（TEXT格式，逗号分隔）
- 用途: 存储item2vec算法生成的电影向量，用于相似度计算

### user_embeddings表
- user_id: 用户ID（主键，外键）
- embedding: 用户嵌入向量（TEXT格式，逗号分隔）
- 用途: 存储用户偏好向量，用于个性化推荐

## 项目结构

```
MovieHonter_python/
├── app.py              # 主应用程序（Flask服务器）
├── init_db.py          # 数据库初始化脚本
├── schema.sql          # 数据库模式定义
├── requirements.txt    # Python依赖列表
├── data/               # 数据文件目录
│   ├── movies.csv      # 电影数据
│   ├── ratings.csv     # 评分数据
│   ├── links.csv       # 外部链接数据
│   ├── item2vecEmb.csv # 电影向量嵌入
│   └── userEmb.csv     # 用户向量嵌入
├── static/             # 静态文件（CSS、JS、图片）
│   ├── css/            # CSS样式文件
│   ├── js/             # JavaScript文件
│   ├── images/         # 图像资源
│   │   └── avatar/     # 用户头像
│   └── posters/        # 电影海报
└── templates/          # HTML模板
    ├── index.html      # 首页模板
    ├── movie.html      # 电影详情页模板
    └── user.html       # 用户页面模板
```

## 注意事项

- 默认端口为6010，可在app.py中修改
- 数据库用户名默认为"root"，密码通过交互方式输入
- 系统会自动创建名为"moviehunter"的数据库
- 使用的mysql-connector-python版本需为8.0.22或更高，以支持连接池功能
- 不用担心JavaScript中的模板语法警告，这些是正常的，因为Flask处理模板后才会将JavaScript发送到浏览器
- 系统采用单例模式管理数据库连接，确保资源优化
- 支持的图片格式：PNG, JPG, JPEG, GIF, WEBP，上传后自动转换为JPEG
- 海报图片会自动压缩到最大宽度300px，保持纵横比
- 评分系统支持0.5的倍数（如4.5分），数据库自动验证评分范围
- 推荐算法支持两种模式：传统类型匹配和智能嵌入向量计算
- 内存缓存机制：启动时将所有数据加载到内存，提高查询性能
- 密码使用MD5加密存储，会话使用随机密钥保护