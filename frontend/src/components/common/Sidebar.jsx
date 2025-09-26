import styles from '../../styles/common/Sidebar.module.css';

const Sidebar = ({ 
  title, 
  icon = '⚙️', 
  children, 
  className = '' 
}) => {
  return (
    <div className={`${styles.sidebar} ${className}`}>
      <div className={styles.sidebarHeader}>
        <h2 className={styles.sidebarTitle}>
          {icon} {title}
        </h2>
      </div>
      <div className={styles.sidebarContent}>
        {children}
      </div>
    </div>
  );
};

export default Sidebar;