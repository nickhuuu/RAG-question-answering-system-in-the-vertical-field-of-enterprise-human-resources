from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境请改为特定前端地址）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有 Headers
)

from prompt_improve import upe_qa

from salary_analyse.langchain_script import salary_analyse

from final.addapi import analyze_video

from performance_analyse.analyse import analyze_performance

