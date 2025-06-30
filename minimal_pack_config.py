# MovieHunter 精简打包配置
# 专门用于减小EXE文件体积的优化配置

import os
import sys

APP_NAME = "MovieHunter"
APP_VERSION = "1.0.0"

# 精简打包配置 - 专注于减小体积
MINIMAL_PACK_CONFIG = {
    "name": APP_NAME,
    "debug": False,
    "console": True,
    "onedir": True,
    "clean": True,
    "noconfirm": True,
    
    # 严格排除不必要的大型库
    "excludes": [
        # GUI 框架 (不需要)
        "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "wx",
        
        # 科学计算的非必要部分
        "matplotlib", "matplotlib.pyplot", "matplotlib.backends",
        "scipy", "scipy.sparse", "scipy.stats", "scipy.optimize",
        "numpy.distutils", "numpy.f2py", "numpy.testing",
        
        # 机器学习库 (项目不需要)
        "sklearn", "scikit-learn", "torch", "tensorflow", "keras",
        "transformers", "huggingface_hub", "tokenizers",
        
        # NLP和向量搜索库 (项目不需要)
        "jieba", "faiss", "faiss_cpu", "sentence_transformers",
        
        # 大数据处理库 (项目不需要)
        "pyarrow", "fastparquet", "tables", "h5py",
        
        # 开发和测试工具
        "pytest", "unittest", "doctest", "pdb", "profile",
        "jupyter", "notebook", "IPython", "ipykernel",
        
        # 网络和异步库的非必要部分
        "asyncio", "aiohttp", "websockets", "grpc",
        
        # 数据库的非必要部分
        "sqlite3", "psycopg2", "pymongo", "sqlalchemy",
        
        # 图像处理的非必要部分
        "PIL.ImImagePlugin", "PIL.PcdImagePlugin", "PIL.PcxImagePlugin",
        "PIL.PdfImagePlugin", "PIL.PixarImagePlugin", "PIL.PpmImagePlugin",
        "PIL.PsdImagePlugin", "PIL.SgiImagePlugin", "PIL.SpiderImagePlugin",
        "PIL.SunImagePlugin", "PIL.TgaImagePlugin", "PIL.TiffImagePlugin",
        "PIL.WmfImagePlugin", "PIL.XVThumbImagePlugin", "PIL.XbmImagePlugin",
        "PIL.XpmImagePlugin", "PIL.BdfFontFile", "PIL.CurImagePlugin",
        "PIL.DcxImagePlugin", "PIL.EpsImagePlugin", "PIL.FitsStubImagePlugin",
        "PIL.FliImagePlugin", "PIL.FpxImagePlugin", "PIL.GbrImagePlugin",
        "PIL.GdImageFile", "PIL.IptcImagePlugin", "PIL.McIdasImagePlugin",
        "PIL.MicImagePlugin", "PIL.MpegImagePlugin", "PIL.WalImageFile",
        
        # Pandas的非必要部分
        "pandas.plotting", "pandas.tests", "pandas.io.excel",
        "pandas.io.stata", "pandas.io.sas", "pandas.io.spss",
        
        # 其他大型库
        "zmq", "pyzmq", "tornado", "bokeh", "plotly",
        "sympy", "dask", "numba", "cython",
    ],
    
    # 只包含必要的数据文件
    "datas": [
        ("templates", "templates"),
        ("static/css", "static/css"),
        ("static/js", "static/js"), 
        ("static/images/logo.ico", "static/images"),
        ("static/images/logo.png", "static/images"),
        ("static/images/default-poster.jpg", "static/images"),
        ("data/movies.csv", "data"),
        ("data/ratings.csv", "data"),
        ("data/links.csv", "data"),
        ("schema.sql", "."),
        ("requirements.txt", "."),
        ("app.py", "."),
        ("init_db.py", "."),
    ],
    
    # 只导入必要的模块
    "hiddenimports": [
        # 数据库连接 (必需)
        "mysql.connector",
        "mysql.connector.pooling",
        "mysql.connector.connection",
        
        # Web框架核心 (必需)
        "flask",
        "werkzeug.serving",
        "werkzeug.utils",
        "jinja2.ext",
        
        # 图像处理核心 (必需)
        "PIL.Image",
        "PIL.ImageOps",
        
        # 基础库 (必需)
        "hashlib", "secrets", "datetime", "decimal",
        "os", "sys", "pathlib", "json", "csv",
        "collections", "math", "getpass",
        "subprocess", "webbrowser", "time",
        
        # 数据处理核心 (必需)
        "numpy.core", "numpy.random",
        "pandas.core", "pandas.io.parsers",
    ],
    
    # 不收集额外的子模块
    "collect_all": [],
}

def get_minimal_pyinstaller_command():
    """生成精简的PyInstaller命令"""
    cmd_parts = [
        "pyinstaller",
        "--onedir",
        "--console", 
        "--name", "MovieHunter",
        "--clean",
        "--noconfirm",
    ]
    
    # 添加排除项
    for exclude in MINIMAL_PACK_CONFIG["excludes"]:
        cmd_parts.extend(["--exclude-module", exclude])
    
    # 添加数据文件
    for src, dst in MINIMAL_PACK_CONFIG["datas"]:
        if os.path.exists(src):
            cmd_parts.extend(["--add-data", f"{src};{dst}"])
    
    # 添加隐藏导入
    for hidden in MINIMAL_PACK_CONFIG["hiddenimports"]:
        cmd_parts.extend(["--hidden-import", hidden])
    
    # 添加启动文件
    cmd_parts.append("launcher.py")
    
    return cmd_parts

if __name__ == "__main__":
    cmd = get_minimal_pyinstaller_command()
    print("Minimal PyInstaller command:")
    print(" ".join(cmd))
