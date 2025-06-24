# MovieHunter 电影推荐系统

MovieHunter是一个功能完善的基于Flask和MySQL的电影推荐系统，能够根据用户对电影的评分和喜好提供个性化的电影推荐。系统结合了协同过滤和基于内容的推荐算法，为用户提供精准的电影建议。

## 🌟 核心功能

### 用户系统
- **用户注册与登录**: 完整的用户认证系统，支持安全的密码加密
- **个性化用户页面**: 包含用户头像、评分历史、统计信息
- **会话管理**: 基于Flask Session的安全会话管理

### 电影浏览与管理
- **电影列表浏览**: 支持分页的电影列表展示
- **电影详情页面**: 详细的电影信息，包括海报、简介、评分等
- **电影分类筛选**: 按类型（动作、喜剧、科幻等）筛选电影
- **电影搜索功能**: 基于关键词的电影搜索
- **电影添加功能**: 注册用户可添加新电影，支持海报上传

### 推荐系统
- **个性化推荐**: 基于用户历史评分的协同过滤推荐
- **相似电影推荐**: 基于电影特征的内容推荐
- **多算法支持**: 集成多种推荐算法提高推荐质量
- **实时推荐**: 根据用户最新评分动态更新推荐结果

### 评分系统
- **电影评分**: 支持0.5-5.0分的精细化评分
- **评分历史**: 完整的用户评分记录和统计
- **评论功能**: 用户可对电影添加文字评论
- **评分统计**: 电影评分分布、平均分等统计信息

### 专题推荐
- **最新电影** (LATEST): 按年份排序的最新电影
- **高分电影** (TOP RATED): 评分最高的电影推荐
- **热门电影** (MOST COMMENTED): 评论最多的热门电影
- **评分分析**: 特定评分范围的用户评价查看

## 🛠️ 技术架构

### 后端技术
- **Python 3.6+**: 主要开发语言
- **Flask 2.0+**: Web应用框架
- **MySQL 8.0**: 关系型数据库
- **mysql-connector-python**: 数据库连接驱动

### 数据处理
- **NumPy**: 数值计算和向量操作
- **Pandas**: 数据处理和分析
- **PIL (Pillow)**: 图像处理和优化

### 前端技术
- **HTML5/CSS3**: 现代化响应式设计
- **JavaScript/jQuery**: 交互功能和AJAX请求
- **Bootstrap风格**: 美观的用户界面

### 部署技术
- **Docker**: 容器化部署
- **Docker Compose**: 多服务编排
- **健康检查**: 服务状态监控

## 📋 环境要求

### 推荐环境 (Docker)
- Docker 20.0+
- Docker Compose 2.0+
- 5GB 可用磁盘空间

### 传统环境
- Python 3.6+
- MySQL 8.0+
- 4GB+ 内存推荐

### Python依赖
```
flask>=2.0.0
numpy>=1.21.0
pandas>=1.3.0
mysql-connector-python>=8.0.22
pillow>=8.0.0
```

## � 快速开始

### 方式一：Docker 一键部署（推荐）

这是最简单快速的部署方式，适合所有用户：

#### 1. 环境准备
```bash
# 确保 Docker 和 Docker Compose 已安装
docker --version
docker-compose --version

# 确保 Docker 服务正在运行
docker info
```

#### 2. 克隆项目
```bash
git clone <your-repo-url>
cd SQL_HOMEWORK
```

#### 3. 一键部署
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

部署脚本会自动：
- ✅ 检查 Docker 环境
- ✅ 检查端口占用
- ✅ 构建应用镜像
- ✅ 启动 MySQL 服务
- ✅ 等待数据库就绪
- ✅ 初始化数据库和数据
- ✅ 启动 Web 应用
- ✅ 验证服务状态

#### 4. 访问应用
部署成功后，访问：**http://localhost:6010**

#### 5. 测试账号
```
测试账号：
- 用户名: test
- 密码: 123456

历史用户：
- 用户名: user_1, user_2, user_3...
- 密码: password
```

### 方式二：传统手动部署

适合开发环境或需要自定义配置的用户：

#### 1. 安装 MySQL
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
# 增加数据库连接池大小
# 在 app.py 中修改 pool_size 参数

# 启用数据库缓存
# 添加Redis缓存层（可选）
```

## 📈 扩展建议

### 短期扩展
- [ ] 添加电影评论点赞功能
- [ ] 实现用户关注系统
- [ ] 添加电影收藏夹功能
- [ ] 支持电影评分导出

### 中期扩展
- [ ] 集成外部电影数据API（TMDB、OMDB）
- [ ] 添加电影推荐邮件通知
- [ ] 实现多语言支持
- [ ] 添加管理员后台

### 长期扩展
- [ ] 机器学习推荐算法优化
- [ ] 实时协同过滤
- [ ] 大数据分析仪表板
- [ ] 微服务架构重构

## 🤝 贡献指南

### 开发环境设置
```bash
# 1. Fork 项目到你的GitHub
# 2. 克隆到本地
git clone https://github.com/your-username/MovieHunter.git

# 3. 创建开发分支
git checkout -b feature/your-feature-name

# 4. 使用Docker开发环境
docker-compose -f docker-compose.dev.yml up
```

### 代码规范
- 遵循PEP 8 Python代码规范
- 添加必要的注释和文档字符串
- 确保新功能有对应的测试用例
- 提交前运行代码格式检查

### 提交流程
```bash
# 1. 提交更改
git add .
git commit -m "feat: 添加新功能描述"

# 2. 推送到你的fork
git push origin feature/your-feature-name

# 3. 创建Pull Request
# 在GitHub上创建PR，详细描述你的更改
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与反馈

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **邮件**: your-email@example.com

---

## 📊 项目统计

- **核心代码**: 1200+ 行 Python
- **前端代码**: 900+ 行 CSS + 500+ 行 JavaScript  
- **数据库表**: 5个核心表
- **API接口**: 20+ RESTful接口
- **电影数据**: 支持10万+电影记录
- **用户评分**: 支持百万级评分数据
- **部署方式**: Docker + 传统部署双支持

**🎬 MovieHunter - 让电影推荐更智能，让观影体验更美好！**