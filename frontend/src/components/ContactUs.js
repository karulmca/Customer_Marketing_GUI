import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  AppBar,
  Toolbar,
  Link,
  TextField,
  Button,
  Grid,
  Alert
} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { useNavigate } from 'react-router-dom';

const ContactUs = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically send the form data to your backend
    console.log('Contact form submitted:', formData);
    setSubmitted(true);
    setFormData({ name: '', email: '', subject: '', message: '' });
    setTimeout(() => setSubmitted(false), 5000);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" color="primary" elevation={0}>
        <Toolbar>
          <BusinessIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => navigate('/login')}>
            Customer Marketing Intelligence System
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Powered by AI
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ flex: 1, py: 4 }}>
        <Grid container spacing={4}>
          {/* Contact Form */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4 }}>
              <Typography variant="h4" component="h1" gutterBottom color="primary">
                Contact Us
              </Typography>
              <Typography variant="body1" paragraph color="text.secondary">
                Have questions or need support? Fill out the form below and we'll get back to you as soon as possible.
              </Typography>

              {submitted && (
                <Alert severity="success" sx={{ mb: 3 }}>
                  Thank you for contacting us! We'll get back to you soon.
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Your Name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email Address"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Message"
                      name="message"
                      multiline
                      rows={6}
                      value={formData.message}
                      onChange={handleChange}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button 
                      type="submit" 
                      variant="contained" 
                      size="large"
                      fullWidth
                    >
                      Send Message
                    </Button>
                  </Grid>
                </Grid>
              </Box>

              <Box sx={{ mt: 4, textAlign: 'center' }}>
                <Link 
                  component="button" 
                  variant="body2" 
                  onClick={() => navigate('/login')}
                  sx={{ cursor: 'pointer' }}
                >
                  Back to Login
                </Link>
              </Box>
            </Paper>
          </Grid>

          {/* Contact Information */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, height: '100%' }}>
              <Typography variant="h5" gutterBottom color="primary">
                Get in Touch
              </Typography>
              <Typography variant="body2" paragraph color="text.secondary">
                We're here to help and answer any question you might have.
              </Typography>

              <Box sx={{ mt: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
                  <EmailIcon sx={{ mr: 2, color: 'primary.main', mt: 0.5 }} />
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Email
                    </Typography>
                    <Link href="mailto:support@nehainfotech.com" color="text.secondary" underline="hover">
                      support@nehainfotech.com
                    </Link>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
                  <PhoneIcon sx={{ mr: 2, color: 'primary.main', mt: 0.5 }} />
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Phone
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      +1 (555) 123-4567
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
                  <LocationOnIcon sx={{ mr: 2, color: 'primary.main', mt: 0.5 }} />
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Address
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      123 Business Street<br />
                      Tech City, TC 12345<br />
                      United States
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mt: 4 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Website
                  </Typography>
                  <Link 
                    href="https://nit-prod.onrender.com/" 
                    target="_blank" 
                    rel="noopener"
                    color="primary"
                    underline="hover"
                  >
                    https://nit-prod.onrender.com/
                  </Link>
                </Box>
              </Box>
            </Paper>
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

export default ContactUs;
