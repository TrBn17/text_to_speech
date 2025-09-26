import React from 'react';

import { useImageDragDrop, useImagePreviews } from '../hooks/useImageUpload';

import styles from './FileUploadZone.module.css';

const FileUploadZone = ({ 
  files = [], 
  onFilesAdd, 
  onFileRemove, 
  maxFiles = 10, 
  maxFileSize = 50 * 1024 * 1024, // 50MB
  disabled = false 
}) => {
  const { isDragOver, dragProps } = useImageDragDrop(onFilesAdd);

  const handleFileInputChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    
    if (selectedFiles.length > 0) {
      onFilesAdd(selectedFiles);
    }
    
    // Reset input value để cho phép chọn lại cùng file
    event.target.value = '';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return '📄';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'bmp':
      case 'webp': return '🖼️';
      case 'txt': return '📝';
      case 'doc':
      case 'docx': return '📋';
      default: return '📁';
    }
  };

  if (disabled) {
    return null;
  }

  return (
    <div className={styles.uploadContainer}>
      {/* Simple Drop Zone */}
      <div 
        className={`${styles.dropZone} ${isDragOver ? styles.dragOver : ''}`}
        {...dragProps}
      >
        <span className={styles.dropIcon}>�</span>
        <span>Kéo thả file hoặc </span>
        <button 
          type="button" 
          className={styles.browseBtn}
          onClick={() => document.getElementById('fileInput')?.click()}
        >
          chọn file
        </button>
        
        <input
          id="fileInput"
          type="file"
          accept="image/*,application/pdf,.txt,.doc,.docx"
          multiple
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className={styles.fileList}>
          {files.map((file, index) => (
            <div key={index} className={styles.fileItem}>
              <span className={styles.fileIcon}>{getFileIcon(file.name)}</span>
              <div className={styles.fileInfo}>
                <div className={styles.fileName}>{file.name}</div>
                <div className={styles.fileSize}>{formatFileSize(file.size)}</div>
              </div>
              <button
                type="button"
                className={styles.removeBtn}
                onClick={() => onFileRemove(index)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUploadZone;