# Big Chatbot Scaffold

Dự án này là khung sẵn cho một chatbot **RAG** với API, DB, ingest pipeline, retrieval chatbot và góc finetune để chuẩn bị dữ liệu huấn luyện.

---

## Tính năng

- **FastAPI**: Cung cấp REST API cho ingest dữ liệu và chatbot.
- **PostgreSQL + pgvector**: Lưu embedding và truy vấn nearest neighbors.
- **RAG Pipeline**:
  - **Ingest**: Chunk tài liệu, sinh embedding, lưu vào DB.
  - **Chat**: Lấy top-k chunk liên quan, xây prompt, gọi LLM.
- **Config tách biệt**: `.env` để dễ cấu hình.
- **Finetune**: Công cụ chuẩn bị dữ liệu QA từ log để huấn luyện LoRA hoặc các mô hình nhỏ.

---

## Cấu trúc thư mục

```text
big-chatbot/
  src/app/
    api/         # FastAPI routes: /ingest, /chat
    core/        # config Settings (pydantic-settings)
    db/          # models, session, init_db
    rag/         # glue/pipeline RAG (mở rộng về sau)
    services/    # chunker, providers (Strategy), repository, ingest & retrieve
  src/scripts/   # load_docs.py (ingest folder)
  finetune/      # README + prepare_qa.py
  data/          # để tài liệu mẫu
  docker-compose.yml
  requirements.txt
  .env.example
  README.md
```
