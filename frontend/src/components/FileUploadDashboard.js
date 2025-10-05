import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  AppBar,
  Toolbar,
  IconButton,
  Grid,
  Paper,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Logout as LogoutIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Storage as StorageIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Download as DownloadIcon,
  GetApp as GetAppIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { FileService, DatabaseService } from '../services/AuthService';

const FileUploadDashboard = ({ sessionId, userInfo, onLogout }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadingAsJson, setUploadingAsJson] = useState(false);
  const [uploadingAndProcessing, setUploadingAndProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [dbStatus, setDbStatus] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showProcessDialog, setShowProcessDialog] = useState(false);
  const [processOptions, setProcessOptions] = useState({
    scrapingEnabled: true,
    aiAnalysisEnabled: false
  });
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [processingFiles, setProcessingFiles] = useState(new Set()); // Track which files are being processed
  const [refreshing, setRefreshing] = useState(false); // Track when auto-refresh is happening
  const [nextJobCountdown, setNextJobCountdown] = useState(120); // Countdown in seconds (2 minutes)
  const [lastJobCheck, setLastJobCheck] = useState(Date.now()); // Track when we last checked for jobs

  // Define checkDatabaseStatus function first
  const checkDatabaseStatus = useCallback(async () => {
    try {
      const status = await DatabaseService.getStatus(sessionId);
      setDbStatus(status);
    } catch (error) {
      console.error('Database status error:', error);
      setDbStatus({ status: 'error', message: error.message });
    }
  }, [sessionId]);

  // Function to load uploaded files
  const loadUploadedFiles = useCallback(async () => {
    try {
      const response = await FileService.getUploadedFiles(sessionId);
      setUploadedFiles(response.files || []);
    } catch (error) {
      console.error('Failed to load uploaded files:', error);
    }
  }, [sessionId]);

  // Check database status on component mount
  useEffect(() => {
    checkDatabaseStatus();
    loadUploadedFiles();
    setLastJobCheck(Date.now()); // Initialize job check time
  }, [sessionId, checkDatabaseStatus, loadUploadedFiles]);

  // Countdown timer for next scheduled job (runs every second)
  useEffect(() => {
    const timerInterval = setInterval(() => {
      const now = Date.now();
      const elapsed = Math.floor((now - lastJobCheck) / 1000); // seconds since last check
      const remaining = Math.max(0, 120 - elapsed); // 2 minutes = 120 seconds
      
      setNextJobCountdown(remaining);
      
      // Reset countdown when it reaches 0 (next job cycle)
      if (remaining === 0) {
        setLastJobCheck(now);
      }
    }, 1000);

    return () => clearInterval(timerInterval);
  }, [lastJobCheck]);

  // Optimized auto-refresh: Only refresh files/processing sections every 30 seconds, unless actively processing
  useEffect(() => {
    const hasActiveProcessing = uploadedFiles.some(f => f.processing_status === 'processing') || processingFiles.size > 0;
    const refreshInterval = hasActiveProcessing ? 10000 : 30000; // 10s when processing, 30s when idle
    
    const autoRefreshInterval = setInterval(async () => {
      try {
        setRefreshing(true);
        // Only update files data, don't refresh entire page
        const previousFiles = [...uploadedFiles];
        await loadUploadedFiles();
        
        // Check if job status changed (could indicate scheduler ran)
        const response = await FileService.getUploadedFiles(sessionId);
        const currentFiles = response.files || [];
        const statusChanged = previousFiles.some((prevFile, index) => {
          const currentFile = currentFiles.find(f => f.id === prevFile.id);
          return currentFile && currentFile.processing_status !== prevFile.processing_status;
        });
        
        // If status changed, reset the countdown (scheduler likely ran)
        if (statusChanged) {
          setLastJobCheck(Date.now());
        }
        
        // Check processing status for active files
        if (processingFiles.size > 0) {
          const response = await FileService.getUploadedFiles(sessionId);
          const files = response.files || [];
          
          // Check if any files finished processing
          const stillProcessing = new Set();
          let hasCompletedFiles = false;
          
          processingFiles.forEach(fileId => {
            const file = files.find(f => f.id === fileId);
            if (file) {
              if (file.processing_status === 'processing' || file.processing_status === 'pending') {
                stillProcessing.add(fileId);
              } else if (file.processing_status === 'completed' || file.processing_status === 'failed') {
                hasCompletedFiles = true;
                if (file.processing_status === 'completed') {
                  setSuccess(`File "${file.file_name}" processed successfully!`);
                } else if (file.processing_status === 'failed') {
                  setError(`File "${file.file_name}" processing failed: ${file.processing_error || 'Unknown error'}`);
                }
              }
            } else {
              // File not found in the list, remove from processing
              hasCompletedFiles = true;
            }
          });
          
          // Update processing files set
          setProcessingFiles(stillProcessing);
          
          // If we have completed files, clear processing status
          if (hasCompletedFiles && stillProcessing.size === 0) {
            setProcessingStatus(null);
          }
        }
        
        } catch (error) {
        console.error('Auto-refresh error:', error);
        } finally {
          setRefreshing(false);
        }
    }, refreshInterval);

    return () => clearInterval(autoRefreshInterval);
  }, [loadUploadedFiles, uploadedFiles, processingFiles.size, sessionId]);  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile({ file });
    setError('');
    setValidationResult(null);
    
    // Auto-validate headers when file is selected
    await validateFileHeaders(file);
  }, []);

  // Validate file headers
  const validateFileHeaders = async (file) => {
    try {
      setValidating(true);
      setError('');
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`http://localhost:8000/api/files/validate-headers?session_id=${sessionId}`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        setValidationResult(result.validation);
        if (!result.validation.valid) {
          setError(`File validation failed: ${result.validation.error}`);
        }
      } else {
        throw new Error(result.detail || 'Validation failed');
      }
    } catch (error) {
      setError(`Validation error: ${error.message}`);
      setValidationResult(null);
    } finally {
      setValidating(false);
    }
  };

  // Upload as JSON (original GUI workflow)
  const handleUploadAsJson = async () => {
    if (!uploadedFile?.file) return;

    try {
      setError('');
      setUploadingAsJson(true);
      
      const response = await FileService.uploadFileAsJson(sessionId, uploadedFile.file);
      
      setSuccess(`File uploaded as JSON successfully! (ID: ${response.file_upload_id})`);
      
      // Clear the uploaded file from dropzone
      setUploadedFile(null);
      setValidationResult(null);
      
      // Immediate refresh and then delayed refresh to ensure file appears
      await loadUploadedFiles();
      setTimeout(async () => {
        await loadUploadedFiles();
      }, 1000);
      
      setUploadingAsJson(false);
    } catch (error) {
      setError(error.message);
      setUploadingAsJson(false);
    }
  };

  // Upload and process immediately (original GUI workflow)
  const handleUploadAndProcess = async () => {
    if (!uploadedFile?.file) return;

    try {
      setError('');
      setUploadingAndProcessing(true);
      
      const response = await FileService.uploadAndProcessFile(sessionId, uploadedFile.file);
      
      if (response.success) {
        setSuccess(`File uploaded and processed successfully! (ID: ${response.file_upload_id})`);
      } else {
        setError(`Processing failed: ${response.message}`);
      }
      
      // Clear the uploaded file from dropzone
      setUploadedFile(null);
      setValidationResult(null);
      
      // Immediate refresh and then delayed refresh to ensure file appears
      await loadUploadedFiles();
      setTimeout(async () => {
        await loadUploadedFiles();
      }, 1000);
      
      setUploadingAndProcessing(false);
    } catch (error) {
      setError(error.message);
      setUploadingAndProcessing(false);
    }
  };

  // Handle processing a specific uploaded file
  const handleProcessFile = async (fileId) => {
    try {
      // Add file to processing set
      setProcessingFiles(prev => new Set([...prev, fileId]));
      setError('');
      setProcessingStatus({ status: 'starting', progress: 0, fileId });
      
      // Start processing the file
      await FileService.processFile(sessionId, fileId);
      setSuccess('File processing started successfully!');
      
      // Start polling for this specific file
      setUploadedFile({ fileId });
      
    } catch (error) {
      setError(error.message);
      // Remove file from processing set on error
      setProcessingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  };

  // Handle downloading sample template
  const handleDownloadTemplate = async () => {
    try {
      setDownloadingTemplate(true);
      setError('');
      
      const response = await fetch('http://localhost:8000/api/sample-template');
      
      if (!response.ok) {
        throw new Error('Failed to download template');
      }
      
      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'company_data_template.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSuccess('Sample template downloaded successfully!');
    } catch (error) {
      setError(`Failed to download template: ${error.message}`);
    } finally {
      setDownloadingTemplate(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleStartProcessing = async () => {
    if (!uploadedFile?.fileId) return;

    try {
      setError('');
      setProcessingStatus({ status: 'processing', progress: 0, message: 'Starting...' });
      
      await FileService.processFile(sessionId, uploadedFile.fileId, processOptions);
      setShowProcessDialog(false);
    } catch (error) {
      setError(error.message);
      setProcessingStatus(null);
    }
  };

  const handleDownloadResults = async () => {
    if (!uploadedFile?.fileId) return;

    try {
      setError('');
      const result = await FileService.downloadProcessedFile(sessionId, uploadedFile.fileId);
      setSuccess(`File downloaded successfully: ${result.filename}`);
    } catch (error) {
      setError(error.message);
    }
  };

  // Handle downloading processed file with LinkedIn enrichment
  const handleDownloadProcessedFile = async (fileId, fileName) => {
    try {
      setError('');
      const response = await fetch(`http://localhost:8000/api/files/download-processed/${fileId}?session_id=${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to download processed file');
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `processed_${fileName}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Processed file downloaded successfully: processed_${fileName}`);
    } catch (error) {
      setError(`Failed to download processed file: ${error.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'processing': return 'primary';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckIcon />;
      case 'failed': return <ErrorIcon />;
      case 'processing': return <ScheduleIcon />;
      default: return <ScheduleIcon />;
    }
  };

  return (
    <Box sx={{ 
      flexGrow: 1,
      '@keyframes pulse': {
        '0%': { opacity: 1 },
        '50%': { opacity: 0.5 },
        '100%': { opacity: 1 }
      },
      '@keyframes spin': {
        '0%': { transform: 'rotate(0deg)' },
        '100%': { transform: 'rotate(360deg)' }
      }
    }}>
      {/* Header */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Company Data Scraper - Welcome {userInfo?.username}
          </Typography>
          {/* Refresh Status Indicator */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              Auto-refresh: {(uploadedFiles.some(f => f.processing_status === 'processing') || processingFiles.size > 0) ? '10s' : '30s'}
            </Typography>
            {refreshing && (
              <Typography sx={{ fontSize: '0.7rem', animation: 'pulse 1.5s infinite' }}>
                🔄
              </Typography>
            )}
          </Box>
          <Tooltip title="Manual refresh (database status & files)">
            <IconButton 
              color="inherit" 
              onClick={async () => {
                setRefreshing(true);
                try {
                  await checkDatabaseStatus();
                  await loadUploadedFiles();
                } finally {
                  setRefreshing(false);
                }
              }}
              disabled={refreshing}
            >
              <RefreshIcon sx={refreshing ? { animation: 'spin 1s linear infinite' } : {}} />
            </IconButton>
          </Tooltip>
          <IconButton color="inherit" onClick={onLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box sx={{ p: 3 }}>
        {/* Status Row */}
        <Grid container spacing={3} sx={{ mb: 1 }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: 'fit-content' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} sx={{ mb: 2 }}>
                  <StorageIcon color={dbStatus?.status === 'connected' ? 'success' : 'error'} />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6">Database Status</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {dbStatus?.message || 'Checking...'}
                    </Typography>
                  </Box>
                  <Chip
                    label={dbStatus?.status || 'Unknown'}
                    color={dbStatus?.status === 'connected' ? 'success' : 'error'}
                    variant="outlined"
                  />
                  {/* Connection Details Tooltip */}
                  {dbStatus?.details && (
                    <Tooltip 
                      title={
                        <Box>
                          <Typography variant="subtitle2" gutterBottom color="inherit">
                            Connection Details:
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Host:</strong> {dbStatus.details.host}
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Port:</strong> {dbStatus.details.port}
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Database:</strong> {dbStatus.details.database}
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>User:</strong> {dbStatus.details.user}
                          </Typography>
                          {dbStatus.details.version && (
                            <Typography variant="body2" color="inherit">
                              <strong>Version:</strong> {dbStatus.details.version}
                            </Typography>
                          )}
                        </Box>
                      }
                      arrow
                      placement="left"
                    >
                      <IconButton
                        size="small"
                        sx={{ 
                          color: 'primary.main',
                          '&:hover': { backgroundColor: 'action.hover' }
                        }}
                      >
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card sx={{ height: 'fit-content' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} sx={{ mb: 2 }}>
                  <ScheduleIcon color="primary" />
                  <Box sx={{ flexGrow: 1 }}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6">Processing Status</Typography>
                      {refreshing && (
                        <Tooltip title="Auto-refreshing data...">
                          <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary', animation: 'pulse 1.5s infinite' }}>
                            🔄
                          </Typography>
                        </Tooltip>
                      )}
                      {uploadedFiles.length > 0 && (
                        (() => {
                          const processingFilesList = uploadedFiles.filter(f => f.processing_status === 'processing');
                          const pendingFiles = uploadedFiles.filter(f => f.processing_status === 'pending' || !f.processing_status);
                          const completedFiles = uploadedFiles.filter(f => f.processing_status === 'completed');
                          const failedFiles = uploadedFiles.filter(f => f.processing_status === 'failed');
                          
                          if (processingFilesList.length > 0) {
                            const isManual = processingFilesList.some(f => processingFiles.has(f.id));
                            return <Typography sx={{ fontSize: '1.2rem' }}>{isManual ? '👤' : '🤖'}</Typography>;
                          } else if (pendingFiles.length > 0) {
                            return <Typography sx={{ fontSize: '1.2rem' }}>⏳</Typography>;
                          } else if (completedFiles.length > 0) {
                            return <Typography sx={{ fontSize: '1.2rem' }}>✅</Typography>;
                          } else if (failedFiles.length > 0) {
                            return <Typography sx={{ fontSize: '1.2rem' }}>❌</Typography>;
                          }
                          return null;
                        })()
                      )}
                    </Box>
                    <Box>
                      {uploadedFiles.length > 0 ? (
                        <>
                          <Typography variant="body2" color="text.secondary">
                            {uploadedFiles.length} files uploaded
                          </Typography>
                          {/* Show countdown timer for next scheduled job */}
                          {uploadedFiles.filter(f => f.processing_status === 'pending' || !f.processing_status).length > 0 && (
                            <Box sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              gap: 1,
                              mt: 0.5,
                              p: 1,
                              borderRadius: 1,
                              backgroundColor: 'info.light',
                              border: '1px solid',
                              borderColor: 'info.main',
                            }}>
                              <Typography sx={{ fontSize: '0.9rem' }}>⏰</Typography>
                              <Typography variant="caption" color="info.main">
                                Next auto-job in: {Math.floor(nextJobCountdown / 60)}:{(nextJobCountdown % 60).toString().padStart(2, '0')}
                              </Typography>
                            </Box>
                          )}
                          {/* Show currently processing file details */}
                          {uploadedFiles.filter(f => f.processing_status === 'processing').map(file => {
                            const isManualProcessing = processingFiles.has(file.id);
                            return (
                              <Box key={file.id} sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1,
                                p: 1,
                                borderRadius: 1,
                                backgroundColor: isManualProcessing ? 'primary.light' : 'warning.light',
                                border: `2px solid ${isManualProcessing ? 'primary.main' : 'warning.main'}`,
                                mt: 0.5
                              }}>
                                <Box sx={{ 
                                  width: 8, 
                                  height: 8, 
                                  borderRadius: '50%', 
                                  backgroundColor: isManualProcessing ? 'primary.main' : 'warning.main',
                                  animation: 'pulse 2s infinite'
                                }} />
                                <Typography variant="body2" sx={{ 
                                  fontWeight: 'bold',
                                  color: isManualProcessing ? 'primary.contrastText' : 'warning.contrastText'
                                }}>
                                  {file.file_name || file.filename}
                                </Typography>
                                <Chip 
                                  label={isManualProcessing ? 'Manual Processing' : 'Automated Processing'}
                                  size="small"
                                  color={isManualProcessing ? 'primary' : 'warning'}
                                  variant="filled"
                                  sx={{ 
                                    fontWeight: 'bold',
                                    fontSize: '0.7rem',
                                    '& .MuiChip-label': {
                                      px: 1
                                    }
                                  }}
                                />
                              </Box>
                            );
                          })}
                          {/* Show most recent activity if no files are currently processing */}
                          {uploadedFiles.filter(f => f.processing_status === 'processing').length === 0 && uploadedFiles.length > 0 && (
                            (() => {
                              const completedFiles = uploadedFiles.filter(f => f.processing_status === 'completed');
                              const pendingFiles = uploadedFiles.filter(f => f.processing_status === 'pending' || !f.processing_status);
                              const failedFiles = uploadedFiles.filter(f => f.processing_status === 'failed');
                              
                              if (completedFiles.length > 0) {
                                const lastCompleted = completedFiles[completedFiles.length - 1];
                                return (
                                  <Box sx={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    gap: 1,
                                    p: 1,
                                    borderRadius: 1,
                                    backgroundColor: 'success.light',
                                    border: '2px solid',
                                    borderColor: 'success.main',
                                    mt: 0.5
                                  }}>
                                    <Box sx={{ 
                                      width: 8, 
                                      height: 8, 
                                      borderRadius: '50%', 
                                      backgroundColor: 'success.main'
                                    }} />
                                    <Typography variant="body2" sx={{ 
                                      fontWeight: 'bold',
                                      color: 'success.contrastText'
                                    }}>
                                      {lastCompleted.file_name || lastCompleted.filename}
                                    </Typography>
                                    <Chip 
                                      label="Completed"
                                      size="small"
                                      color="success"
                                      variant="filled"
                                      sx={{ 
                                        fontWeight: 'bold',
                                        fontSize: '0.7rem'
                                      }}
                                    />
                                  </Box>
                                );
                              } else if (pendingFiles.length > 0) {
                                const nextPending = pendingFiles[0];
                                return (
                                  <Box sx={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    gap: 1,
                                    p: 1,
                                    borderRadius: 1,
                                    backgroundColor: 'info.light',
                                    border: '2px solid',
                                    borderColor: 'info.main',
                                    mt: 0.5
                                  }}>
                                    <Box sx={{ 
                                      width: 8, 
                                      height: 8, 
                                      borderRadius: '50%', 
                                      backgroundColor: 'info.main'
                                    }} />
                                    <Typography variant="body2" sx={{ 
                                      fontWeight: 'bold',
                                      color: 'info.contrastText'
                                    }}>
                                      {nextPending.file_name || nextPending.filename}
                                    </Typography>
                                    <Chip 
                                      label="Pending"
                                      size="small"
                                      color="info"
                                      variant="filled"
                                      sx={{ 
                                        fontWeight: 'bold',
                                        fontSize: '0.7rem'
                                      }}
                                    />
                                  </Box>
                                );
                              } else if (failedFiles.length > 0) {
                                const lastFailed = failedFiles[failedFiles.length - 1];
                                return (
                                  <Box sx={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    gap: 1,
                                    p: 1,
                                    borderRadius: 1,
                                    backgroundColor: 'error.light',
                                    border: '2px solid',
                                    borderColor: 'error.main',
                                    mt: 0.5
                                  }}>
                                    <Box sx={{ 
                                      width: 8, 
                                      height: 8, 
                                      borderRadius: '50%', 
                                      backgroundColor: 'error.main'
                                    }} />
                                    <Typography variant="body2" sx={{ 
                                      fontWeight: 'bold',
                                      color: 'error.contrastText'
                                    }}>
                                      {lastFailed.file_name || lastFailed.filename}
                                    </Typography>
                                    <Chip 
                                      label="Failed"
                                      size="small"
                                      color="error"
                                      variant="filled"
                                      sx={{ 
                                        fontWeight: 'bold',
                                        fontSize: '0.7rem'
                                      }}
                                    />
                                  </Box>
                                );
                              }
                              return null;
                            })()
                          )}
                        </>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No files uploaded yet
                        </Typography>
                      )}
                    </Box>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip
                      label={uploadedFiles.filter(f => f.processing_status === 'completed').length > 0 
                        ? 'Active' : 'Ready'}
                      color={uploadedFiles.filter(f => f.processing_status === 'processing').length > 0 
                        ? 'warning' : 'success'}
                      variant="outlined"
                    />
                    <RefreshIcon 
                      sx={{ 
                        fontSize: '0.8rem', 
                        color: 'text.secondary',
                        animation: 'spin 2s linear infinite',
                        '@keyframes spin': {
                          '0%': { transform: 'rotate(0deg)' },
                          '100%': { transform: 'rotate(360deg)' }
                        }
                      }} 
                    />
                  </Box>
                  {/* Processing Stats Tooltip */}
                  {uploadedFiles.length > 0 && (
                    <Tooltip 
                      title={
                        <Box>
                          <Typography variant="subtitle2" gutterBottom color="inherit">
                            File Processing Statistics:
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Total Files:</strong> {uploadedFiles.length}
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Completed:</strong> {uploadedFiles.filter(f => f.processing_status === 'completed').length}
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Processing:</strong> {uploadedFiles.filter(f => f.processing_status === 'processing').length}
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                            <strong>Pending:</strong> {uploadedFiles.filter(f => f.processing_status === 'pending' || !f.processing_status).length}
                          </Typography>
                          <Typography variant="body2" color="inherit">
                            <strong>Failed:</strong> {uploadedFiles.filter(f => f.processing_status === 'failed').length}
                          </Typography>
                        </Box>
                      }
                      arrow
                      placement="left"
                    >
                      <IconButton
                        size="small"
                        sx={{ 
                          color: 'primary.main',
                          '&:hover': { backgroundColor: 'action.hover' }
                        }}
                      >
                        <InfoIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* File Upload Section - Original GUI Workflow */}
        <Grid container spacing={3} sx={{ alignItems: 'flex-start' }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: 'fit-content' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} sx={{ mb: 3 }}>
                  <UploadIcon color="primary" />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6">File Upload - JSON Storage for Scheduled Processing</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Upload Excel/CSV files → Store as JSON → Process with enhanced scraping
                    </Typography>
                  </Box>
                  {/* Column Format Guide Tooltip */}
                  <Tooltip 
                    title={
                      <Box sx={{ maxWidth: 400 }}>
                        <Typography variant="subtitle2" gutterBottom color="inherit">
                          📊 Expected Column Format
                        </Typography>
                        <Typography variant="body2" color="inherit" sx={{ mb: 1 }}>
                          Your Excel/CSV file should contain these columns (exact names):
                        </Typography>
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="body2" color="inherit" sx={{ fontWeight: 'bold', color: 'error.light' }}>
                            Required Columns:
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ ml: 1, mb: 0.5 }}>
                            • Company Name - Full company name
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ ml: 1, mb: 1 }}>
                            • LinkedIn_URL - LinkedIn company URL
                          </Typography>
                        </Box>
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="body2" color="inherit" sx={{ fontWeight: 'bold', color: 'primary.light' }}>
                            Optional Columns:
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ ml: 1, mb: 0.5 }}>
                            • Website_URL - Company website
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ ml: 1, mb: 0.5 }}>
                            • Company_Size - Current size
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ ml: 1, mb: 0.5 }}>
                            • Industry - Company sector
                          </Typography>
                          <Typography variant="body2" color="inherit" sx={{ ml: 1, mb: 1 }}>
                            • Revenue - Revenue information
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="inherit" sx={{ fontStyle: 'italic' }}>
                          ✨ Our system will enhance your data by scraping LinkedIn for accurate details automatically!
                        </Typography>
                      </Box>
                    }
                    arrow
                    placement="left"
                  >
                    <IconButton
                      size="small"
                      sx={{ 
                        color: 'primary.main',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                    >
                      <AssessmentIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  {/* How it works Tooltip */}
                  <Tooltip 
                    title={
                      <Box>
                        <Typography variant="subtitle2" gutterBottom color="inherit">
                          How it works:
                        </Typography>
                        <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                          1. 📤 Upload Excel/CSV files → Stored as JSON in database
                        </Typography>
                        <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                          2. ⏸️ Files remain in 'pending' status until processed
                        </Typography>
                        <Typography variant="body2" color="inherit" sx={{ mb: 0.5 }}>
                          3. ⚙️ Choose to process immediately or later
                        </Typography>
                        <Typography variant="body2" color="inherit">
                          4. 📊 Monitor processing status and view results
                        </Typography>
                      </Box>
                    }
                    arrow
                    placement="left"
                  >
                    <IconButton
                      size="small"
                      sx={{ 
                        color: 'info.main',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                    >
                      <InfoIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>

                <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2 }}>
                  <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 'medium' }}>
                    📋 Download Sample Template
                  </Typography>
                  <Tooltip 
                    title={
                      <Box>
                        <Typography variant="subtitle2" gutterBottom color="inherit">
                          📋 Use Our Standardized Template Format
                        </Typography>
                        <Typography variant="body2" color="inherit" sx={{ mb: 1 }}>
                          Download our Excel template with the exact standardized column names. Using this format ensures optimal processing and prevents column mapping issues.
                        </Typography>
                        <Typography variant="caption" color="inherit">
                          <strong>✨ Recommended:</strong> All new uploads should use our standardized template format for best results!
                        </Typography>
                      </Box>
                    }
                    arrow
                    placement="top"
                  >
                    <IconButton
                      color="primary"
                      onClick={handleDownloadTemplate}
                      disabled={downloadingTemplate}
                      size="large"
                      sx={{ 
                        backgroundColor: 'action.hover',
                        '&:hover': { backgroundColor: 'action.selected' },
                        border: '2px dashed',
                        borderColor: 'primary.main'
                      }}
                    >
                      <GetAppIcon fontSize="large" />
                    </IconButton>
                  </Tooltip>
                </Box>



                <Paper
                  {...getRootProps()}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    border: '2px dashed',
                    borderColor: isDragActive ? 'primary.main' : 'grey.300',
                    bgcolor: isDragActive ? 'action.hover' : 'background.default',
                    '&:hover': {
                      bgcolor: 'action.hover',
                      borderColor: 'primary.main'
                    }
                  }}
                >
                  <input {...getInputProps()} />
                  <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    {isDragActive ? 'Drop the file here' : 'Select Excel/CSV file to upload'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Drag & drop or click to select file
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Supports .xlsx, .xls, and .csv files (max 10MB)
                  </Typography>
                  <Typography variant="caption" display="block" color="primary" sx={{ mt: 1 }}>
                    💡 Expected columns: Company Name, LinkedIn_URL, Website_URL, Company_Size, Industry, Revenue
                  </Typography>
                </Paper>

                {uploadedFile && uploadedFile.file && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Selected File:
                    </Typography>
                    <Chip
                      label={uploadedFile.file.name}
                      color="primary"
                      variant="outlined"
                      sx={{ mb: 2 }}
                    />
                    
                    {/* Validation Status */}
                    {validating && (
                      <Alert severity="info" sx={{ mb: 2 }}>
                        <Typography variant="body2">
                          🔍 Validating file headers...
                        </Typography>
                      </Alert>
                    )}
                    
                    {validationResult && (
                      <Alert 
                        severity={validationResult.valid ? "success" : "error"} 
                        sx={{ mb: 2 }}
                      >
                        {validationResult.valid ? (
                          <Box>
                            <Typography variant="body2" gutterBottom>
                              ✅ File validation successful!
                            </Typography>
                            <Typography variant="caption" display="block">
                              Found {validationResult.total_rows} rows with required columns: {validationResult.found_required?.join(', ')}
                            </Typography>
                            {validationResult.found_optional?.length > 0 && (
                              <Typography variant="caption" display="block">
                                Optional columns: {validationResult.found_optional.join(', ')}
                              </Typography>
                            )}
                            {validationResult.unexpected_headers?.length > 0 && (
                              <Typography variant="caption" display="block" color="warning.main">
                                Unexpected columns (will be ignored): {validationResult.unexpected_headers.join(', ')}
                              </Typography>
                            )}
                          </Box>
                        ) : (
                          <Box>
                            <Typography variant="body2" gutterBottom>
                              ❌ File validation failed
                            </Typography>
                            <Typography variant="caption" display="block">
                              {validationResult.error}
                            </Typography>
                            {validationResult.expected_headers && (
                              <Typography variant="caption" display="block">
                                Expected: {validationResult.expected_headers.join(', ')}
                              </Typography>
                            )}
                          </Box>
                        )}
                      </Alert>
                    )}
                    
                    <Box display="flex" gap={2} flexWrap="wrap">
                      <Button
                        variant="contained"
                        onClick={handleUploadAsJson}
                        disabled={uploadingAsJson || uploadingAndProcessing || validating || !validationResult?.valid}
                        startIcon={<StorageIcon />}
                        sx={{ flex: 1, minWidth: '200px' }}
                      >
                        {uploadingAsJson ? 'Uploading...' : '📤 Upload as JSON'}
                      </Button>
                      
                      <Button
                        variant="contained"
                        color="secondary"
                        onClick={handleUploadAndProcess}
                        disabled={uploadingAsJson || uploadingAndProcessing || validating || !validationResult?.valid}
                        startIcon={<AssessmentIcon />}
                        sx={{ flex: 1, minWidth: '200px' }}
                      >
                        {uploadingAndProcessing ? 'Processing...' : '⚡ Upload & Process Now'}
                      </Button>
                    </Box>
                    
                    {validationResult && !validationResult.valid ? (
                      <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
                        ⚠️ Please fix the file format issues above before uploading
                      </Typography>
                    ) : validationResult?.valid ? (
                      <Typography variant="caption" color="success.main" sx={{ mt: 1, display: 'block' }}>
                        ✅ File ready for upload! Choose your processing option above.
                      </Typography>
                    ) : (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        💡 Upload as JSON for later processing, or Upload & Process for immediate results
                      </Typography>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Uploaded Files List Section */}
          <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="h6">
                      📁 Uploaded Files
                    </Typography>
                    {refreshing && (
                      <Tooltip title="Auto-refreshing files...">
                        <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary', animation: 'pulse 1.5s infinite' }}>
                          🔄
                        </Typography>
                      </Tooltip>
                    )}
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    <RefreshIcon 
                      sx={{ 
                        fontSize: '1rem', 
                        color: 'primary.main',
                        animation: 'spin 2s linear infinite',
                        '@keyframes spin': {
                          '0%': { transform: 'rotate(0deg)' },
                          '100%': { transform: 'rotate(360deg)' }
                        }
                      }} 
                    />
                    <Typography variant="caption" color="primary.main">
                      Auto-refresh
                    </Typography>
                  </Box>
                </Box>

                {uploadedFiles.length > 0 ? (
                  <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>File</TableCell>
                          <TableCell align="center">Rows</TableCell>
                          <TableCell align="center">Status</TableCell>
                          <TableCell align="center">Date</TableCell>
                          <TableCell align="center">Action</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {uploadedFiles.map((file) => (
                          <TableRow key={file.id}>
                            <TableCell>
                              <Box display="flex" alignItems="center" gap={1}>
                                📊
                                <Typography variant="body2" noWrap>
                                  {file.file_name || file.filename}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell align="center">{file.records_count || file.total_rows}</TableCell>
                            <TableCell align="center">
                              <Chip
                                label={file.processing_status || 'pending'}
                                size="small"
                                color={
                                  file.processing_status === 'completed' ? 'success' :
                                  file.processing_status === 'failed' ? 'error' :
                                  processingFiles.has(file.id) ? 'primary' : 'default'
                                }
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="caption">
                                {new Date(file.upload_date).toLocaleDateString()}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Box display="flex" gap={1} justifyContent="center">
                                {file.processing_status === 'completed' ? (
                                  <Button
                                    variant="contained"
                                    size="small"
                                    color="success"
                                    startIcon={<DownloadIcon />}
                                    onClick={() => handleDownloadProcessedFile(file.id, file.file_name || file.filename)}
                                  >
                                    Download
                                  </Button>
                                ) : (
                                  <Button
                                    variant="contained"
                                    size="small"
                                    onClick={() => handleProcessFile(file.id)}
                                    disabled={
                                      processingFiles.has(file.id) || 
                                      file.processing_status === 'processing'
                                    }
                                    color={
                                      file.processing_status === 'failed' ? 'error' : 'primary'
                                    }
                                  >
                                    {processingFiles.has(file.id) || file.processing_status === 'processing' ? 'Processing...' :
                                     file.processing_status === 'failed' ? 'Retry' : 'Process'}
                                  </Button>
                                )}
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', textAlign: 'center', py: 3 }}>
                    No uploaded files found. Upload files using the options above.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Processing Status */}
        {(uploadingAsJson || uploadingAndProcessing) && processingStatus && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} sx={{ mb: 2 }}>
                {getStatusIcon(processingStatus.status)}
                <Typography variant="h6">Processing Status</Typography>
                <Chip
                  label={processingStatus.status}
                  color={getStatusColor(processingStatus.status)}
                  variant="outlined"
                />
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={processingStatus.progress}
                sx={{ mb: 1 }}
              />
              
              <Typography variant="body2" color="text.secondary">
                {processingStatus.message} ({processingStatus.progress}%)
              </Typography>

              {processingStatus.result && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Results:
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={3}>
                      <Typography variant="caption" color="text.secondary">
                        Processed Rows:
                      </Typography>
                      <Typography variant="body1">
                        {processingStatus.result.processed_rows}
                      </Typography>
                    </Grid>
                    <Grid item xs={3}>
                      <Typography variant="caption" color="text.secondary">
                        Successful:
                      </Typography>
                      <Typography variant="body1" color="success.main">
                        {processingStatus.result.successful_rows}
                      </Typography>
                    </Grid>
                    <Grid item xs={3}>
                      <Typography variant="caption" color="text.secondary">
                        Failed:
                      </Typography>
                      <Typography variant="body1" color="error.main">
                        {processingStatus.result.failed_rows}
                      </Typography>
                    </Grid>
                    <Grid item xs={3}>
                      <Typography variant="caption" color="text.secondary">
                        Processing Time:
                      </Typography>
                      <Typography variant="body1">
                        {processingStatus.result.processing_time}
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  {processingStatus.status === 'completed' && (
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<DownloadIcon />}
                        onClick={handleDownloadResults}
                        fullWidth
                      >
                        Download Processed File
                      </Button>
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        )}
      </Box>

      {/* Processing Options Dialog */}
      <Dialog open={showProcessDialog} onClose={() => setShowProcessDialog(false)}>
        <DialogTitle>Processing Options</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={processOptions.scrapingEnabled}
                  onChange={(e) => setProcessOptions(prev => ({
                    ...prev,
                    scrapingEnabled: e.target.checked
                  }))}
                />
              }
              label="Enable web scraping for additional data"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={processOptions.aiAnalysisEnabled}
                  onChange={(e) => setProcessOptions(prev => ({
                    ...prev,
                    aiAnalysisEnabled: e.target.checked
                  }))}
                />
              }
              label="Enable AI analysis for revenue estimation"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowProcessDialog(false)}>Cancel</Button>
          <Button onClick={handleStartProcessing} variant="contained">
            Start Processing
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar notifications */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError('')} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccess('')} severity="success">
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FileUploadDashboard;