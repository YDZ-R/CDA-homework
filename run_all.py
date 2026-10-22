"""Run the offline data, analysis, charts, dashboard and paper pipeline."""
from pathlib import Path
import subprocess
import sys
import os

root=Path(__file__).resolve().parent
stages=['01_load.py','02_clean.py','03_analysis.py','04_visuals.py','05_dashboard.py','06_paper.py','07_check.py']
for name in stages:
    print('\n运行',name,flush=True)
    executable=os.environ.get('CDA_DOCUMENT_PYTHON',sys.executable) if name=='06_paper.py' else sys.executable
    subprocess.run([executable,str(root/'scripts'/name)],cwd=root,check=True)
print('全部完成。大屏：outputs/dashboard/index.html；论文：docs/杭州酒店入住率分析与预测.docx')
