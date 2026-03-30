import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { Upload, Image as ImageIcon, Video, ArrowRight, Activity, Clock, BarChart3, ChevronRight } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleUpload = async (uploadedFile) => {
    if (!uploadedFile) return;
    
    setLoading(true);
    setResult(null);
    
    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      setResult(response.data);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    const uploadedFile = e.dataTransfer.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      handleUpload(uploadedFile);
    }
  }, []);

  const onDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      handleUpload(uploadedFile);
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Smart Traffic Dashboard</h1>
        <p>AI-Powered Real-Time Traffic Density Analysis & Management</p>
      </header>

      <div className="upload-section">
        {/* Left Card: Upload Control */}
        <div className="card">
          <div className="card-header">
            <h2 style={{ marginBottom: '20px', fontSize: '1.4rem' }}>Media Analysis</h2>
          </div>
          <div 
            className={`upload-box ${isDragging ? 'dragging' : ''}`}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <Upload size={48} />
            <div>
              <p style={{ fontWeight: 600, fontSize: '1.1rem' }}>Click or Drop File</p>
              <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem', marginTop: '5px' }}>
                Supports JPG, PNG, MP4, AVI
              </p>
            </div>
            <input 
              id="fileInput"
              type="file" 
              hidden 
              onChange={handleFileChange}
              accept="image/*,video/*"
            />
          </div>

          {file && (
            <div style={{ marginTop: '20px', padding: '15px', background: 'var(--glass)', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              {file.type.startsWith('video') ? <Video size={20} color="var(--secondary)" /> : <ImageIcon size={20} color="var(--primary)" />}
              <span style={{ fontSize: '0.9rem', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>{file.name}</span>
              <Activity size={16} color="var(--primary)" className={loading ? 'spinner' : ''} />
            </div>
          )}

          <div style={{ marginTop: '30px' }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '15px', color: 'var(--text-dim)' }}>System Status</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)', boxShadow: '0 0 10px var(--primary)' }}></div>
              <span>Neural Engine Online</span>
            </div>
          </div>
        </div>

        {/* Right Card: Results View */}
        <div className="card results-preview">
          {!result && !loading && (
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', opacity: 0.5 }}>
              <BarChart3 size={64} style={{ marginBottom: '20px' }} />
              <p>Upload a file to start AI analysis</p>
            </div>
          )}

          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Analyzing Traffic Patterns...</p>
            </div>
          )}

          {result && (
            <>
              <div className="image-container">
                <img 
                  src={`${API_BASE_URL}${result.result_url || result.preview_url}`} 
                  alt="Detection Analysis" 
                />
              </div>

              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-value">{result.total_vehicles}</span>
                  <span className="stat-label">Vehicles</span>
                </div>
                <div className="stat-item green-time">
                  <span className="stat-value">{result.recommended_green_time}s</span>
                  <span className="stat-label">Green Time</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">High</span>
                  <span className="stat-label">Accuracy</span>
                </div>
              </div>

              <div className="breakdown">
                <h3><BarChart3 size={18} style={{ verticalAlign: 'middle', marginRight: '8px' }} /> Vehicle Composition</h3>
                <div className="tag-cloud">
                  {Object.entries(result.breakdown).map(([type, count]) => (
                    <div key={type} className="tag">
                      <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{count}</span> {type.charAt(0).toUpperCase() + type.slice(1)}s
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', color: 'var(--primary)', fontSize: '0.9rem', cursor: 'pointer' }}>
                View Full Analytics <ChevronRight size={16} />
              </div>
            </>
          )}
        </div>
      </div>
      
      <footer style={{ textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '40px' }}>
        Antigravity Smart Traffic Engine v2.0 • Real-time Computer Vision Powered
      </footer>
    </div>
  );
}

export default App;
