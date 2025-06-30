# MovieHunter Windows 一键启动指南

## 🚀 超简单使用方法

**只需双击 `MovieHunter启动器.bat` 文件，然后按菜单提示操作即可！**

### 🔥 首次使用（1步搞定）
1. 双击 `完整安装向导.bat` - **终极一键安装，推荐所有用户**
2. 或双击 `MovieHunter启动器.bat`，选择 `0` → 🚀 一键初始化和启动

### ⚡ 传统方式（3步）
1. 双击 `MovieHunter启动器.bat`
2. 选择 `1` → 环境检查（确保Python和MySQL已安装）
3. 选择 `2` → 完整初始化（自动安装依赖、初始化数据库）

### 💨 日常使用（1步启动）
1. 双击 `MovieHunter启动器.bat`，选择 `3` → 快速启动

### 📦 EXE打包（分发给其他用户）
1. 双击 `MovieHunter启动器.bat`，选择 `8` → 打包为EXE文件
2. 等待打包完成，生成独立的可执行文件

## 🎯 新功能特色

### 🌟 自动镜像源配置
- **自动配置国内镜像源**，加速依赖包下载
- **支持多个镜像源**：清华、阿里云、豆瓣、华为云等
- **智能切换**：某个镜像源失败时自动尝试其他镜像源
- **一键配置**：专门的镜像源配置工具

### ⚡ 智能环境检测
- **自动检测**Python、pip、MySQL环境
- **自动启动**MySQL服务（如果已安装）
- **智能提示**：缺少组件时自动打开下载页面
- **彩色输出**：更清晰的状态显示

## 📁 文件说明

| 文件名 | 用途 | 适用场景 |
|--------|------|----------|
| `完整安装向导.bat` | **🌟 终极安装器** | **推荐所有用户，一步到位安装** |
| `MovieHunter启动器.bat` | **主启动器** | **功能齐全，包含所有工具** |
| `一键启动.bat` | **🚀 全自动启动器** | **快速部署，自动配置所有环境** |
| `打包exe.bat` | **📦 EXE打包工具** | **生成独立可执行文件** |
| `check_environment.bat` | 环境检查和安装指南 | 首次使用，检查系统环境 |
| `start_windows.bat` | 完整初始化和启动 | 首次使用或需要重新初始化 |
| `quick_start.bat` | 快速启动 | 日常使用，环境已配置好 |
| `pip镜像源配置.bat` | pip镜像源配置工具 | 配置加速下载的镜像源 |
| `测试镜像源速度.bat` | 镜像源速度测试 | 测试并选择最快的镜像源 |
| `troubleshoot.bat` | 故障排除工具 | 遇到问题时的诊断和修复 |
| `config_template.bat` | 配置文件模板 | 自定义数据库连接配置 |

## 🎉 推荐使用流程

### 🌟 超级简单方式（推荐所有用户）：
1. 双击 `完整安装向导.bat`
2. 按向导提示完成所有步骤
3. 自动安装Python、MySQL、配置环境、初始化数据库
4. 浏览器访问 http://localhost:6010

### 🔧 传统方式：
1. 双击 `check_environment.bat` → 检查并安装环境  
2. 双击 `start_windows.bat` → 完整初始化
3. 按提示输入MySQL密码
4. 等待初始化完成
5. 浏览器访问 http://localhost:6010

### ⚡ 日常使用：
1. 双击 `quick_start.bat` → 快速启动
2. 浏览器访问 http://localhost:6010

### 📦 生成EXE分发包：
1. 双击 `MovieHunter启动器.bat`
2. 选择 `8` → 打包为EXE文件
3. 等待打包完成，获得独立可执行程序
4. 可分发给没有Python环境的用户

## 测试账号

- **新用户测试账号**：test / 123456
- **历史用户账号**：user_1 / password

## 常见问题

### Q1: 提示Python未安装
**解决方案：**
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.7+版本
3. 安装时确保勾选"Add Python to PATH"

### Q2: 提示MySQL服务未运行
**解决方案：**
1. **推荐**：安装XAMPP (https://www.apachefriends.org/)
2. 启动XAMPP控制面板，点击MySQL的"Start"
3. 或者安装MySQL Server并启动服务

### Q3: 数据库连接失败
**解决方案：**
1. 确认MySQL服务正在运行
2. 检查MySQL用户名密码是否正确
3. 如使用XAMPP，默认用户名root，密码为空

### Q4: 端口被占用
**解决方案：**
1. 修改`app.py`中的端口号（默认6010）
2. 或结束占用端口的其他程序

### Q5: 依赖包安装失败
**解决方案：**
1. 使用 `pip镜像源配置.bat` 配置国内镜像源
2. 或手动使用镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
3. 检查网络连接
4. 尝试使用不同的镜像源（清华、阿里云、豆瓣等）

### Q6: pip下载速度慢
**解决方案：**
1. 双击 `pip镜像源配置.bat` 配置镜像源
2. 推荐使用清华大学镜像：https://pypi.tuna.tsinghua.edu.cn/simple
3. 或使用阿里云镜像：https://mirrors.aliyun.com/pypi/simple/

## 🌟 镜像源配置

### 支持的镜像源
- **清华大学**：https://pypi.tuna.tsinghua.edu.cn/simple （推荐）
- **阿里云**：https://mirrors.aliyun.com/pypi/simple/
- **豆瓣**：https://pypi.douban.com/simple/
- **中科大**：https://pypi.mirrors.ustc.edu.cn/simple/
- **华为云**：https://mirrors.huaweicloud.com/repository/pypi/simple/

### 手动配置方法
1. 运行 `pip镜像源配置.bat`
2. 选择合适的镜像源
3. 自动创建配置文件

### 临时使用镜像源
```bash
pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 高级配置

### 自定义数据库配置
1. 复制 `config_template.bat` 为 `config.bat`
2. 修改数据库连接参数
3. 运行启动脚本前先运行 `config.bat`

### 修改Web端口
在 `app.py` 文件末尾修改：
```python
app.run(host='0.0.0.0', port=6010, debug=False)
```

## 技术支持

如遇到问题：
1. 查看控制台错误信息
2. 检查MySQL服务状态
3. 确认Python和pip版本
4. 查看项目的完整README.md文件

## 注意事项

- 首次运行需要输入MySQL密码
- 确保防火墙允许6010端口访问
- 建议使用管理员权限运行（如需启动MySQL服务）
- 数据库初始化可能需要几分钟时间
