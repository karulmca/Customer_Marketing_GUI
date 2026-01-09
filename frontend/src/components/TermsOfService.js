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

const TermsOfService = () => {
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
            Terms of Service
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Last updated: {new Date().toLocaleDateString()}
          </Typography>
          
          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            1. Acceptance of Terms
          </Typography>
          <Typography variant="body1" paragraph>
            By accessing and using the Customer Marketing Intelligence System, you accept and agree 
            to be bound by the terms and provision of this agreement. If you do not agree to these 
            terms, please do not use our service.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            2. Use License
          </Typography>
          <Typography variant="body1" paragraph>
            Permission is granted to temporarily access the materials (information or software) on 
            the Customer Marketing Intelligence System for personal, non-commercial transitory viewing 
            only. This is the grant of a license, not a transfer of title.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            3. User Accounts
          </Typography>
          <Typography variant="body1" paragraph>
            You are responsible for maintaining the confidentiality of your account and password. 
            You agree to accept responsibility for all activities that occur under your account or 
            password. You must notify us immediately of any unauthorized use of your account.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            4. Prohibited Uses
          </Typography>
          <Typography variant="body1" paragraph>
            You may not use our service: (a) for any unlawful purpose or to solicit others to perform 
            or participate in any unlawful acts; (b) to violate any international, federal, provincial 
            or state regulations, rules, laws, or local ordinances; (c) to infringe upon or violate 
            our intellectual property rights or the intellectual property rights of others.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            5. Service Modifications
          </Typography>
          <Typography variant="body1" paragraph>
            We reserve the right to modify or discontinue, temporarily or permanently, the service 
            (or any part thereof) with or without notice. We shall not be liable to you or to any 
            third party for any modification, suspension or discontinuance of the service.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            6. Intellectual Property
          </Typography>
          <Typography variant="body1" paragraph>
            The service and its original content, features, and functionality are and will remain 
            the exclusive property of NehaInfoTech and its licensors. The service is protected by 
            copyright, trademark, and other laws.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            7. Limitation of Liability
          </Typography>
          <Typography variant="body1" paragraph>
            In no event shall NehaInfoTech, nor its directors, employees, partners, agents, suppliers, 
            or affiliates, be liable for any indirect, incidental, special, consequential or punitive 
            damages, including without limitation, loss of profits, data, use, goodwill, or other 
            intangible losses.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            8. Disclaimer
          </Typography>
          <Typography variant="body1" paragraph>
            Your use of the service is at your sole risk. The service is provided on an "AS IS" 
            and "AS AVAILABLE" basis. The service is provided without warranties of any kind, 
            whether express or implied.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            9. Governing Law
          </Typography>
          <Typography variant="body1" paragraph>
            These terms shall be governed and construed in accordance with applicable laws, without 
            regard to its conflict of law provisions.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            10. Changes to Terms
          </Typography>
          <Typography variant="body1" paragraph>
            We reserve the right, at our sole discretion, to modify or replace these terms at any 
            time. What constitutes a material change will be determined at our sole discretion. 
            By continuing to access or use our service after those revisions become effective, you 
            agree to be bound by the revised terms.
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            11. Contact Us
          </Typography>
          <Typography variant="body1" paragraph>
            If you have any questions about these terms, please contact us at{' '}
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

export default TermsOfService;
