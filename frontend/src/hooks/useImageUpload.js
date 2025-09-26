import { useCallback, useEffect, useState } from 'react';

/**
 * Hook để xử lý việc paste ảnh từ clipboard
 */
export const useImagePaste = (onImagesAdd) => {
  const [pastedImages, setPastedImages] = useState([]);

  const handlePaste = useCallback(async (event) => {
    const clipboardData = event.clipboardData;
    
    if (!clipboardData) {
      return;
    }

    const items = Array.from(clipboardData.items);
    const imageFiles = [];

    // Lọc và xử lý các item là ảnh
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          // Tạo tên file với timestamp
          const timestamp = Date.now();
          const extension = file.type.split('/')[1] || 'png';
          const renamedFile = new File([file], `pasted-image-${timestamp}.${extension}`, {
            type: file.type,
            lastModified: file.lastModified
          });
          
          imageFiles.push(renamedFile);
        }
      }
    }

    if (imageFiles.length > 0) {
      // Thêm vào danh sách ảnh đã paste
      setPastedImages(prev => [...prev, ...imageFiles]);
      
      // Gọi callback nếu có
      if (onImagesAdd) {
        onImagesAdd(imageFiles);
      }
    }
  }, [onImagesAdd]);

  const clearPastedImages = useCallback(() => {
    setPastedImages([]);
  }, []);

  const removePastedImage = useCallback((index) => {
    setPastedImages(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Thêm event listener cho paste
  useEffect(() => {
    document.addEventListener('paste', handlePaste);
    
    return () => {
      document.removeEventListener('paste', handlePaste);
    };
  }, [handlePaste]);

  return {
    pastedImages,
    clearPastedImages,
    removePastedImage
  };
};

/**
 * Hook để xử lý drag and drop ảnh
 */
export const useImageDragDrop = (onImagesAdd) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(event.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length > 0 && onImagesAdd) {
      onImagesAdd(imageFiles);
    }
  }, [onImagesAdd]);

  const dragProps = {
    onDragOver: handleDragOver,
    onDragLeave: handleDragLeave,
    onDrop: handleDrop
  };

  return {
    isDragOver,
    dragProps
  };
};

/**
 * Utility function để tạo preview URL cho ảnh
 */
export const createImagePreview = (file) => {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith('image/')) {
      reject(new Error('File is not an image'));
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      resolve({
        file,
        preview: e.target.result,
        name: file.name,
        size: file.size,
        type: file.type
      });
    };
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    reader.readAsDataURL(file);
  });
};

/**
 * Hook để xử lý preview ảnh
 */
export const useImagePreviews = (files) => {
  const [previews, setPreviews] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!files || files.length === 0) {
      setPreviews([]);
      return;
    }

    setLoading(true);
    
    const createPreviews = async () => {
      try {
        const previewPromises = files.map(file => createImagePreview(file));
        const results = await Promise.allSettled(previewPromises);
        
        const successfulPreviews = results
          .filter(result => result.status === 'fulfilled')
          .map(result => result.value);
        
        setPreviews(successfulPreviews);
      } catch (error) {
        console.error('Failed to create image previews:', error);
        setPreviews([]);
      } finally {
        setLoading(false);
      }
    };

    createPreviews();
  }, [files]);

  return { previews, loading };
};