import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  Grid,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Search as SearchIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { API_ENDPOINTS } from '../config/apiConfig';

const FileStatusManager = ({ token, sessionId }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingFile, setEditingFile] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, fileId: null, status: null });

  // Available status options
  const statusOptions = [
    { value: 'pending', label: 'Pending', color: 'warning' },
    { value: 'processing', label: 'Processing', color: 'info' },
    { value: 'completed', label: 'Completed', color: 'success' },
    { value: 'failed', label: 'Failed', color: 'error' },
    { value: 'cancelled', label: 'Cancelled', color: 'default' }
  ];

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.files.list(sessionId), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      } else {
        showSnackbar('Failed to fetch files', 'error');
      }
    } catch (error) {
      showSnackbar('Error fetching files: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (file) => {
    setEditingFile(file.id);
    setNewStatus(file.processing_status);
  };

  const handleCancelEdit = () => {
    setEditingFile(null);
    setNewStatus('');
  };

  const handleStatusChange = (event) => {
    setNewStatus(event.target.value);
  };

  const handleSaveClick = (fileId) => {
    setConfirmDialog({ open: true, fileId, status: newStatus });
  };

  const handleConfirmUpdate = async () => {
    const { fileId, status } = confirmDialog;
    setConfirmDialog({ open: false, fileId: null, status: null });

    try {
      const response = await fetch(API_ENDPOINTS.files.updateStatus(fileId, sessionId), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        showSnackbar('File status updated successfully', 'success');
        setEditingFile(null);
        setNewStatus('');
        fetchFiles(); // Refresh the list
      } else {
        const error = await response.json();
        showSnackbar('Failed to update status: ' + (error.detail || 'Unknown error'), 'error');
      }
    } catch (error) {
      showSnackbar('Error updating status: ' + error.message, 'error');
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getStatusChip = (status) => {
    const statusConfig = statusOptions.find(s => s.value === status) || 
      { label: status, color: 'default' };
    
    return (
      <Chip
        label={statusConfig.label}
        color={statusConfig.color}
        size="small"
        icon={
          status === 'completed' ? <CheckIcon /> :
          status === 'failed' ? <ErrorIcon /> :
          status === 'processing' ? <ScheduleIcon /> : null
        }
      />
    );
  };

  const filteredFiles = files.filter(file => {
    const matchesStatus = filterStatus === 'all' || file.processing_status === filterStatus;
    const matchesSearch = !searchTerm || 
      file.file_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (file.uploaded_by && file.uploaded_by.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesStatus && matchesSearch;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" component="h2">
              File Status Manager
            </Typography>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchFiles}
              disabled={loading}
            >
              Refresh
            </Button>
          </Box>

          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search by file name or user..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Filter by Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                  startAdornment={<FilterIcon sx={{ mr: 1, color: 'action.active' }} />}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  {statusOptions.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Files Table */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : filteredFiles.length === 0 ? (
            <Alert severity="info">No files found matching your criteria.</Alert>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>File Name</strong></TableCell>
                    <TableCell><strong>Uploaded By</strong></TableCell>
                    <TableCell><strong>Upload Date</strong></TableCell>
                    <TableCell><strong>Current Status</strong></TableCell>
                    <TableCell><strong>Records</strong></TableCell>
                    <TableCell align="center"><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredFiles.map((file) => (
                    <TableRow key={file.id} hover>
                      <TableCell>
                        <Tooltip title={file.file_name}>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {file.file_name}
                          </Typography>
                        </Tooltip>
                      </TableCell>
                      <TableCell>{file.uploaded_by || 'Unknown'}</TableCell>
                      <TableCell>
                        {file.upload_date ? new Date(file.upload_date).toLocaleString() : 'N/A'}
                      </TableCell>
                      <TableCell>
                        {editingFile === file.id ? (
                          <FormControl size="small" fullWidth>
                            <Select
                              value={newStatus}
                              onChange={handleStatusChange}
                              autoWidth
                            >
                              {statusOptions.map(option => (
                                <MenuItem key={option.value} value={option.value}>
                                  {option.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        ) : (
                          getStatusChip(file.processing_status)
                        )}
                      </TableCell>
                      <TableCell>{file.records_count || 0}</TableCell>
                      <TableCell align="center">
                        {editingFile === file.id ? (
                          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                            <Tooltip title="Save changes">
                              <IconButton
                                color="primary"
                                size="small"
                                onClick={() => handleSaveClick(file.id)}
                                disabled={newStatus === file.processing_status}
                              >
                                <SaveIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Cancel">
                              <IconButton
                                color="default"
                                size="small"
                                onClick={handleCancelEdit}
                              >
                                <CancelIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        ) : (
                          <Tooltip title="Edit status">
                            <IconButton
                              color="primary"
                              size="small"
                              onClick={() => handleEditClick(file)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Summary */}
          <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Typography variant="body2" color="text.secondary">
              Total Files: <strong>{filteredFiles.length}</strong>
            </Typography>
            {statusOptions.map(option => {
              const count = filteredFiles.filter(f => f.processing_status === option.value).length;
              return count > 0 ? (
                <Typography key={option.value} variant="body2" color="text.secondary">
                  {option.label}: <strong>{count}</strong>
                </Typography>
              ) : null;
            })}
          </Box>
        </CardContent>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialog.open} onClose={() => setConfirmDialog({ open: false, fileId: null, status: null })}>
        <DialogTitle>Confirm Status Update</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to update the file status to{' '}
            <strong>{statusOptions.find(s => s.value === confirmDialog.status)?.label}</strong>?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This action will update the file's processing status in the database.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog({ open: false, fileId: null, status: null })}>
            Cancel
          </Button>
          <Button onClick={handleConfirmUpdate} variant="contained" color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FileStatusManager;
