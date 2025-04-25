# SQL_HOMEWORK

MovieHunter是一个基于Flask和MySQL的电影推荐系统，能够根据用户对电影的评分和喜好提供个性化的电影推荐。系统结合了协同过滤和基于内容的推荐算法，为用户提供精准的电影建议。

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

## 我们目前用到的技术

- **后端**: Python 3.6+, Flask
- **数据库**: MySQL 5.7+
- **数据处理**: NumPy, Pandas
- **前端**: HTML, CSS, JavaScript, jQuery
- **数据分析**: 协同过滤算法, 基于内容的推荐算法

## 环境要求

- Python 3.6+
- MySQL 5.7+
- Flask
- NumPy
- Pandas
- mysql-connector-python (8.0.22+)

## 安装步骤

### 1. 安装MySQL

#### Windows
1. 下载并安装MySQL：https://dev.mysql.com/downloads/installer/
2. 安装过程中设置root用户密码（请记住此密码）
3. 确保MySQL服务已启动

#### macOS
```bash
brew install mysql
brew services start mysql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

如果遇到mysql-connector-python没有pooling模块的错误，请尝试：
```bash
pip uninstall mysql-connector-python
pip install mysql-connector-python>=8.0.22
```

### 3. 初始化数据库

1. 确保MySQL服务已启动
2. 如果之前已经初始化过数据库，建议重新初始化以确保结构一致：
   ```sql
   DROP DATABASE IF EXISTS moviehunter;
   ```
3. 运行初始化脚本：

```bash
python init_db.py
```

4. 按提示输入MySQL数据库密码
5. 等待系统完成数据库创建和示例数据导入

### 4. 运行应用程序

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
- rating: 评分（1-5分）
- comment: 评论
- timestamp: 时间戳（用于排序）
- created_at: 创建时间

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