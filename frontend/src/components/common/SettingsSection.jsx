import React from 'react';
import styles from '../../styles/common/SettingsSection.module.css';

const SettingsSection = ({ 
  title, 
  children, 
  className = '' 
}) => {
  return (
    <div className={`${styles.settingsSection} ${className}`}>
      {title && <h3 className={styles.sectionTitle}>{title}</h3>}
      {children}
    </div>
  );
};

const SettingGroup = ({ 
  label, 
  htmlFor, 
  children, 
  className = '' 
}) => {
  return (
    <div className={`${styles.settingGroup} ${className}`}>
      {label && (
        <label htmlFor={htmlFor} className={styles.label}>
          {label}
        </label>
      )}
      {children}
    </div>
  );
};

export { SettingsSection, SettingGroup };