# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：生成单文件 exe。

使用方式（在项目根目录执行）：
    python -m PyInstaller app.spec --noconfirm
"""
from PyInstaller.utils.hooks import collect_data_files

# 需要随程序一起打包的资源
datas = [("app/ui/styles.qss", "app/ui")]
datas += collect_data_files("matplotlib")

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "rapidfuzz.distance",
        "matplotlib.backends.backend_qtagg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # 排除未使用的 GUI/交互后端与重型 Qt 模块，压缩体积
    excludes=[
        "tkinter", "PyQt5", "PyQt6", "PySide2", "IPython",
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineQuick", "PySide6.QtWebChannel",
        "PySide6.QtWebSockets", "PySide6.QtQml", "PySide6.QtQuick",
        "PySide6.QtQuickWidgets", "PySide6.QtQuick3D", "PySide6.Qt3DCore",
        "PySide6.Qt3DRender", "PySide6.Qt3DExtras", "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets", "PySide6.QtPdf", "PySide6.QtPdfWidgets",
        "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtSql",
        "PySide6.QtTest", "PySide6.QtBluetooth", "PySide6.QtNfc",
        "PySide6.QtPositioning", "PySide6.QtLocation", "PySide6.QtSerialPort",
        "PySide6.QtSensors", "PySide6.QtDesigner", "PySide6.QtHelp",
        "PySide6.QtOpenGL", "PySide6.QtOpenGLWidgets",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WordMemorySystem",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)