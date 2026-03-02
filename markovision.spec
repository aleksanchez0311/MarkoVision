# -*- mode: python ; coding: utf-8 -*-
"""
MarkoVision PyInstaller Spec File
===================================
Para construir el exe ejecutar: pyinstaller markovision.spec
El exe abrira el dashboard automaticamente al ejecutarse.
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collect all data files from dependencies
dash_datas, dash_binaries, dash_hiddenimports = collect_all('dash')
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all('plotly')
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all('pandas')
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
hmmlearn_datas, hmmlearn_binaries, hmmlearn_hiddenimports = collect_all('hmmlearn')
sklearn_datas, sklearn_binaries, sklearn_hiddenimports = collect_all('sklearn')
scipy_datas, scipy_binaries, scipy_hiddenimports = collect_all('scipy')

# Collect additional data
plotly_data = collect_data_files('plotly')

block_cipher = None

# El exe abrira directamente el dashboard
a = Analysis(
    ['dashboard.py'],
    pathex=[],
    binaries=
        dash_binaries +
        plotly_binaries +
        pandas_binaries +
        numpy_binaries +
        hmmlearn_binaries +
        sklearn_binaries +
        scipy_binaries,
    datas=
        dash_datas +
        plotly_datas +
        plotly_data +
        pandas_datas +
        numpy_datas +
        hmmlearn_datas +
        sklearn_datas +
        scipy_datas +
        [('assets', 'assets')],
    hiddenimports=
        dash_hiddenimports +
        plotly_hiddenimports +
        pandas_hiddenimports +
        numpy_hiddenimports +
        hmmlearn_hiddenimports +
        sklearn_hiddenimports +
        scipy_hiddenimports +
        [
            'werkzeug',
            'jinja2',
            'markupsafe',
            'flask',
            'dash',
            'plotly',
            'pandas',
            'numpy',
            'hmmlearn',
            'scikit_learn',
            'scipy',
            'dateutil',
            'matplotlib',
            'sklearn',
            'lxml',
            'sqlalchemy',
            'tenacity',
            'flask_compress',
            'data_generator',
            'hmm_model',
        ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Ejecutar el dashboard directamente (no en modo consola)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MarkoVision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin consola - abre ventana gráfica
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un icono aquí
)
