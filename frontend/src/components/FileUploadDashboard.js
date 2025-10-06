import React, { useState, useCallback, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/apiConfig';
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
  Checkbox,
  Alert,
  Snackbar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Menu,
  MenuItem,
  TextField,
  Avatar,
  Tabs,
  Tab,
  TabPanel
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
  Info as InfoIcon,
  Delete as DeleteIcon,
  People as PeopleIcon,
  Edit as EditIcon,
  PersonAdd as PersonAddIcon,
  MoreVert as MoreVertIcon,
  Folder as FolderIcon,
  Visibility as ViewIcon,
  Replay as RetryIcon,
  DataUsage as DataIcon,
  Home as HomeIcon,
  TableChart as TableIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { FileService, DatabaseService } from '../services/AuthService';

// Custom TabPanel component for tab content
function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Tab accessibility props
function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

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
  
  // User Management States
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [showUserManagement, setShowUserManagement] = useState(false);
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);

  // Tab Management State
  const [activeTab, setActiveTab] = useState(0);

  // Data Management States
  const [viewingData, setViewingData] = useState(null);
  const [showViewDataDialog, setShowViewDataDialog] = useState(false);
  const [editingData, setEditingData] = useState(null);
  const [showEditDataDialog, setShowEditDataDialog] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [showRecordEditDialog, setShowRecordEditDialog] = useState(false);

  // Confirmation Dialog States
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [confirmMessage, setConfirmMessage] = useState('');
  const [confirmTitle, setConfirmTitle] = useState('');

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
      
      const response = await fetch(API_ENDPOINTS.files.validateHeaders(sessionId), {
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
  const handleProcessFile = async (fileId, isReprocess = false) => {
    // Find the file to get its name for the confirmation dialog
    const file = uploadedFiles.find(f => f.id === fileId);
    const fileName = file?.filename || file?.file_name || 'this file';
    
    // Show confirmation dialog for reprocessing
    if (isReprocess && file?.processing_status === 'completed') {
      setConfirmTitle('Confirm Reprocessing');
      setConfirmMessage(`Are you sure you want to reprocess "${fileName}"? This will update all existing data and may overwrite previous results.`);
      setConfirmAction(() => () => executeProcessFile(fileId));
      setShowConfirmDialog(true);
      return;
    }
    
    // For new processing (not reprocessing), execute directly
    executeProcessFile(fileId);
  };

  const executeProcessFile = async (fileId) => {
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
      
      const response = await fetch(API_ENDPOINTS.templates.sample);
      
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
      const response = await fetch(API_ENDPOINTS.files.downloadProcessed(fileId, sessionId), {
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

  // Handle deleting file and all associated data
  const handleDeleteFile = async (fileId, fileName) => {
    // Show confirmation dialog
    setConfirmTitle('Confirm Deletion');
    setConfirmMessage(`Are you sure you want to delete "${fileName}" and all its associated data? This action cannot be undone.`);
    setConfirmAction(() => () => executeDeleteFile(fileId, fileName));
    setShowConfirmDialog(true);
  };

  const executeDeleteFile = async (fileId, fileName) => {
    try {
      setError('');
      const result = await FileService.deleteFile(sessionId, fileId);
      setSuccess(result.message || `File "${fileName}" deleted successfully`);
      
      // Refresh the file list
      loadUploadedFiles();
    } catch (error) {
      setError(`Failed to delete file: ${error.message}`);
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

  // Helper function to determine if operations should be disabled
  const isOperationDisabled = (file) => {
    return (
      processingFiles.has(file.id) || 
      file.processing_status === 'processing' || 
      file.processing_status === 'pending' ||
      !file.processing_status // If status is undefined/null, also disable
    );
  };



  // Enhanced Data Management Functions
  const handleViewData = async (file) => {
    try {
      setError('');
      const fileId = file.id || file.file_id;
      
      const response = await fetch(API_ENDPOINTS.files.viewData(fileId, sessionId, 100, 0), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setViewingData({
            file: file,
            data: result.data,
            totalRecords: result.total_records,
            fileInfo: result.file_info
          });
          setShowViewDataDialog(true);
          setSuccess(`Loaded ${result.data.length} records for viewing`);
        } else {
          throw new Error(result.message || 'Failed to load data');
        }
      } else {
        throw new Error(`HTTP ${response.status}: Failed to fetch data`);
      }
    } catch (error) {
      setError(`Failed to view data: ${error.message}`);
    }
  };

  const handleEditData = async (file) => {
    try {
      setError('');
      const fileId = file.id || file.file_id;
      
      const response = await fetch(API_ENDPOINTS.files.viewData(fileId, sessionId, 100, 0), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setEditingData({
            file: file,
            data: result.data,
            totalRecords: result.total_records,
            fileInfo: result.file_info
          });
          setShowEditDataDialog(true);
          setSuccess(`Loaded ${result.data.length} records for editing`);
        } else {
          throw new Error(result.message || 'Failed to load data');
        }
      } else {
        throw new Error(`HTTP ${response.status}: Failed to fetch data`);
      }
    } catch (error) {
      setError(`Failed to load data for editing: ${error.message}`);
    }
  };

  const handleDownload = async (fileId, filename) => {
    try {
      setError('');
      const result = await FileService.downloadProcessed(sessionId, fileId);
      
      // Create blob and download
      const blob = new Blob([result], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `processed_${filename}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSuccess(`Downloaded processed file: ${filename}`);
    } catch (error) {
      setError(`Failed to download processed file: ${error.message}`);
    }
  };

  const handleRetryProcessing = async (fileId, fileName) => {
    if (!window.confirm(`Retry processing for "${fileName}"?`)) {
      return;
    }

    try {
      setError('');
      setProcessingFiles(prev => new Set([...prev, fileId]));
      
      // Call the process endpoint
      const result = await FileService.processFile(sessionId, fileId);
      
      if (result.success) {
        setSuccess(`Processing started for "${fileName}"`);
        // Refresh file list to show updated status
        loadUploadedFiles();
      } else {
        setError(result.message || 'Failed to start processing');
      }
    } catch (error) {
      setError(`Failed to retry processing: ${error.message}`);
    } finally {
      setProcessingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  };

  // User Management Functions
  const loadUsers = useCallback(async () => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.getUsers(sessionId), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setUsers(result.users || []);
      } else {
        throw new Error('Failed to load users');
      }
    } catch (error) {
      console.error('Error loading users:', error);
      setError('Failed to load users: ' + error.message);
    }
  }, [sessionId]);

  const handleUserMenuClick = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleShowUserManagement = () => {
    setShowUserManagement(true);
    setUserMenuAnchor(null);
    loadUsers();
  };

  const handleEditUser = (user) => {
    setEditingUser({ ...user });
    setShowEditDialog(true);
  };

  const handleDeleteUser = (user) => {
    setUserToDelete(user);
    setShowDeleteDialog(true);
  };

  const handleSaveUser = async () => {
    try {
      const isNewUser = !editingUser?.id;
      const endpoint = isNewUser ? 
        API_ENDPOINTS.auth.createUser(sessionId) : 
        API_ENDPOINTS.auth.updateUser(sessionId);
      
      const method = isNewUser ? 'POST' : 'PUT';
      
      const response = await fetch(endpoint, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editingUser)
      });
      
      if (response.ok) {
        setSuccess(isNewUser ? 'User created successfully' : 'User updated successfully');
        setShowEditDialog(false);
        setEditingUser(null);
        loadUsers();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || (isNewUser ? 'Failed to create user' : 'Failed to update user'));
      }
    } catch (error) {
      setError((editingUser?.id ? 'Failed to update user: ' : 'Failed to create user: ') + error.message);
    }
  };

  const handleConfirmDeleteUser = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.auth.deleteUser(sessionId, userToDelete.id), {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setSuccess('User deleted successfully');
        setShowDeleteDialog(false);
        setUserToDelete(null);
        loadUsers();
      } else {
        throw new Error('Failed to delete user');
      }
    } catch (error) {
      setError('Failed to delete user: ' + error.message);
    }
  };

  const handleAddUser = () => {
    setEditingUser({ username: '', email: '', password: '', role: 'user' });
    setShowEditDialog(true);
  };

  return (
    <Box sx={{ 
      flexGrow: 1,
      pb: 8, // Add bottom padding to prevent content from being hidden behind fixed footer
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
          
          {/* User Management Menu */}
          <Tooltip title="User Management">
            <IconButton color="inherit" onClick={handleUserMenuClick}>
              <PeopleIcon />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={handleUserMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem onClick={handleShowUserManagement}>
              <PeopleIcon sx={{ mr: 1 }} />
              Manage Users
            </MenuItem>
          </Menu>
          
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
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center" gap={1.5}>
                        <Typography variant="h6">Processing Status</Typography>
                        {refreshing && (
                          <Tooltip title="Auto-refreshing data...">
                            <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary', animation: 'pulse 1.5s infinite' }}>
                              🔄
                            </Typography>
                          </Tooltip>
                        )}
                        {/* Active/Ready Status Chip */}
                        <Chip
                          label={uploadedFiles.filter(f => f.processing_status === 'completed').length > 0 
                            ? 'Active' : 'Ready'}
                          color={uploadedFiles.filter(f => f.processing_status === 'processing').length > 0 
                            ? 'warning' : 'success'}
                          variant="outlined"
                          size="small"
                        />
                        
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
                      {uploadedFiles.length > 0 && (
                        (() => {
                          const processingFilesList = uploadedFiles.filter(f => f.processing_status === 'processing');
                          const pendingFiles = uploadedFiles.filter(f => f.processing_status === 'pending' || !f.processing_status);
                          const completedFiles = uploadedFiles.filter(f => f.processing_status === 'completed');
                          const failedFiles = uploadedFiles.filter(f => f.processing_status === 'failed');
                          
                          if (processingFilesList.length > 0) {
                            const isManual = processingFilesList.some(f => processingFiles.has(f.id));
                            return <Typography sx={{ fontSize: '1.4rem' }}>{isManual ? '👤' : '🤖'}</Typography>;
                          } else if (pendingFiles.length > 0) {
                            return <Typography sx={{ fontSize: '1.4rem' }}>⏳</Typography>;
                          } else if (completedFiles.length > 0) {
                            return <Typography sx={{ fontSize: '1.4rem' }}>✅</Typography>;
                          } else if (failedFiles.length > 0) {
                            return <Typography sx={{ fontSize: '1.4rem' }}>❌</Typography>;
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
                              gap: 1.5,
                              mt: 1,
                              p: 1.5,
                              borderRadius: 2,
                              backgroundColor: 'info.light',
                              border: '1px solid',
                              borderColor: 'info.main',
                            }}>
                              <Typography sx={{ fontSize: '1rem' }}>⏰</Typography>
                              <Typography variant="body2" color="info.dark" sx={{ fontWeight: 500 }}>
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
                                justifyContent: 'space-between',
                                gap: 2,
                                p: 1.5,
                                borderRadius: 2,
                                backgroundColor: isManualProcessing ? 'primary.light' : 'warning.light',
                                border: `2px solid ${isManualProcessing ? 'primary.main' : 'warning.main'}`,
                                mt: 1
                              }}>
                                <Box sx={{ 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  gap: 1.5,
                                  flex: 1,
                                  minWidth: 0 // Allow text to truncate
                                }}>
                                  <Box sx={{ 
                                    width: 10, 
                                    height: 10, 
                                    borderRadius: '50%', 
                                    backgroundColor: isManualProcessing ? 'primary.main' : 'warning.main',
                                    animation: 'pulse 2s infinite',
                                    flexShrink: 0
                                  }} />
                                  <Typography variant="body2" sx={{ 
                                    fontWeight: 600,
                                    color: isManualProcessing ? 'primary.dark' : 'warning.dark',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap'
                                  }}>
                                    {file.file_name || file.filename}
                                  </Typography>
                                </Box>
                                <Chip 
                                  label={isManualProcessing ? 'Manual Processing' : 'Automated Processing'}
                                  size="small"
                                  color={isManualProcessing ? 'primary' : 'warning'}
                                  variant="filled"
                                  sx={{ 
                                    fontWeight: 600,
                                    fontSize: '0.75rem',
                                    flexShrink: 0,
                                    '& .MuiChip-label': {
                                      px: 1.5
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

                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs Navigation */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs 
            value={activeTab} 
            onChange={(event, newValue) => setActiveTab(newValue)}
            aria-label="main navigation tabs"
            sx={{ 
              '& .MuiTab-root': {
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 500
              }
            }}
          >
            <Tab 
              icon={<HomeIcon />} 
              label="File Upload" 
              {...a11yProps(0)}
              sx={{ minHeight: 64 }}
            />
            <Tab 
              icon={<FolderIcon />} 
              label="Uploaded Files & Data Management" 
              {...a11yProps(1)}
              sx={{ minHeight: 64 }}
            />
          </Tabs>
        </Box>

        {/* Tab Content */}
        <CustomTabPanel value={activeTab} index={0}>
          {/* File Upload Section - Original GUI Workflow */}
          <Grid container spacing={3} sx={{ alignItems: 'flex-start' }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: 'fit-content' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} sx={{ mb: 3 }}>
                  <UploadIcon color="primary" />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6">File Upload and Scheduled to Processing</Typography>
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
                                  <>
                                    <Button
                                      variant="contained"
                                      size="small"
                                      color="success"
                                      startIcon={<DownloadIcon />}
                                      onClick={() => handleDownloadProcessedFile(file.id, file.file_name || file.filename)}
                                    >
                                      Download
                                    </Button>
                                    <IconButton
                                      size="small"
                                      color="error"
                                      onClick={() => handleDeleteFile(file.id, file.file_name || file.filename)}
                                      title="Delete file and all associated data"
                                    >
                                      <DeleteIcon />
                                    </IconButton>
                                  </>
                                ) : (
                                  <>
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
                                    <IconButton
                                      size="small"
                                      color="error"
                                      onClick={() => handleDeleteFile(file.id, file.file_name || file.filename)}
                                      title="Delete file and all associated data"
                                      disabled={processingFiles.has(file.id) || file.processing_status === 'processing'}
                                    >
                                      <DeleteIcon />
                                    </IconButton>
                                  </>
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
              <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                <Box display="flex" alignItems="center" gap={2}>
                  {getStatusIcon(processingStatus.status)}
                  <Typography variant="h6">Processing Status</Typography>
                </Box>
                <Chip
                  label={processingStatus.status}
                  color={getStatusColor(processingStatus.status)}
                  variant="outlined"
                  sx={{ fontWeight: 600 }}
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
        </CustomTabPanel>

        {/* Second Tab - Uploaded Files & Data Management */}
        <CustomTabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2} sx={{ mb: 3 }}>
                    <TableIcon color="primary" />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h5">Data Management & Analysis</Typography>
                      <Typography variant="body2" color="text.secondary">
                        View, edit, delete and retry processing for uploaded files and processed data
                      </Typography>
                    </Box>
                  </Box>

                  {/* Enhanced File Management Table */}
                  {uploadedFiles && uploadedFiles.length > 0 ? (
                    <Box sx={{ width: '100%', overflow: 'auto' }}>
                      <Table size="medium" sx={{ minWidth: 1000 }}>
                        <TableHead>
                          <TableRow sx={{ backgroundColor: 'grey.50' }}>
                            <TableCell><strong>File Details</strong></TableCell>
                            <TableCell><strong>Processing Status</strong></TableCell>
                            <TableCell><strong>Data Statistics</strong></TableCell>
                            <TableCell><strong>Actions</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {uploadedFiles.map((file) => (
                            <TableRow key={file.id} hover sx={{ '&:hover': { backgroundColor: 'grey.25' } }}>
                              <TableCell>
                                <Box>
                                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                                    {file.file_name || file.filename}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    📅 Uploaded: {new Date(file.upload_date || file.uploadDate).toLocaleString()}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    👤 By: {file.uploaded_by || file.uploadedBy}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    📊 Records: {file.records_count || file.recordsCount || 0}
                                  </Typography>
                                </Box>
                              </TableCell>
                              
                              <TableCell>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                  <Chip
                                    label={processingFiles.has(file.id) ? 'Processing...' : 
                                           file.processing_status === 'completed' ? 'Completed' :
                                           file.processing_status === 'failed' ? 'Failed' :
                                           file.processing_status === 'processing' ? 'Processing' :
                                           'Pending'}
                                    color={processingFiles.has(file.id) || file.processing_status === 'processing' ? 'warning' :
                                           file.processing_status === 'completed' ? 'success' :
                                           file.processing_status === 'failed' ? 'error' : 'default'}
                                    size="small"
                                    icon={processingFiles.has(file.id) || file.processing_status === 'processing' ? <ScheduleIcon /> :
                                          file.processing_status === 'completed' ? <CheckIcon /> :
                                          file.processing_status === 'failed' ? <ErrorIcon /> : <InfoIcon />}
                                  />
                                  {file.error_message && (
                                    <Typography variant="caption" color="error" sx={{ fontSize: '0.7rem', maxWidth: 200 }}>
                                      ⚠️ {file.error_message}
                                    </Typography>
                                  )}
                                </Box>
                              </TableCell>
                              
                              <TableCell>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                  <Typography variant="body2">
                                    📈 Total: {file.records_count || 0}
                                  </Typography>
                                  <Typography variant="body2" color="success.main">
                                    ✅ Processed: {file.processed_count || 0}
                                  </Typography>
                                  <Typography variant="body2" color="error.main">
                                    ❌ Failed: {file.failed_count || 0}
                                  </Typography>
                                  {file.processing_status === 'completed' && (
                                    <Typography variant="caption" color="text.secondary">
                                      🎯 Success Rate: {((file.processed_count || 0) / (file.records_count || 1) * 100).toFixed(1)}%
                                    </Typography>
                                  )}
                                </Box>
                              </TableCell>
                              
                              <TableCell>
                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, minWidth: 200 }}>
                                  {/* View Data Button */}
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    startIcon={<ViewIcon />}
                                    onClick={() => handleViewData(file)}
                                    disabled={isOperationDisabled(file)}
                                    sx={{ justifyContent: 'flex-start' }}
                                  >
                                    View Data
                                  </Button>
                                  
                                  {/* Download Processed Button */}
                                  {file.processing_status === 'completed' && (
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      color="success"
                                      startIcon={<DownloadIcon />}
                                      onClick={() => handleDownload(file.id, file.file_name || file.filename)}
                                      disabled={isOperationDisabled(file)}
                                      sx={{ justifyContent: 'flex-start' }}
                                    >
                                      Download Results
                                    </Button>
                                  )}
                                  
                                  {/* Edit Data Button */}
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    color="info"
                                    startIcon={<EditIcon />}
                                    onClick={() => handleEditData(file)}
                                    disabled={isOperationDisabled(file)}
                                    sx={{ justifyContent: 'flex-start' }}
                                  >
                                    Edit Data
                                  </Button>
                                  
                                  {/* Process/Retry Button */}
                                  <Button
                                    size="small"
                                    variant="contained"
                                    color={file.processing_status === 'failed' ? 'warning' : 'primary'}
                                    startIcon={file.processing_status === 'failed' ? <RetryIcon /> : <AssessmentIcon />}
                                    onClick={() => file.processing_status === 'failed' ? 
                                      handleRetryProcessing(file.id, file.file_name || file.filename) : 
                                      handleProcessFile(file.id, file.processing_status === 'completed')}
                                    disabled={isOperationDisabled(file)}
                                    sx={{ justifyContent: 'flex-start' }}
                                  >
                                    {processingFiles.has(file.id) || file.processing_status === 'processing' ? 'Processing...' :
                                     file.processing_status === 'failed' ? 'Retry Processing' : 
                                     file.processing_status === 'completed' ? 'Reprocess' : 
                                     file.processing_status === 'pending' ? 'Pending...' : 'Process Now'}
                                  </Button>
                                  
                                  {/* Delete Button */}
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    color="error"
                                    startIcon={<DeleteIcon />}
                                    onClick={() => handleDeleteFile(file.id, file.file_name || file.filename)}
                                    disabled={isOperationDisabled(file)}
                                    sx={{ justifyContent: 'flex-start' }}
                                  >
                                    Delete All Data
                                  </Button>
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </Box>
                  ) : (
                    <Box sx={{ textAlign: 'center', py: 6 }}>
                      <DataIcon sx={{ fontSize: 60, color: 'grey.300', mb: 2 }} />
                      <Typography variant="h6" color="text.secondary" gutterBottom>
                        No Data Available
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Upload files in the "File Upload" tab to see data management options here.
                      </Typography>
                      <Button 
                        variant="outlined" 
                        onClick={() => setActiveTab(0)}
                        startIcon={<UploadIcon />}
                      >
                        Go to File Upload
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CustomTabPanel>

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

      {/* User Management Dialog */}
      <Dialog 
        open={showUserManagement} 
        onClose={() => setShowUserManagement(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={1}>
              <PeopleIcon />
              <Typography variant="h6">User Management</Typography>
            </Box>
            <Button
              startIcon={<PersonAddIcon />}
              variant="outlined"
              size="small"
              onClick={handleAddUser}
            >
              Add User
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Avatar</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                      {user.username?.charAt(0).toUpperCase()}
                    </Avatar>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {user.username}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {user.email || 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.role || 'user'} 
                      size="small"
                      color={user.role === 'superuser' ? 'error' : 
                             user.role === 'admin' ? 'primary' : 'default'}
                      variant={user.role === 'superuser' ? 'filled' : 'outlined'}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={user.is_active === false ? 'Inactive' : 'Active'} 
                      size="small"
                      color={user.is_active === false ? 'error' : 'success'}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={1}>
                      <Tooltip title="Edit User">
                        <IconButton 
                          size="small" 
                          onClick={() => handleEditUser(user)}
                          color="primary"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete User">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteUser(user)}
                          color="error"
                          disabled={user.username === userInfo?.username} // Prevent self-deletion
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No users found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUserManagement(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={showEditDialog} onClose={() => setShowEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingUser?.id ? 'Edit User' : 'Add New User'}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} sx={{ mt: 1 }}>
            <TextField
              label="Username"
              value={editingUser?.username || ''}
              onChange={(e) => setEditingUser(prev => ({ ...prev, username: e.target.value }))}
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={editingUser?.email || ''}
              onChange={(e) => setEditingUser(prev => ({ ...prev, email: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Role"
              select
              value={editingUser?.role || 'user'}
              onChange={(e) => setEditingUser(prev => ({ ...prev, role: e.target.value }))}
              fullWidth
              SelectProps={{
                native: true
              }}
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
              <option value="superuser">Superuser</option>
            </TextField>
            
            {/* Status Checkboxes */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Status Options</Typography>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={editingUser?.is_active !== false}
                    onChange={(e) => setEditingUser(prev => ({ ...prev, is_active: e.target.checked }))}
                    color="success"
                  />
                }
                label="Active User"
              />
              {editingUser?.role === 'superuser' && (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={editingUser?.is_superuser || false}
                      onChange={(e) => setEditingUser(prev => ({ ...prev, is_superuser: e.target.checked }))}
                      color="error"
                    />
                  }
                  label="Superuser Privileges"
                />
              )}
            </Box>
            {!editingUser?.id && (
              <TextField
                label="Password"
                type="password"
                value={editingUser?.password || ''}
                onChange={(e) => setEditingUser(prev => ({ ...prev, password: e.target.value }))}
                fullWidth
                required
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEditDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveUser} variant="contained">
            {editingUser?.id ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete User Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete user "{userToDelete?.username}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleConfirmDeleteUser} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Data Dialog */}
      <Dialog 
        open={showViewDataDialog} 
        onClose={() => setShowViewDataDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          View Company Data - {viewingData?.fileInfo?.file_name}
        </DialogTitle>
        <DialogContent>
          {viewingData && (
            <Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Showing {viewingData.data?.length || 0} of {viewingData.totalRecords} records
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Company Name</TableCell>
                    <TableCell>LinkedIn URL</TableCell>
                    <TableCell>Website</TableCell>
                    <TableCell>Company Size</TableCell>
                    <TableCell>Industry</TableCell>
                    <TableCell>Revenue</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {viewingData.data?.map((record, index) => (
                    <TableRow key={record.id || index}>
                      <TableCell>{record.company_name}</TableCell>
                      <TableCell>
                        {record.linkedin_url ? (
                          <a href={record.linkedin_url} target="_blank" rel="noopener noreferrer">
                            {record.linkedin_url.length > 30 ? 
                              record.linkedin_url.substring(0, 30) + '...' : 
                              record.linkedin_url
                            }
                          </a>
                        ) : '-'}
                      </TableCell>
                      <TableCell>
                        {record.company_website ? (
                          <a href={record.company_website} target="_blank" rel="noopener noreferrer">
                            {record.company_website.length > 30 ? 
                              record.company_website.substring(0, 30) + '...' : 
                              record.company_website
                            }
                          </a>
                        ) : '-'}
                      </TableCell>
                      <TableCell>{record.company_size || '-'}</TableCell>
                      <TableCell>{record.industry || '-'}</TableCell>
                      <TableCell>{record.revenue || '-'}</TableCell>
                      <TableCell>
                        <Chip 
                          label={record.processing_status || 'pending'} 
                          color={getStatusColor(record.processing_status)} 
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowViewDataDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Data Dialog */}
      <Dialog 
        open={showEditDataDialog} 
        onClose={() => setShowEditDataDialog(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Edit Company Data - {editingData?.fileInfo?.file_name}
        </DialogTitle>
        <DialogContent>
          {editingData && (
            <Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Editing {editingData.data?.length || 0} of {editingData.totalRecords} records
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Company Name</TableCell>
                    <TableCell>LinkedIn URL</TableCell>
                    <TableCell>Website</TableCell>
                    <TableCell>Company Size</TableCell>
                    <TableCell>Industry</TableCell>
                    <TableCell>Revenue</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {editingData.data?.map((record, index) => (
                    <TableRow key={record.id || index}>
                      <TableCell>{record.company_name}</TableCell>
                      <TableCell>
                        {record.linkedin_url ? (
                          <a href={record.linkedin_url} target="_blank" rel="noopener noreferrer">
                            {record.linkedin_url.length > 30 ? 
                              record.linkedin_url.substring(0, 30) + '...' : 
                              record.linkedin_url
                            }
                          </a>
                        ) : '-'}
                      </TableCell>
                      <TableCell>
                        {record.company_website ? (
                          <a href={record.company_website} target="_blank" rel="noopener noreferrer">
                            {record.company_website.length > 30 ? 
                              record.company_website.substring(0, 30) + '...' : 
                              record.company_website
                            }
                          </a>
                        ) : '-'}
                      </TableCell>
                      <TableCell>{record.company_size || '-'}</TableCell>
                      <TableCell>{record.industry || '-'}</TableCell>
                      <TableCell>{record.revenue || '-'}</TableCell>
                      <TableCell>
                        <Chip 
                          label={record.processing_status || 'pending'} 
                          color={getStatusColor(record.processing_status)} 
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          size="small"
                          startIcon={<EditIcon />}
                          onClick={() => {
                            setEditingRecord(record);
                            setShowRecordEditDialog(true);
                          }}
                        >
                          Edit
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEditDataDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Record Dialog */}
      <Dialog 
        open={showRecordEditDialog} 
        onClose={() => setShowRecordEditDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Company Record</DialogTitle>
        <DialogContent>
          {editingRecord && (
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Company Name"
                value={editingRecord.company_name || ''}
                onChange={(e) => setEditingRecord({...editingRecord, company_name: e.target.value})}
                margin="normal"
              />
              <TextField
                fullWidth
                label="LinkedIn URL"
                value={editingRecord.linkedin_url || ''}
                onChange={(e) => setEditingRecord({...editingRecord, linkedin_url: e.target.value})}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Company Website"
                value={editingRecord.company_website || ''}
                onChange={(e) => setEditingRecord({...editingRecord, company_website: e.target.value})}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Company Size"
                value={editingRecord.company_size || ''}
                onChange={(e) => setEditingRecord({...editingRecord, company_size: e.target.value})}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Industry"
                value={editingRecord.industry || ''}
                onChange={(e) => setEditingRecord({...editingRecord, industry: e.target.value})}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Revenue"
                value={editingRecord.revenue || ''}
                onChange={(e) => setEditingRecord({...editingRecord, revenue: e.target.value})}
                margin="normal"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRecordEditDialog(false)}>Cancel</Button>
          <Button 
            onClick={async () => {
              try {
                const response = await fetch(API_ENDPOINTS.files.editRecord(editingRecord.id, sessionId), {
                  method: 'PUT',
                  headers: {
                    'Content-Type': 'application/json'
                  },
                  body: JSON.stringify(editingRecord)
                });
                
                if (response.ok) {
                  const result = await response.json();
                  if (result.success) {
                    setSuccess('Record updated successfully');
                    setShowRecordEditDialog(false);
                    setEditingRecord(null);
                    // Refresh the edit dialog data
                    handleEditData(editingData.file);
                  } else {
                    throw new Error(result.message || 'Failed to update record');
                  }
                } else {
                  throw new Error(`HTTP ${response.status}: Failed to update record`);
                }
              } catch (error) {
                setError(`Failed to update record: ${error.message}`);
              }
            }}
            color="primary" 
            variant="contained"
          >
            Save Changes
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

      {/* Confirmation Dialog */}
      <Dialog
        open={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-description"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle 
          id="confirm-dialog-title"
          sx={{ 
            color: 'error.main',
            fontWeight: 'bold',
            pb: 1
          }}
        >
          ⚠️ {confirmTitle}
        </DialogTitle>
        <DialogContent>
          <Typography 
            id="confirm-dialog-description"
            variant="body1"
            sx={{ mt: 1 }}
          >
            {confirmMessage}
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={() => setShowConfirmDialog(false)}
            color="inherit"
            variant="outlined"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              setShowConfirmDialog(false);
              if (confirmAction) {
                confirmAction();
              }
            }}
            color="error"
            variant="contained"
            autoFocus
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Fixed Footer */}
      <Box
        component="footer"
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: 'primary.main',
          color: 'white',
          py: 1,
          px: 2,
          zIndex: 1000,
          borderTop: '1px solid',
          borderColor: 'divider',
          boxShadow: '0 -2px 8px rgba(0,0,0,0.1)'
        }}
      >
        <Typography 
          variant="body2" 
          align="center"
          sx={{ 
            fontSize: '0.875rem',
            fontWeight: 500
          }}
        >
          © 2025 Neha Info Tech. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default FileUploadDashboard;