import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  AppBar,
  Toolbar,
  Link,
  Divider
} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import { useNavigate } from 'react-router-dom';

const PrivacyPolicy = () => {
  const navigate = useNavigate();

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
      <Container maxWidth="md" sx={{ flex: 1, py: 4 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom color="primary">
            Privacy Policy
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Last updated: {new Date().toLocaleDateString()}
          </Typography>
          
          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            1. Information We Collect
          </Typography>
          <Typography variant="body1" paragraph>
            We collect information that you provide directly to us when you register for an account, 
            use our services, or communicate with us. This may include your name, email address, 
            username, and any other information you choose to provide.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2. How We Use Your Information
          </Typography>
          <Typography variant="body1" paragraph>
            We use the information we collect to provide, maintain, and improve our services, 
            to process your requests, to communicate with you, and to protect our users and services.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            3. Data Security
          </Typography>
          <Typography variant="body1" paragraph>
            We implement appropriate technical and organizational measures to protect the security 
            of your personal information. However, please note that no method of transmission over 
            the Internet or electronic storage is 100% secure.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4. Data Retention
          </Typography>
          <Typography variant="body1" paragraph>
            We retain your personal information for as long as necessary to fulfill the purposes 
            outlined in this privacy policy, unless a longer retention period is required or 
            permitted by law.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5. Your Rights
          </Typography>
          <Typography variant="body1" paragraph>
            You have the right to access, update, or delete your personal information. You may 
            also have the right to restrict or object to certain processing of your data. To 
            exercise these rights, please contact us.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6. Cookies and Tracking Technologies
          </Typography>
          <Typography variant="body1" paragraph>
            We use cookies and similar tracking technologies to track activity on our service and 
            hold certain information. You can instruct your browser to refuse all cookies or to 
            indicate when a cookie is being sent.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            7. Third-Party Services
          </Typography>
          <Typography variant="body1" paragraph>
            Our service may contain links to third-party websites or services that are not owned 
            or controlled by us. We are not responsible for the privacy practices of these third parties.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            8. Changes to This Privacy Policy
          </Typography>
          <Typography variant="body1" paragraph>
            We may update our privacy policy from time to time. We will notify you of any changes 
            by posting the new privacy policy on this page and updating the "Last updated" date.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            9. Contact Us
          </Typography>
          <Typography variant="body1" paragraph>
            If you have any questions about this privacy policy, please contact us at{' '}
            <Link href="https://nit-prod.onrender.com/" target="_blank" rel="noopener">
              NehaInfoTech
            </Link>.
          </Typography>

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

export default PrivacyPolicy;
