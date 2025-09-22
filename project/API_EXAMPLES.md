# Text-to-Speech API Examples

## 📋 Available Endpoints

### 1. GET /config/templates
Lấy các mẫu cấu hình có sẵn

```bash
curl -X GET "http://localhost:8000/config/templates"
```

### 2. GET /config
Lấy cấu hình hiện tại

```bash
curl -X GET "http://localhost:8000/config"
```

### 3. POST /config
Cập nhật cấu hình (có thể config riêng lẻ hoặc kết hợp)

#### Chỉ config Text Generation:
```json
{
  "model": "gpt-3.5-turbo",
  "system_prompt": "You are a helpful assistant.",
  "model_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 100
  }
}
```

#### Chỉ config TTS:
```json
{
  "tts_parameters": {
    "voice": "alloy",
    "speed": 1.0,
    "provider": "openai"
  }
}
```

#### Config cả Text và TTS:
```json
{
  "model": "gpt-4o",
  "system_prompt": "You are a creative writing assistant.",
  "model_parameters": {
    "temperature": 1.2,
    "top_p": 0.95,
    "max_tokens": 500
  },
  "tts_parameters": {
    "voice": "nova",
    "speed": 1.1,
    "provider": "openai"
  }
}
```

#### Chỉ thay đổi model:
```json
{
  "model": "gemini-2.5-flash"
}
```

#### Chỉ thay đổi voice:
```json
{
  "tts_parameters": {
    "voice": "echo"
  }
}
```

### 4. POST /generate/text (Form Data)
Generate text từ prompt với support file upload và streaming

#### Basic Text Generation:
```bash
curl -X POST "http://localhost:8000/generate/text" \
  -F "prompt=Viết một câu chuyện ngắn về robot" \
  -F "max_tokens=200" \
  -F "stream=false"
```

#### Text Generation với File Upload:
```bash
curl -X POST "http://localhost:8000/generate/text" \
  -F "prompt=Tóm tắt nội dung trong file đính kèm" \
  -F "max_tokens=500" \
  -F "stream=false" \
  -F "files=@document.pdf" \
  -F "files=@report.docx"
```

#### Streaming Response:
```bash
curl -X POST "http://localhost:8000/generate/text" \
  -F "prompt=Viết một bài văn dài về AI" \
  -F "max_tokens=1000" \
  -F "stream=true"
```

#### Phân tích ảnh với OCR:
```bash
curl -X POST "http://localhost:8000/generate/text" \
  -F "prompt=Mô tả và phân tích nội dung trong ảnh" \
  -F "max_tokens=300" \
  -F "files=@screenshot.png"
```

**Supported File Types:**
- **PDF**: `.pdf` (text extraction)
- **Word**: `.docx`, `.doc` (text extraction)
- **Text**: `.txt` (plain text)
- **Images**: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff` (OCR text extraction)

### 5. POST /tts
Convert text to speech

```json
{
  "text": "Xin chào, đây là ví dụ text to speech",
  "voice": "alloy",
  "speed": 1.0,
  "provider": "openai"
}
```

## 🔧 Parameter Descriptions

### Model Parameters:
- **temperature** (0.0-2.0): Độ sáng tạo - cao hơn = sáng tạo hơn
- **top_p** (0.0-1.0): Nucleus sampling - thấp hơn = tập trung hơn
- **max_tokens** (1-8192): Số token tối đa cho response

### TTS Parameters:
- **voice**: alloy, echo, fable, onyx, nova, shimmer
- **speed** (0.25-4.0): Tốc độ đọc
- **provider**: openai, google, gemini

## 🎯 Usage Tips

1. **Flexible Configuration**:
   - Chỉ config text: bỏ qua `tts_parameters`
   - Chỉ config TTS: bỏ qua `model` và `model_parameters`
   - Config từng phần: chỉ gửi field muốn thay đổi

2. **Tuning parameters**:
   - Creative writing: temperature cao (1.0-1.5)
   - Technical content: temperature thấp (0.1-0.5)
   - Balanced: temperature medium (0.7-0.9)

3. **TTS optimization**:
   - Formal content: voice "echo", speed 0.9
   - Casual content: voice "alloy", speed 1.0
   - Expressive: voice "nova", speed 1.1

4. **Templates available**:
   - `text_only_basic`, `text_only_creative`, `text_only_technical`
   - `tts_only_basic`, `tts_only_expressive`, `tts_only_formal`
   - `complete_config` (cả text và TTS)

5. **File Processing Features**:
   - **Multi-file upload**: Có thể upload nhiều file cùng lúc
   - **Smart extraction**: Tự động detect file type và extract text
   - **OCR support**: Extract text từ ảnh và scanned documents
   - **Error handling**: Graceful handling nếu file không đọc được

6. **Streaming Benefits**:
   - **Real-time response**: Nhận output ngay khi model generate
   - **Better UX**: Không phải chờ toàn bộ response
   - **Professional**: Giống ChatGPT, Claude interface
   - **SSE format**: Server-Sent Events cho web integration

## 🐛 Error Handling

API sẽ trả về error nếu:
- Parameters ngoài range cho phép
- Model name không hợp lệ
- JSON format sai
- API keys chưa được cấu hình

Example error response:
```json
{
  "detail": "Config update failed: temperature must be between 0.0 and 2.0"
}
```