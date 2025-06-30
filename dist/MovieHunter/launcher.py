import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

def setup_environment():
    """设置运行环境"""
    # 确保当前目录是exe所在目录
    if getattr(sys, 'frozen', False):
        # 运行在PyInstaller打包的exe中
        base_dir = Path(sys.executable).parent
    else:
        # 运行在Python脚本中
        base_dir = Path(__file__).parent
    
    os.chdir(base_dir)
    return base_dir

def check_mysql():
    """检查MySQL服务状态"""
    try:
        # Windows下检查MySQL服务
        result = subprocess.run(['sc', 'query', 'mysql'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'RUNNING' in result.stdout:
            return True
        return False
    except:
        return False

def start_mysql():
    """尝试启动MySQL服务"""
    try:
        result = subprocess.run(['net', 'start', 'mysql'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_database_init():
    """检查数据库是否已初始化"""
    init_file = Path('db_initialized.flag')
    return init_file.exists()

def main():
    print("=" * 60)
    print("🎬 MovieHunter 电影推荐系统")
    print("=" * 60)
    print()
    
    # 设置环境
    base_dir = setup_environment()
    print(f"📁 工作目录: {base_dir}")
    
    # 检查MySQL
    print("🔍 检查MySQL服务状态...")
    if not check_mysql():
        print("⚠️  MySQL服务未运行，尝试启动...")
        if start_mysql():
            print("✅ MySQL服务启动成功")
        else:
            print("❌ MySQL服务启动失败")
            print()
            print("请手动启动MySQL服务：")
            print("1. 如果使用XAMPP，请启动XAMPP控制面板并启动MySQL")
            print("2. 如果使用MySQL服务，请以管理员权限运行命令：net start mysql")
            print("3. 或者在服务管理器中启动MySQL服务")
            print()
            input("按回车键继续...")
    else:
        print("✅ MySQL服务正在运行")
    
    # 检查数据库初始化
    if not check_database_init():
        print()
        print("🔧 检测到数据库尚未初始化")
        choice = input("是否现在初始化数据库？(y/N): ").lower()
        if choice == 'y':
            print("正在初始化数据库...")
            try:
                # 运行数据库初始化
                result = subprocess.run([sys.executable, 'init_db.py'], 
                                      cwd=base_dir)
                if result.returncode == 0:
                    # 创建初始化标记文件
                    Path('db_initialized.flag').touch()
                    print("✅ 数据库初始化完成")
                else:
                    print("⚠️  数据库初始化可能失败，但继续启动应用")
            except Exception as e:
                print(f"❌ 数据库初始化失败: {e}")
                print("请手动运行🔧初始化数据库.bat")
    
    print()
    print("🚀 启动MovieHunter应用...")
    print("请稍候，首次启动可能需要30秒到1分钟...")
    
    try:
        # 导入并启动Flask应用
        from app import app, DatabaseManager
        
        # 初始化数据库管理器
        db_manager = DatabaseManager.get_instance()
        
        print()
        print("=" * 60)
        print("🎉 MovieHunter启动成功！")
        print("=" * 60)
        print()
        print("📱 访问地址：http://localhost:6010")
        print()
        print("👤 测试账号：")
        print("   用户名: test")
        print("   密码:   123456")
        print()
        print("💡 提示：")
        print("   - 按 Ctrl+C 停止应用")
        print("   - 关闭此窗口也会停止应用")
        print("=" * 60)
        
        # 等待2秒后自动打开浏览器
        time.sleep(2)
        try:
            webbrowser.open('http://localhost:6010')
            print("🌐 已自动打开浏览器")
        except:
            print("⚠️  无法自动打开浏览器，请手动访问：http://localhost:6010")
        
        print()
        print("应用正在运行中...")
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=6010, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 用户主动停止应用")
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        print("\n可能的解决方案：")
        print("1. 确保MySQL服务正在运行")
        print("2. 检查端口6010是否被占用")
        print("3. 确保数据库已正确初始化")
        print("4. 检查防火墙设置")
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()
