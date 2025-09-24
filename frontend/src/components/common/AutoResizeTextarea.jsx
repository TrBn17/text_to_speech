import React, { useRef, useEffect } from 'react';

const AutoResizeTextarea = ({ 
  value, 
  onChange, 
  onKeyDown,
  placeholder = "Type your message here... (Shift+Enter for new line)", 
  disabled = false, 
  className = '',
  minRows = 1,
  maxRows = 6,
  ...props 
}) => {
  const textareaRef = useRef(null);

  const adjustHeight = React.useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Calculate the number of rows based on content
    const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight);
    const padding = parseInt(window.getComputedStyle(textarea).paddingTop) + 
                   parseInt(window.getComputedStyle(textarea).paddingBottom);
    
    const contentHeight = textarea.scrollHeight - padding;
    const rows = Math.ceil(contentHeight / lineHeight);
    
    // Clamp between min and max rows
    const clampedRows = Math.max(minRows, Math.min(maxRows, rows));
    const height = (clampedRows * lineHeight) + padding;
    
    textarea.style.height = `${height}px`;
  }, [minRows, maxRows]);

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  useEffect(() => {
    // Adjust height on mount
    adjustHeight();
  }, [adjustHeight]);

  const handleChange = (e) => {
    if (onChange) {
      onChange(e);
    }
    // Adjust height after state update
    setTimeout(adjustHeight, 0);
  };

  const handleKeyDown = (e) => {
    if (onKeyDown) {
      onKeyDown(e);
    }
  };

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      placeholder={placeholder}
      disabled={disabled}
      className={className}
      style={{
        resize: 'none',
        overflow: 'hidden',
        transition: 'height 0.1s ease-out',
        boxSizing: 'border-box'
      }}
      {...props}
    />
  );
};

export default AutoResizeTextarea;