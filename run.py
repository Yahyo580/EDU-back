# Serverni ishga tushirish uchun oddiy fayl.
#   python run.py
# yoki:
#   uvicorn app.server:app --reload
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True)
