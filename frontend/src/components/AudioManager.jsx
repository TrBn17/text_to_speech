import React, { useState, useEffect, useCallback } from 'react';

import env from '../config/environment';
import './AudioManager.css';

const AudioManager = () => {
    const [files, setFiles] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_BASE = env.api.baseUrl;

    // Fetch files from API
    const fetchFiles = useCallback(async () => {
        try {
            setLoading(true);
            const url = `${API_BASE}/api/audio/files`;
            console.log('🔍 Fetching files from:', url);
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setFiles(data);
            setError(null);
        } catch (err) {
            setError(`Failed to fetch files: ${err.message}`);
            console.error('Error fetching files:', err);
        } finally {
            setLoading(false);
        }
    }, [API_BASE]);

    // Fetch statistics
    const fetchStats = useCallback(async () => {
        try {
            const url = `${API_BASE}/api/audio/stats`;
            console.log('🔍 Fetching stats from:', url);
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setStats(data);
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    }, [API_BASE]);

    // Delete a file
    const deleteFile = async (filename) => {
        if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }

        try {
            const url = `${API_BASE}/api/audio/files/${encodeURIComponent(filename)}`;
            console.log('🔍 Deleting file:', url);
            const response = await fetch(url, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Refresh the file list
            await fetchFiles();
            await fetchStats();
        } catch (err) {
            alert(`Failed to delete file: ${err.message}`);
        }
    };

    // Cleanup old files
    const cleanupOldFiles = async (days = 7) => {
        if (!window.confirm(`Delete all files older than ${days} days?`)) {
            return;
        }

        try {
            const url = `${API_BASE}/api/audio/cleanup?days=${days}`;
            console.log('🔍 Cleanup URL:', url);
            const response = await fetch(url, {
                method: 'POST'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const result = await response.json();
            alert(`Cleanup completed. Deleted ${result.count} files.`);
            // Refresh the file list
            await fetchFiles();
            await fetchStats();
        } catch (err) {
            alert(`Cleanup failed: ${err.message}`);
        }
    };

    // Format file size
    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Format date
    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleString();
    };

    useEffect(() => {
        fetchFiles();
        fetchStats();
    }, [fetchFiles, fetchStats]);

    if (loading) {
        return (
            <div className="audio-manager">
                <div className="loading">Loading audio files...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="audio-manager">
                <div className="error">
                    <p>Error: {error}</p>
                    <button onClick={fetchFiles} className="retry-btn">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="audio-manager">
            <div className="header">
                <h2>Audio Files Manager</h2>
                <div className="stats">
                    <span className="stat">Total Files: {stats.total_files || 0}</span>
                    <span className="stat">Audio Files: {stats.audio_files || 0}</span>
                    <span className="stat">Total Size: {formatFileSize(stats.total_size_bytes || 0)}</span>
                </div>
                <div className="actions">
                    <button onClick={fetchFiles} className="refresh-btn">
                        Refresh
                    </button>
                    <button onClick={() => cleanupOldFiles(7)} className="cleanup-btn">
                        Cleanup (7+ days)
                    </button>
                </div>
            </div>

            {files.length === 0 ? (
                <div className="no-files">
                    <p>No audio files found</p>
                    <p className="tip">Files will appear here after you generate audio conversations</p>
                </div>
            ) : (
                <div className="file-list">
                    {files.map((file, index) => (
                        <div key={index} className={`file-item ${file.is_audio ? 'audio-file' : ''}`}>
                            <div className="file-info">
                                <div className="file-name">
                                    {file.is_audio && <span className="audio-icon">🎵</span>}
                                    <strong>{file.name}</strong>
                                </div>
                                <div className="file-meta">
                                    <span className="file-size">{formatFileSize(file.size)}</span>
                                    <span className="file-date">{formatDate(file.modified)}</span>
                                    <span className="file-type">{file.mime_type}</span>
                                </div>
                            </div>
                            <div className="file-actions">
                                <a
                                    href={`${API_BASE}${file.download_url}`}
                                    download
                                    className="download-btn"
                                    title="Download file"
                                >
                                    Download
                                </a>
                                {file.is_audio && (
                                    <audio controls className="audio-player">
                                        <source src={`${API_BASE}${file.download_url}`} type={file.mime_type} />
                                        Your browser does not support the audio element.
                                    </audio>
                                )}
                                <button
                                    onClick={() => deleteFile(file.name)}
                                    className="delete-btn"
                                    title="Delete file"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className="footer">
                <p className="storage-path">Storage: {stats.directory}</p>
            </div>
        </div>
    );
};

export default AudioManager;