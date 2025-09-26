import React, { useState, useEffect, useCallback } from 'react';
import './NotificationManager.css';

const NotificationManager = ({ notifications, onRemove }) => {
    return (
        <div className="notification-container">
            {notifications.map((notification) => (
                <Notification
                    key={notification.id}
                    notification={notification}
                    onRemove={onRemove}
                />
            ))}
        </div>
    );
};

const Notification = ({ notification, onRemove }) => {
    const { id, type, title, message, duration = 5000, persistent = false } = notification;

    useEffect(() => {
        if (!persistent && duration > 0) {
            const timer = setTimeout(() => {
                onRemove(id);
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [id, duration, persistent, onRemove]);

    const getIcon = () => {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            case 'processing': return '🔄';
            default: return '📢';
        }
    };

    const handleClose = () => {
        onRemove(id);
    };

    return (
        <div className={`notification notification-${type}`}>
            <div className="notification-content">
                <div className="notification-icon">
                    {getIcon()}
                </div>
                <div className="notification-text">
                    {title && <div className="notification-title">{title}</div>}
                    <div className="notification-message">{message}</div>
                </div>
            </div>
            <button
                className="notification-close"
                onClick={handleClose}
                aria-label="Close notification"
            >
                ×
            </button>
            {!persistent && duration > 0 && (
                <div
                    className="notification-progress"
                    style={{
                        animation: `notification-progress ${duration}ms linear`
                    }}
                />
            )}
        </div>
    );
};

// Hook for managing notifications
export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = useCallback((notification) => {
        const id = Date.now() + Math.random();
        const newNotification = {
            id,
            ...notification,
            timestamp: new Date().toISOString()
        };

        setNotifications(prev => [...prev, newNotification]);
        return id;
    }, []);

    const removeNotification = useCallback((id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    }, []);

    const clearAll = useCallback(() => {
        setNotifications([]);
    }, []);

    // Helper methods for different notification types
    const notify = {
        success: useCallback((message, options = {}) =>
            addNotification({ ...options, type: 'success', message }), [addNotification]),

        error: useCallback((message, options = {}) =>
            addNotification({ ...options, type: 'error', message, duration: 8000 }), [addNotification]),

        warning: useCallback((message, options = {}) =>
            addNotification({ ...options, type: 'warning', message }), [addNotification]),

        info: useCallback((message, options = {}) =>
            addNotification({ ...options, type: 'info', message }), [addNotification]),

        processing: useCallback((message, options = {}) =>
            addNotification({ ...options, type: 'processing', message, persistent: true }), [addNotification])
    };

    return {
        notifications,
        addNotification,
        removeNotification,
        clearAll,
        notify
    };
};

export default NotificationManager;