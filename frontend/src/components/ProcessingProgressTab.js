import React, { useEffect, useState } from 'react';
import { Box, Typography, LinearProgress, Card, CardContent } from '@mui/material';
import { AuthService } from '../services/AuthService';

const ProcessingProgressTab = () => {
  const [progress, setProgress] = useState({ processed: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const percent = progress.total > 0 ? (progress.processed / progress.total) * 100 : 0;

  useEffect(() => {
    const fetchProgress = async () => {
      setLoading(true);
      try {
        const data = await AuthService.getRecordProgress();
        setProgress(data);
      } catch (err) {
        setProgress({ processed: 0, total: 0 });
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
    const interval = setInterval(fetchProgress, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card sx={{ maxWidth: 500, margin: '0 auto' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Processed Records Progress
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="body1">
            {progress.processed} / {progress.total}
          </Typography>
          <LinearProgress variant="determinate" value={percent} sx={{ flex: 1, height: 10, borderRadius: 5 }} />
          <Typography variant="body2" color="text.secondary">
            {Math.round(percent)}%
          </Typography>
        </Box>
        {loading && <Typography variant="caption" color="text.secondary">Loading...</Typography>}
      </CardContent>
    </Card>
  );
};

export default ProcessingProgressTab;
