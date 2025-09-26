# Audio Files Service Guide

## Tổng quan

Service này cung cấp khả năng quản lý và truy cập các file audio được tạo ra bởi hệ thống NotebookLM automation.

## API Endpoints

### 1. Liệt kê tất cả files
```
GET /api/audio/files
```
**Response:**
```json
[
  {
    "name": "filename.mp4",
    "size": 26371895,
    "size_mb": 25.15,
    "modified": "2025-01-21T10:30:00.000Z",
    "mime_type": "video/mp4",
    "is_audio": true,
    "download_url": "/api/audio/download/filename.mp4"
  }
]
```

### 2. Download file cụ thể
```
GET /api/audio/download/{filename}
```
**Response:** File binary data

### 3. Xóa file
```
DELETE /api/audio/files/{filename}
```
**Response:**
```json
{
  "message": "File 'filename.mp4' deleted successfully"
}
```

### 4. Thống kê thư mục
```
GET /api/audio/stats
```
**Response:**
```json
{
  "total_files": 2,
  "audio_files": 1,
  "total_size_bytes": 26372476,
  "total_size_mb": 25.15,
  "file_types": {
    ".mp4": 1,
    ".txt": 1
  },
  "directory": "/path/to/audio_downloads"
}
```

### 5. Dọn dẹp files cũ
```
POST /api/audio/cleanup?days=7
```
**Response:**
```json
{
  "message": "Cleanup completed",
  "deleted_files": ["old_file1.mp4", "old_file2.mp4"],
  "count": 2
}
```

## Web Interface

### Truy cập
- Mở trình duyệt và vào `http://localhost:3000`
- Click vào tab "🎵 Audio Files"

### Tính năng
1. **Xem danh sách files:** Hiển thị tất cả files với metadata
2. **Download:** Click nút "⬇️ Download" để tải file
3. **Preview audio:** Nghe trực tiếp audio files với built-in player
4. **Xóa files:** Click nút "🗑️ Delete" để xóa file
5. **Thống kê:** Xem tổng số files, dung lượng
6. **Dọn dẹp:** Xóa files cũ hơn 7 ngày

### Screenshots/UI Features
- 🎵 Icon để phân biệt audio files
- Responsive design cho mobile
- File size hiển thị dễ đọc (MB, KB)
- Timestamp cho mỗi file
- Built-in audio player
- Confirmation dialog khi xóa

## Cấu hình

### Thư mục lưu trữ
```
C:\Users\Hi\text_to_speech\project\src\static\audio_downloads\
```

### CORS settings
Frontend có thể truy cập từ:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## Bảo mật

1. **Path traversal protection:** API kiểm tra file path để tránh truy cập file ngoài thư mục audio_downloads
2. **File type validation:** Xác định MIME type cho mỗi file
3. **Error handling:** Xử lý lỗi gracefully với HTTP status codes phù hợp

## Troubleshooting

### API không hoạt động
```bash
# Kiểm tra server có chạy không
curl http://localhost:8000/health

# Test audio endpoint
curl http://localhost:8000/api/audio/files
```

### Frontend không hiển thị files
1. Kiểm tra console browser có lỗi CORS không
2. Xác nhận API_URL trong frontend config
3. Kiểm tra network tab trong dev tools

### Thư mục không tồn tại
Service sẽ tự động tạo thư mục `audio_downloads` nếu chưa có.

## Development

### Add new endpoints
1. Edit `src/app/api/audio.py`
2. Update router trong `src/app/main.py`
3. Test với FastAPI's TestClient

### Frontend updates
1. Edit `src/components/AudioManager.jsx`
2. Update CSS trong `AudioManager.css`
3. Test trong development mode

## Testing

Service đã được test với:
- ✅ API endpoints hoạt động
- ✅ File listing và metadata
- ✅ Download functionality
- ✅ Security checks
- ✅ Error handling
- ✅ Frontend integration

Logs hiện tại cho thấy có 2 files trong thư mục:
- `README.txt` (581 bytes)
- `Nghe_Thay_Vì_Đọc__Khám_Phá_Công_Nghệ_Nghe_Nội_Dung,_Từ_Tiện_Lợi.mp4` (25.15 MB)