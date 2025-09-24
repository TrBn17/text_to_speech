import React from 'react';
import styles from '../../styles/common/FormControls.module.css';

const Select = ({ 
  value, 
  onChange, 
  options = [], 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  return (
    <select
      value={value}
      onChange={onChange}
      disabled={disabled}
      className={`${styles.select} ${className}`}
      {...props}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
};

const Input = ({ 
  type = 'text', 
  value, 
  onChange, 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      disabled={disabled}
      className={`${styles.input} ${className}`}
      {...props}
    />
  );
};

const Textarea = ({ 
  value, 
  onChange, 
  rows = 3, 
  disabled = false, 
  className = '', 
  ...props 
}) => {
  return (
    <textarea
      value={value}
      onChange={onChange}
      rows={rows}
      disabled={disabled}
      className={`${styles.textarea} ${className}`}
      {...props}
    />
  );
};

const Slider = ({ 
  min = 0, 
  max = 100, 
  step = 1, 
  value, 
  onChange, 
  showValue = true, 
  valueFormatter = (v) => v, 
  className = '' 
}) => {
  return (
    <div className={`${styles.sliderContainer} ${className}`}>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={onChange}
        className={styles.slider}
      />
      {showValue && (
        <span className={styles.sliderValue}>
          {valueFormatter(value)}
        </span>
      )}
    </div>
  );
};

const CheckboxLabel = ({ 
  checked, 
  onChange, 
  children, 
  className = '' 
}) => {
  return (
    <label className={`${styles.checkboxLabel} ${className}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className={styles.checkbox}
      />
      {children}
    </label>
  );
};

export { Select, Input, Textarea, Slider, CheckboxLabel };