import React from 'react';
import { useImageDragDrop, useImagePreviews } from '../hooks/useImageUpload';
import styles from './ImageUploadZone.module.css';

const ImageUploadZone = ({ 
  files = [], 
  onFilesAdd, 
  onFileRemove, 
  maxFiles = 10, 
  maxFileSize = 50 * 1024 * 1024, // 50MB
  disabled = false 
}) => {
  const { isDragOver, dragProps } = useImageDragDrop(onFilesAdd);
  const { previews, loading } = useImagePreviews(files);

  const handleFileInputChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const imageFiles = selectedFiles.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length > 0) {
      onFilesAdd(imageFiles);
    }
    
    // Reset input value để cho phép chọn lại cùng file
    event.target.value = '';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (disabled) {
    return null;
  }

  return (
    <div className={styles.imageUploadContainer}>
      {/* Drop Zone */}
      <div 
        className={`${styles.dropZone} ${isDragOver ? styles.dragOver : ''} ${files.length > 0 ? styles.hasFiles : ''}`}
        {...dragProps}
      >
        <div className={styles.dropZoneContent}>
          <div className={styles.dropZoneIcon}>📷</div>
          <div className={styles.dropZoneText}>
            <p><strong>Kéo thả ảnh vào đây</strong></p>
            <p>hoặc <strong>Ctrl+V</strong> để paste ảnh</p>
            <p>hoặc <button 
              type="button" 
              className={styles.browseButton}
              onClick={() => document.getElementById('imageFileInput')?.click()}
            >
              chọn file
            </button></p>
          </div>
          <div className={styles.dropZoneDetails}>
            <small>
              Hỗ trợ: JPG, PNG, GIF, WebP | Tối đa {maxFiles} ảnh | Tối đa {formatFileSize(maxFileSize)}/ảnh
            </small>
          </div>
        </div>
        
        <input
          id="imageFileInput"
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
      </div>

      {/* Image Previews */}
      {files.length > 0 && (
        <div className={styles.imagePreviewsContainer}>
          <div className={styles.previewsHeader}>
            <h4>Ảnh đã chọn ({files.length}/{maxFiles})</h4>
            {files.length > maxFiles && (
              <span className={styles.warningText}>
                Vượt quá giới hạn! Chỉ {maxFiles} ảnh đầu tiên sẽ được gửi.
              </span>
            )}
          </div>

          {loading && (
            <div className={styles.loadingPreviews}>
              <div className={styles.spinner}></div>
              <span>Đang tạo preview...</span>
            </div>
          )}

          <div className={styles.imagePreviews}>
            {previews.map((preview, index) => (
              <div key={index} className={styles.imagePreview}>
                <div className={styles.imageContainer}>
                  <img 
                    src={preview.preview} 
                    alt={preview.name}
                    className={styles.previewImage}
                  />
                  <button
                    type="button"
                    className={styles.removeButton}
                    onClick={() => onFileRemove(index)}
                    title="Xóa ảnh"
                  >
                    ×
                  </button>
                </div>
                <div className={styles.imageInfo}>
                  <div className={styles.imageName} title={preview.name}>
                    {preview.name}
                  </div>
                  <div className={styles.imageSize}>
                    {formatFileSize(preview.size)}
                  </div>
                  {preview.size > maxFileSize && (
                    <div className={styles.sizeWarning}>
                      ⚠️ Quá lớn
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Paste Hint */}
      <div className={styles.pasteHint}>
        💡 <strong>Mẹo:</strong> Bạn có thể paste ảnh từ clipboard bất cứ đâu trên trang này bằng <kbd>Ctrl+V</kbd>
      </div>
    </div>
  );
};

export default ImageUploadZone;