# MovieHunter PyInstaller 配置文件
# 此文件定义了打包MovieHunter为Windows可执行文件的详细配置

# 项目信息
APP_NAME = "MovieHunter"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "MovieHunter 电影推荐系统"
APP_AUTHOR = "MovieHunter Team"

# 打包配置
PACK_CONFIG = {
    # 基本设置
    "name": APP_NAME,
    "debug": False,
    "console": True,  # 显示控制台，便于查看启动信息
    "onedir": True,   # 创建文件夹形式的分发
    
    # 图标和版本信息
    "icon": "static/images/logo.ico",
    "version_file": "version_info.txt",
    
    # 优化设置
    "upx": True,      # 使用UPX压缩
    "clean": True,    # 清理临时文件
    "noconfirm": True,  # 不询问确认
    
    # 排除不必要的模块以减小体积
    "excludes": [
        "tkinter", "matplotlib", "scipy", "numpy.distutils",
        "PyQt5", "PyQt6", "PySide2", "PySide6",
        "jupyter", "notebook", "IPython",
        "pandas.plotting", "pandas.tests",
        "PIL.BdfFontFile", "PIL.CurImagePlugin", 
        "PIL.DcxImagePlugin", "PIL.EpsImagePlugin",
        "PIL.FitsStubImagePlugin", "PIL.FliImagePlugin",
        "PIL.FpxImagePlugin", "PIL.GbrImagePlugin",
        "PIL.GdImageFile", "PIL.ImImagePlugin",
        "PIL.IptcImagePlugin", "PIL.McIdasImagePlugin",
        "PIL.MicImagePlugin", "PIL.MpegImagePlugin",
        "PIL.PcdImagePlugin", "PIL.PixarImagePlugin",
        "PIL.PsdImagePlugin", "PIL.SgiImagePlugin",
        "PIL.SunImagePlugin", "PIL.TgaImagePlugin",
        "PIL.WalImageFile", "PIL.XVThumbImagePlugin",
        "PIL.XbmImagePlugin", "PIL.XpmImagePlugin",
    ],
    
    # 需要包含的数据文件
    "datas": [
        ("templates", "templates"),
        ("static", "static"), 
        ("data", "data"),
        ("schema.sql", "."),
        ("requirements.txt", "."),
        ("app.py", "."),
        ("init_db.py", "."),
        ("README.md", "."),
        ("Windows启动指南.md", "."),
    ],
    
    # 隐藏导入
    "hiddenimports": [
        "mysql.connector",
        "mysql.connector.pooling",
        "mysql.connector.connection",
        "mysql.connector.cursor",
        "PIL",
        "PIL.Image", 
        "PIL.ImageTk",
        "flask",
        "werkzeug",
        "jinja2",
        "markupsafe",
        "click",
        "itsdangerous",
        "hashlib",
        "secrets",
        "datetime",
        "decimal",
        "math",
        "collections",
        "getpass",
        "os",
        "json",
        "csv",
        "pathlib",
        "subprocess",
        "webbrowser",
        "time",
    ],
    
    # 收集所有子模块
    "collect_all": [
        "mysql.connector",
        "PIL",
        "flask",
        "werkzeug",
        "jinja2",
    ],
}

# 版本信息配置
VERSION_INFO = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
        StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 {APP_AUTHOR}'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'{APP_DESCRIPTION}'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
