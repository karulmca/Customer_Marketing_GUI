import React, { useState, useEffect } from 'react';
import { 
  ThemeProvider, 
  createTheme,
  CssBaseline,
  Container,
  Box,
  Alert,
  Snackbar
} from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';

import LoginForm from './components/LoginForm';
import FileUploadDashboard from './components/FileUploadDashboard';
import PrivacyPolicy from './components/PrivacyPolicy';
import TermsOfService from './components/TermsOfService';
import ContactUs from './components/ContactUs';
import { AuthService } from './services/AuthService';

// Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check for existing session on app load
    const storedSessionId = localStorage.getItem('sessionId');
    const storedUserInfo = localStorage.getItem('userInfo');
    
    if (storedSessionId && storedUserInfo) {
      setSessionId(storedSessionId);
      setUserInfo(JSON.parse(storedUserInfo));
      setIsAuthenticated(true);
    }
    
    setLoading(false);
  }, []);

  const handleLogin = async (credentials) => {
    try {
      setError('');
      const response = await AuthService.login(credentials);
      
      if (response.success) {
        setSessionId(response.session_id);
        setUserInfo(response.user_info);
        setIsAuthenticated(true);
        
        // Persist session
        localStorage.setItem('sessionId', response.session_id);
        localStorage.setItem('userInfo', JSON.stringify(response.user_info));
      }
    } catch (error) {
      setError(error.message || 'Login failed');
      throw error;
    }
  };

  const handleLogout = async () => {
    try {
      if (sessionId) {
        await AuthService.logout(sessionId);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear session regardless of API response
      setSessionId(null);
      setUserInfo(null);
      setIsAuthenticated(false);
      localStorage.removeItem('sessionId');
      localStorage.removeItem('userInfo');
    }
  };

  const handleCloseError = () => {
    setError('');
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="sm">
          <Box 
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            minHeight="100vh"
          >
            Loading...
          </Box>
        </Container>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3}>
        <Router>
          <Container maxWidth="lg">
            <Routes>
              <Route 
                path="/login" 
                element={
                  !isAuthenticated ? (
                    <LoginForm onLogin={handleLogin} />
                  ) : (
                    <Navigate to="/dashboard" replace />
                  )
                } 
              />
              <Route 
                path="/dashboard" 
                element={
                  isAuthenticated ? (
                    <FileUploadDashboard 
                      sessionId={sessionId}
                      userInfo={userInfo} 
                      onLogout={handleLogout}
                    />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                } 
              />
              <Route path="/privacy-policy" element={<PrivacyPolicy />} />
              <Route path="/terms-of-service" element={<TermsOfService />} />
              <Route path="/contact-us" element={<ContactUs />} />
              <Route 
                path="/" 
                element={
                  <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
                } 
              />
            </Routes>
          </Container>
        </Router>
        
        {error && (
          <Snackbar 
            open={!!error} 
            autoHideDuration={6000} 
            onClose={handleCloseError}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert onClose={handleCloseError} severity="error">
              {error}
            </Alert>
          </Snackbar>
        )}
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;