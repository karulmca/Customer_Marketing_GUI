import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  Avatar,
  Divider,
  Link,
  CircularProgress,
  AppBar,
  Toolbar,
  Paper,
  Grid,
  IconButton
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import BusinessIcon from '@mui/icons-material/Business';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import { AuthService } from '../services/AuthService';
import { useNavigate } from 'react-router-dom';

const LoginForm = ({ onLogin }) => {
  const navigate = useNavigate();
  
  // Carousel images for login page
  const loginImages = [
    {
      url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80',
      title: 'Transform Your Business Data',
      subtitle: 'Advanced analytics and insights powered by AI'
    },
    {
      url: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80',
      title: 'Real-Time Data Visualization',
      subtitle: 'Monitor your business metrics in real-time'
    },
    {
      url: 'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&q=80',
      title: 'Intelligent Marketing Insights',
      subtitle: 'Make data-driven decisions with confidence'
    },
    {
      url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80',
      title: 'Customer Intelligence Platform',
      subtitle: 'Understand your customers like never before'
    }
  ];

  // Carousel images for registration page
  const registerImages = [
    {
      url: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80',
      title: 'Join Our Platform',
      subtitle: 'Start leveraging powerful data insights today'
    },
    {
      url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80',
      title: 'Powerful Analytics Tools',
      subtitle: 'Everything you need to grow your business'
    },
    {
      url: 'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=800&q=80',
      title: 'Seamless Integration',
      subtitle: 'Connect all your data sources effortlessly'
    }
  ];

  const [currentSlide, setCurrentSlide] = useState(0);
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [registerData, setRegisterData] = useState({
    username: '',
    password: '',
    email: ''
  });

  // Auto-advance carousel
  useEffect(() => {
    const images = showRegister ? registerImages : loginImages;
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % images.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(timer);
  }, [showRegister]);

  const handleNextSlide = () => {
    const images = showRegister ? registerImages : loginImages;
    setCurrentSlide((prev) => (prev + 1) % images.length);
  };

  const handlePrevSlide = () => {
    const images = showRegister ? registerImages : loginImages;
    setCurrentSlide((prev) => (prev - 1 + images.length) % images.length);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleRegisterInputChange = (e) => {
    const { name, value } = e.target;
    setRegisterData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    try {
      await onLogin(formData);
    } catch (error) {
      setErrors({ submit: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);
    try {
      await AuthService.register(registerData);
      setShowRegister(false);
      setErrors({ success: 'Registration successful! Please login.' });
      setRegisterData({ username: '', password: '', email: '' });
    } catch (error) {
      setErrors({ register: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (showRegister) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* Header */}
        <AppBar position="static" color="primary" elevation={0}>
          <Toolbar>
            <BusinessIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Customer Marketing Intelligence System
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Powered by AI
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ flex: 1, py: 2 }}>
          <Grid container spacing={0} sx={{ height: '100%', minHeight: 'calc(100vh - 180px)' }}>
            {/* Left Side - Analytics Image Carousel */}
            <Grid item xs={12} md={6} sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              p: 4,
              position: 'relative'
            }}>
              <Box sx={{ textAlign: 'center', color: 'white', width: '100%', maxWidth: 700 }}>
                <Box sx={{ position: 'relative' }}>
                  <Box
                    component="img"
                    src={registerImages[currentSlide].url}
                    alt={registerImages[currentSlide].title}
                    sx={{
                      width: '100%',
                      maxWidth: 600,
                      height: 'auto',
                      borderRadius: 2,
                      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
                      mb: 3,
                      transition: 'opacity 0.5s ease-in-out'
                    }}
                  />
                  
                  {/* Navigation Buttons */}
                  <IconButton
                    onClick={handlePrevSlide}
                    sx={{
                      position: 'absolute',
                      left: -20,
                      top: '40%',
                      color: 'white',
                      bgcolor: 'rgba(0,0,0,0.3)',
                      '&:hover': { bgcolor: 'rgba(0,0,0,0.5)' }
                    }}
                  >
                    <ArrowBackIosNewIcon />
                  </IconButton>
                  
                  <IconButton
                    onClick={handleNextSlide}
                    sx={{
                      position: 'absolute',
                      right: -20,
                      top: '40%',
                      color: 'white',
                      bgcolor: 'rgba(0,0,0,0.3)',
                      '&:hover': { bgcolor: 'rgba(0,0,0,0.5)' }
                    }}
                  >
                    <ArrowForwardIosIcon />
                  </IconButton>
                </Box>
                
                <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                  {registerImages[currentSlide].title}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
                  {registerImages[currentSlide].subtitle}
                </Typography>
                
                {/* Slide Indicators */}
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
                  {registerImages.map((_, index) => (
                    <Box
                      key={index}
                      onClick={() => setCurrentSlide(index)}
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        bgcolor: currentSlide === index ? 'white' : 'rgba(255,255,255,0.4)',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                      }}
                    />
                  ))}
                </Box>
              </Box>
            </Grid>

            {/* Right Side - Registration Form */}
            <Grid item xs={12} md={6} sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              p: 2
            }}>
          <Card sx={{ width: '100%', maxWidth: 450 }}>
            <CardContent sx={{ p: 4 }}>
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  mb: 3
                }}
              >
                <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
                  <LockOutlinedIcon />
                </Avatar>
                <Typography component="h1" variant="h5">
                  Register
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                  Create a new account for Company Data Scraper
                </Typography>
              </Box>

              {errors.register && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {errors.register}
                </Alert>
              )}

              <Box component="form" onSubmit={handleRegisterSubmit}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="username"
                  label="Username"
                  name="username"
                  autoComplete="username"
                  autoFocus
                  value={registerData.username}
                  onChange={handleRegisterInputChange}
                  error={!!errors.username}
                  helperText={errors.username}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={registerData.email}
                  onChange={handleRegisterInputChange}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                  value={registerData.password}
                  onChange={handleRegisterInputChange}
                  error={!!errors.password}
                  helperText={errors.password}
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  disabled={loading}
                  sx={{ mt: 3, mb: 2 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Register'}
                </Button>
                
                <Divider sx={{ my: 2 }} />
                
                <Box textAlign="center">
                  <Link
                    component="button"
                    variant="body2"
                    onClick={(e) => {
                      e.preventDefault();
                      setShowRegister(false);
                      setErrors({});
                    }}
                  >
                    Already have an account? Sign in
                  </Link>
                </Box>
              </Box>
            </CardContent>
          </Card>
            </Grid>
          </Grid>
        </Container>

      {/* Footer */}
      <Paper 
        component="footer" 
        elevation={0} 
        sx={{ 
          py: 3, 
          px: 2, 
          mt: 'auto',
          backgroundColor: 'primary.main',
          color: 'white'
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="body2" color="inherit">
              © {new Date().getFullYear()}{' '}
              <Link href="https://nit-prod.onrender.com/" target="_blank" rel="noopener" color="inherit" underline="hover" sx={{ fontWeight: 500 }}>
                NehaInfoTech
              </Link>
              . All rights reserved.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Link component="button" variant="body2" color="inherit" underline="hover" onClick={() => navigate('/privacy-policy')}>
                Privacy Policy
              </Link>
              <Link component="button" variant="body2" color="inherit" underline="hover" onClick={() => navigate('/terms-of-service')}>
                Terms of Service
              </Link>
              <Link component="button" variant="body2" color="inherit" underline="hover" onClick={() => navigate('/contact-us')}>
                Contact Us
              </Link>
            </Box>
          </Box>
        </Container>
      </Paper>
    </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" color="primary" elevation={0}>
        <Toolbar>
          <BusinessIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Customer Marketing Intelligence System
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Powered by AI
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ flex: 1, py: 2 }}>
        <Grid container spacing={0} sx={{ height: '100%', minHeight: 'calc(100vh - 180px)' }}>
          {/* Left Side - Analytics Image Carousel */}
          <Grid item xs={12} md={6} sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            p: 4,
            position: 'relative'
          }}>
            <Box sx={{ textAlign: 'center', color: 'white', width: '100%', maxWidth: 700 }}>
              <Box sx={{ position: 'relative' }}>
                <Box
                  component="img"
                  src={loginImages[currentSlide].url}
                  alt={loginImages[currentSlide].title}
                  sx={{
                    width: '100%',
                    maxWidth: 600,
                    height: 'auto',
                    borderRadius: 2,
                    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
                    mb: 3,
                    transition: 'opacity 0.5s ease-in-out'
                  }}
                />
                
                {/* Navigation Buttons */}
                <IconButton
                  onClick={handlePrevSlide}
                  sx={{
                    position: 'absolute',
                    left: -20,
                    top: '40%',
                    color: 'white',
                    bgcolor: 'rgba(0,0,0,0.3)',
                    '&:hover': { bgcolor: 'rgba(0,0,0,0.5)' }
                  }}
                >
                  <ArrowBackIosNewIcon />
                </IconButton>
                
                <IconButton
                  onClick={handleNextSlide}
                  sx={{
                    position: 'absolute',
                    right: -20,
                    top: '40%',
                    color: 'white',
                    bgcolor: 'rgba(0,0,0,0.3)',
                    '&:hover': { bgcolor: 'rgba(0,0,0,0.5)' }
                  }}
                >
                  <ArrowForwardIosIcon />
                </IconButton>
              </Box>
              
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                {loginImages[currentSlide].title}
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
                {loginImages[currentSlide].subtitle}
              </Typography>
              
              {/* Slide Indicators */}
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 2 }}>
                {loginImages.map((_, index) => (
                  <Box
                    key={index}
                    onClick={() => setCurrentSlide(index)}
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      bgcolor: currentSlide === index ? 'white' : 'rgba(255,255,255,0.4)',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Grid>

          {/* Right Side - Login Form */}
          <Grid item xs={12} md={6} sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            p: 2
          }}>
        <Card sx={{ width: '100%', maxWidth: 450 }}>
          <CardContent sx={{ p: 4 }}>
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                mb: 3
              }}
            >
              <Avatar sx={{ m: 1, bgcolor: 'primary.main' }}>
                <LockOutlinedIcon />
              </Avatar>
              <Typography component="h1" variant="h5" sx={{ whiteSpace: 'nowrap' }}>
                Company Data Scraper
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                Sign in to access the file upload and processing dashboard
              </Typography>
            </Box>

            {errors.submit && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {errors.submit}
              </Alert>
            )}

            {errors.success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {errors.success}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={formData.username}
                onChange={handleInputChange}
                error={!!errors.username}
                helperText={errors.username}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleInputChange}
                error={!!errors.password}
                helperText={errors.password}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Sign In'}
              </Button>
              
              <Divider sx={{ my: 2 }} />
              
              <Box textAlign="center">
                <Link
                  component="button"
                  variant="body2"
                  onClick={(e) => {
                    e.preventDefault();
                    setShowRegister(true);
                    setErrors({});
                  }}
                >
                  Don't have an account? Register here
                </Link>
              </Box>
            </Box>
          </CardContent>
        </Card>
          </Grid>
        </Grid>
      </Container>

    {/* Footer */}
    <Paper 
      component="footer" 
      elevation={0} 
      sx={{ 
        py: 3, 
        px: 2, 
        mt: 'auto',
        backgroundColor: 'primary.main',
        color: 'white'
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="body2" color="inherit">
            © {new Date().getFullYear()}{' '}
            <Link href="https://nit-prod.onrender.com/" target="_blank" rel="noopener" color="inherit" underline="hover" sx={{ fontWeight: 500 }}>
              NehaInfoTech
            </Link>
            . All rights reserved.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Link component="button" variant="body2" color="inherit" underline="hover" onClick={() => navigate('/privacy-policy')}>
              Privacy Policy
            </Link>
            <Link component="button" variant="body2" color="inherit" underline="hover" onClick={() => navigate('/terms-of-service')}>
              Terms of Service
            </Link>
            <Link component="button" variant="body2" color="inherit" underline="hover" onClick={() => navigate('/contact-us')}>
              Contact Us
            </Link>
          </Box>
        </Box>
      </Container>
    </Paper>
  </Box>
  );
};

export default LoginForm;