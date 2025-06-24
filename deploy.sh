#!/bin/bash

# MovieHunter Docker 部署脚本
# 如果任何命令失败，脚本将退出
set -e

# 当脚本意外退出时的清理函数
cleanup() {
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 部署过程中发生错误"
        echo "💡 可以尝试以下命令进行故障排除："
        echo "   - 查看所有容器状态: docker-compose ps"
        echo "   - 查看所有服务日志: docker-compose logs"
        echo "   - 停止所有服务: docker-compose down"
    fi
}
trap cleanup EXIT

echo "======================================"
echo "MovieHunter Docker 部署脚本"
echo "======================================"

# 检查 Docker 和 Docker Compose 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"

# 检查 Docker 守护进程是否运行
echo ""
echo "🔍 检查 Docker 服务状态..."
if ! docker info &> /dev/null; then
    echo "❌ Docker 守护进程未运行，请启动 Docker"
    echo "💡 提示："
    echo "   - macOS: 启动 Docker Desktop 应用"
    echo "   - Linux: sudo systemctl start docker"
    echo "   - Windows: 启动 Docker Desktop"
    exit 1
fi

echo "✅ Docker 守护进程正在运行"

# 检查端口是否被占用
echo ""
echo "🔍 检查端口占用情况..."
if netstat -an 2>/dev/null | grep -q ":6010.*LISTEN" || lsof -i :6010 2>/dev/null | grep -q LISTEN; then
    echo "⚠️  端口 6010 已被占用"
    echo "💡 请检查是否有其他 MovieHunter 实例正在运行"
    echo "💡 或者修改 docker-compose.yml 中的端口配置"
    read -p "是否要停止现有服务并继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 1
    fi
    echo "🛑 停止现有服务..."
    docker-compose down 2>/dev/null || true
fi

if netstat -an 2>/dev/null | grep -q ":3306.*LISTEN" || lsof -i :3306 2>/dev/null | grep -q LISTEN; then
    echo "⚠️  端口 3306 已被占用"
    echo "💡 请确保没有其他 MySQL 实例在运行"
    echo "💡 或者修改 docker-compose.yml 中的 MySQL 端口配置"
fi

# 检查数据文件是否存在
if [ ! -f "data/movies.csv" ]; then
    echo "⚠️  警告: data/movies.csv 不存在，应用可能无法正常工作"
fi

if [ ! -f "data/ratings.csv" ]; then
    echo "⚠️  警告: data/ratings.csv 不存在，应用可能无法正常工作"
fi

# 构建和启动服务
echo ""
echo "🔨 构建 Docker 镜像..."
if ! docker-compose build; then
    echo "❌ Docker 镜像构建失败"
    exit 1
fi

echo ""
echo "🚀 启动 MySQL 服务..."
if ! docker-compose up -d mysql; then
    echo "❌ MySQL 服务启动失败"
    exit 1
fi

echo ""
echo "⏳ 等待 MySQL 服务就绪..."
# 更可靠的等待方式：检查 MySQL 健康状态
echo "检查 MySQL 容器健康状态..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker-compose ps mysql | grep -q "(healthy)"; then
        echo "✅ MySQL 服务已就绪"
        break
    elif docker-compose ps mysql | grep -q "(unhealthy)"; then
        echo "❌ MySQL 服务启动失败"
        echo "💡 查看错误日志: docker-compose logs mysql"
        exit 1
    else
        echo "等待中... ($((attempt + 1))/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ MySQL 服务启动超时"
    echo "💡 查看错误日志: docker-compose logs mysql"
    exit 1
fi

echo ""
echo "📊 初始化数据库数据..."
if ! docker-compose --profile init run --rm init-data; then
    echo "❌ 数据库初始化失败"
    echo "💡 查看错误日志: docker-compose logs"
    exit 1
fi

echo ""
echo "🌐 启动 Web 应用..."
if ! docker-compose up -d web; then
    echo "❌ Web 应用启动失败"
    echo "💡 查看错误日志: docker-compose logs web"
    exit 1
fi

echo ""
echo "🔍 验证服务状态..."
sleep 5  # 给应用一些启动时间

# 检查容器是否正在运行
if ! docker-compose ps | grep -q "moviehunter_web.*Up"; then
    echo "❌ Web 应用容器未正常运行"
    echo "💡 查看容器状态: docker-compose ps"
    echo "💡 查看错误日志: docker-compose logs web"
    exit 1
fi

# 检查端口是否可访问
echo "检查应用端口连通性..."
max_attempts=15
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:6010 > /dev/null 2>&1; then
        echo "✅ Web 应用已就绪并可访问"
        break
    else
        echo "等待应用启动... ($((attempt + 1))/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  应用可能需要更多时间启动，请稍后访问"
    echo "💡 手动检查: curl http://localhost:6010"
fi

echo ""
echo "======================================"
echo "✅ 部署完成！"
echo ""
echo "🌍 应用访问地址: http://localhost:6010"
echo "🗄️  MySQL 访问地址: localhost:3306"
echo ""
echo "📋 可用账号："
echo "   测试账号 - 用户名: test, 密码: 123456"
echo "   历史用户 - 密码: password"
echo ""
echo "🛠️  管理命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo "   清理数据: docker-compose down -v"
echo "======================================"
