# SQL_HOMEWORK

MovieHunter是一个基于Flask和MySQL的电影推荐系统，能够根据用户对电影的评分和喜好提供个性化的电影推荐。系统结合了协同过滤和基于内容的推荐算法，为用户提供精准的电影建议。

## 目前实现的功能

- 浏览电影列表与详情
- 按类型筛选电影
- 基于用户历史评分的个性化电影推荐
- 发现与特定电影相似的其他影片
- 浏览最新上映的电影
- 查看评分最高的电影
- 查看评论最多的热门电影
- 用户个人资料页面，包括个性化头像和评分历史
- 完整的导航菜单，支持全站快速访问
- 搜索功能，允许用户根据关键词查找电影
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
- **数据库**: MySQL 8.0+, mysql-connector-python (连接池)
- **数据处理**: NumPy, Pandas
- **前端**: HTML, CSS, JavaScript, jQuery
- **图像处理**: PIL (Pillow) - 海报图片压缩和格式转换
- **安全**: hashlib (MD5密码加密), secrets (会话密钥生成)
- **数据分析**: 协同过滤算法, 基于内容的推荐算法, item2vec嵌入向量
- **架构模式**: 单例模式, MVC架构, 数据访问对象模式

## 环境要求

- Docker 20.0+
- Docker Compose 2.0+
- Python 3.6+
- MySQL 8.0+
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

### 方式一：Docker 一键部署

这是最简单快速的部署方式

#### 1. 环境准备
```bash
# 确保 Docker 和 Docker Compose 已安装
docker --version
docker compose --version

# 确保 Docker 服务正在运行
docker info
```

#### 2. 克隆项目
```bash
git clone https://github.com/yalishiduozhang/SQL_HOMEWORK
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
- 检查 Docker 环境
- 检查端口占用
- 构建应用镜像
- 启动 MySQL 服务
- 等待数据库准备就绪
- 初始化数据库和数据
- 启动 Web 应用
- 验证服务状态

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

### 方式二：Windows EXE 打包部署

这种方式适合需要分发给没有Python环境的Windows用户，生成独立的可执行文件。

#### 🎯 体积优化说明
原始打包后体积约为**457MB**，通过优化可减少到**100MB以内**（减少70-80%）。

详见：[EXE打包体积优化指南.md](EXE打包体积优化指南.md)

#### 1. 环境准备
- Windows 操作系统
- Python 3.7+ 已安装
- 项目依赖已安装（`pip install -r requirements.txt`）
- PyInstaller 打包工具

#### 2. 安装打包工具
```bash
pip install pyinstaller
```

#### 3. 执行打包
使用项目提供的打包脚本：

**方式A：使用精简版打包脚本（强烈推荐 - 体积减少73%）**
```bash
# 运行精简版打包脚本，体积从457MB减少到约100MB
minimal_build_exe.bat
```

**方式B：使用修复版打包脚本（推荐 - 体积减少50%）**
```bash
# 运行修复版打包脚本，体积减少约50%
fix_build_exe.bat
```

**方式C：使用英文版打包脚本（基础版）**
```bash
# 运行英文版打包脚本（避免中文编码问题）
build_exe.bat
```

**方式D：使用spec文件打包（高级用户）**
```bash
# 使用精简配置spec文件
pyinstaller moviehunter_minimal.spec
```

**方式E：手动打包命令（自定义）**
```bash
pyinstaller --onedir --console --name "MovieHunter" \
    --add-data "app.py;." \
    --add-data "launcher.py;." \
    --add-data "init_db.py;." \
    --add-data "templates;templates" \
    --add-data "static;static" \
    --add-data "data;data" \
    --add-data "schema.sql;." \
    --add-data "requirements.txt;." \
    --hidden-import "mysql.connector" \
    --hidden-import "PIL" \
    --hidden-import "flask" \
    --hidden-import "numpy" \
    --hidden-import "pandas" \
    --noconfirm \
    launcher.py
```

#### 4. 打包结果
打包完成后，在 `dist\MovieHunter\` 文件夹中会生成：
- `MovieHunter.exe` - 主程序
- `Start_MovieHunter.bat` - 启动脚本
- `Debug_MovieHunter.bat` - 调试脚本
- `_internal\` - 依赖文件夹（包含所有必要文件）

#### 5. 分发说明
- 将整个 `dist\MovieHunter` 文件夹打包分发
- 用户需要安装MySQL并启动服务
- 双击 `Start_MovieHunter.bat` 即可运行
- 首次运行会自动引导数据库初始化

#### 6. EXE版本特点
- **无需Python环境**：可在任何Windows机器上运行
- **文件大小**：约4-5GB（包含完整Python运行时）
- **启动时间**：首次启动可能需要30秒-1分钟
- **系统要求**：Windows 7/8/10/11，4GB+ 内存

### 方式三：手动部署
#### 1. 安装MySQL

##### Windows
1. 下载并安装MySQL：https://dev.mysql.com/downloads/installer/
2. 安装过程中设置root用户密码（请记住此密码）
3. 确保MySQL服务已启动

##### macOS
```bash
brew install mysql
brew services start mysql
```

##### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

#### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

如果遇到mysql-connector-python没有pooling模块的错误，请尝试：
```bash
pip uninstall mysql-connector-python
pip install mysql-connector-python>=8.0.22
```

#### 3. 初始化数据库

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

#### 4. 运行应用程序

```bash
python app.py
```

1. 按提示输入MySQL数据库密码
2. 然后在浏览器中访问：http://localhost:6010

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
├── docker-init.py      # Docker环境初始化
├── schema.sql          # 数据库模式定义
├── requirements.txt    # Python依赖列表
├── deploy.sh           # 一键部署脚本
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # 生产环境
├── docker-compose.dev.yml  # 开发环境
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
    ├── user.html       # 用户页面模板
    ├── login.html      # 登录页面
    ├── register.html   # 注册页面
    └── add_movie.html  # 添加电影页面
```

## 注意事项

- 默认端口为6010，可在app.py中修改
- Docker部署时MySQL的用户名和密码需要在.env中修改
- 手动部署数据库用户名默认为"root"，密码通过交互方式输入
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
