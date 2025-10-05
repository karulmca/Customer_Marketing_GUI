# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller Specification File for Company Data Scraper
Creates a single executable file with all dependencies bundled
"""

import os
from pathlib import Path

# Get the application directory
app_dir = Path(os.getcwd())

# Define data files and directories to include
data_files = [
    # Configuration files
    ('config.json', '.'),
    ('database_config', 'database_config'),
    ('auth', 'auth'),
    ('gui', 'gui'),
    ('scrapers', 'scrapers'),
    ('utilities', 'utilities'),
    
    # Documentation
    ('README.md', '.'),
    ('AUTHENTICATION_GUIDE.md', '.'),
    ('USER_REGISTRATION_GUIDE.md', '.'),
    
    # Templates
    ('templates', 'templates'),
]

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'psycopg2',
    'pandas',
    'openpyxl',
    'xlsxwriter',
    'requests',
    'selenium',
    'webdriver_manager',
    'beautifulsoup4',
    'python-dotenv',
    'bcrypt',
    'sqlalchemy',
    'concurrent.futures',
    'threading',
    'queue',
    'json',
    'hashlib',
    'uuid',
    'datetime',
    'logging',
    'pathlib',
    'subprocess',
    'tempfile',
    'os',
    'sys',
    'time',
    're',
    'urllib',
    'ssl',
    'socket',
    'email',
    'smtplib',
    # Database config modules
    'database_config',
    'database_config.db_utils',
    'database_config.file_upload_processor',
    'database_config.setup_database',
    # Auth modules
    'auth',
    'auth.user_auth',
    'auth.file_processing_bridge',
    # GUI modules
    'gui',
    'gui.login_gui',
    'gui.file_upload_json_gui',
    # Other modules
    'enhanced_scheduled_processor',
    'scheduled_processor',
]

a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.testing',
        'pytest',
        'jupyter',
        'IPython',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CompanyDataScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)