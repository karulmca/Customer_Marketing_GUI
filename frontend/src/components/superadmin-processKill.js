import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Typography,
} from '@mui/material';

const SuperadminProcessKill = () => {
  const [files, setFiles] = useState([]);
  const [selectedFileId, setSelectedFileId] = useState('');
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch processing files from API
    const fetchFiles = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/superadmin/processing-files');
        setFiles(response.data.files || []);
      } catch (error) {
        setMessage('Failed to fetch processing files.');
      } finally {
        setLoading(false);
      }
    };
    fetchFiles();
  }, []);

  const handleKillProcess = async () => {
    setMessage('');
    if (!selectedFileId) {
      setMessage('Please select a file to kill the process.');
      return;
    }
    try {
      const response = await axios.post('/api/superadmin/kill-process', {
        process_id: selectedFileId
      });
      if (response.data.success) {
        setStatus('success');
        setMessage('Process killed and statuses updated successfully.');
        // Optionally refresh the file list
        setFiles(files.filter(f => f.id !== selectedFileId));
        setSelectedFileId('');
      } else {
        setStatus('error');
        setMessage(response.data.message || 'Failed to kill process.');
      }
    } catch (error) {
      setStatus('error');
      setMessage(error.response?.data?.message || 'Error occurred while killing process.');
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{ background: '#1976d2', color: '#fff', padding: '1rem', textAlign: 'center' }}>
        <h2 style={{ margin: 0 }}>Superadmin: Kill Process</h2>
      </header>
      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ padding: '2rem', maxWidth: '700px', width: '100%' }}>
          <Typography variant="h6" gutterBottom>Processing Files</Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Select</TableCell>
                    <TableCell>File Name</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Uploaded By</TableCell>
                    <TableCell>Upload Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {files.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">No processing files found.</TableCell>
                    </TableRow>
                  ) : (
                    files.map(file => (
                      <TableRow key={file.file_id} selected={selectedFileId === file.file_id}>
                        <TableCell>
                          <input
                            type="radio"
                            name="selectedFile"
                            checked={selectedFileId === file.file_id}
                            onChange={() => setSelectedFileId(file.file_id)}
                          />
                        </TableCell>
                        <TableCell>{file.file_name}</TableCell>
                        <TableCell>{file.status}</TableCell>
                        <TableCell>{file.uploaded_by}</TableCell>
                        <TableCell>{file.upload_date}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          <Button
            variant="contained"
            color="error"
            onClick={handleKillProcess}
            style={{ marginTop: '2rem', width: '100%' }}
            disabled={!selectedFileId || loading}
          >
            Kill Selected Process
          </Button>
          {message && (
            <div style={{ marginTop: '1rem', color: status === 'success' ? 'green' : 'red' }}>
              {message}
            </div>
          )}
          <Button onClick={() => navigate(-1)} style={{ marginTop: '2rem', width: '100%' }}>
            &larr; Back
          </Button>
        </div>
      </div>
      {/* Footer */}
      <footer style={{ background: '#f5f5f5', color: '#888', padding: '1rem', textAlign: 'center' }}>
        &copy; {new Date().getFullYear()} Company Data Scraper
      </footer>
    </div>
  );
};

export default SuperadminProcessKill;
