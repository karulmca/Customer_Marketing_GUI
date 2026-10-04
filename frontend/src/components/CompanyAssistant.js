import React, { useEffect, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Link,
  Paper,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import DownloadIcon from '@mui/icons-material/Download';
import SendIcon from '@mui/icons-material/Send';
import SyncIcon from '@mui/icons-material/Sync';
import { AssistantService } from '../services/AuthService';

const welcomeMessage = {
  role: 'assistant',
  content: 'Ask a question about your company records, compare companies, or request a summary. Answers include sources when available.'
};

const CompanyAssistant = ({ sessionId }) => {
  const [status, setStatus] = useState(null);
  const [messages, setMessages] = useState([welcomeMessage]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [deletingIndex, setDeletingIndex] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef(null);

  useEffect(() => {
    let active = true;
    AssistantService.getStatus(sessionId)
      .then((result) => {
        if (active) setStatus(result);
      })
      .catch((requestError) => {
        if (active) setError(requestError.response?.data?.detail || requestError.message);
      });
    return () => { active = false; };
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, sending]);

  const handleIndex = async () => {
    setIndexing(true);
    setError('');
    try {
      await AssistantService.indexCompanies(sessionId);
      setStatus(await AssistantService.getStatus(sessionId));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.message);
    } finally {
      setIndexing(false);
    }
  };

  const handleDeleteIndex = async () => {
    if (!window.confirm('Delete your Company AI index from OpenAI? Your uploaded and processed records will remain in this app.')) return;
    setDeletingIndex(true);
    setError('');
    try {
      await AssistantService.deleteIndex(sessionId);
      setStatus(await AssistantService.getStatus(sessionId));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.message);
    } finally {
      setDeletingIndex(false);
    }
  };

  const handleSend = async (event) => {
    event.preventDefault();
    const message = draft.trim();
    if (!message || sending) return;

    const history = messages
      .filter((item) => item !== welcomeMessage)
      .map(({ role, content }) => ({ role, content: content.slice(-4000) }))
      .slice(-24);
    setMessages((current) => [...current, { role: 'user', content: message }]);
    setDraft('');
    setSending(true);
    setError('');

    try {
      const result = await AssistantService.chat(sessionId, message, history);
      setMessages((current) => [...current, {
        role: 'assistant',
        content: result.answer,
        citations: result.citations || [],
        exportRows: result.export_rows || []
      }]);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.message);
    } finally {
      setSending(false);
    }
  };

  const handleExport = (rows) => {
    if (!rows.length) return;
    const columns = [...new Set(rows.flatMap((row) => Object.keys(row)))];
    const escapeCsv = (value) => {
      let text = value == null ? '' : typeof value === 'object' ? JSON.stringify(value) : String(value);
      if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
      return `"${text.replaceAll('"', '""')}"`;
    };
    const csv = [columns, ...rows.map((row) => columns.map((column) => row[column]))]
      .map((line) => line.map(escapeCsv).join(','))
      .join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `company-ai-results-${new Date().toISOString().slice(0, 10)}.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto' }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} alignItems={{ sm: 'center' }} spacing={2} sx={{ mb: 2 }}>
        <Box sx={{ flexGrow: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <AutoAwesomeIcon color="primary" />
            <Typography variant="h5">Company AI</Typography>
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Research your records and the public websites attached to them.
          </Typography>
        </Box>
        {status?.indexed && <Chip color="success" size="small" label={`${status.document_count} sources indexed`} />}
        <Button
          variant={status?.indexed ? 'outlined' : 'contained'}
          startIcon={indexing ? <CircularProgress size={16} color="inherit" /> : <SyncIcon />}
          onClick={handleIndex}
          disabled={indexing || deletingIndex || !status?.configured}
        >
          {indexing ? 'Indexing...' : status?.indexed ? 'Refresh index' : 'Index my records'}
        </Button>
        {status?.indexed && (
          <Button
            variant="text"
            color="error"
            startIcon={deletingIndex ? <CircularProgress size={16} color="inherit" /> : <DeleteOutlineIcon />}
            onClick={handleDeleteIndex}
            disabled={indexing || deletingIndex}
          >
            {deletingIndex ? 'Deleting...' : 'Delete index'}
          </Button>
        )}
      </Stack>

      {!status?.configured && status && (
        <Alert severity="warning" sx={{ mb: 2 }}>OpenAI is not configured. Set OPENAI_API_KEY in the backend environment.</Alert>
      )}
      <Alert severity="info" sx={{ mb: 2 }}>
        Indexing sends your uploaded company records to OpenAI. Public web search is restricted to website domains in your records. Deleting the index does not delete records in this app.
      </Alert>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <Paper variant="outlined" sx={{ overflow: 'hidden' }}>
        <Box sx={{ height: { xs: 420, md: 500 }, overflowY: 'auto', px: { xs: 2, md: 3 }, py: 2 }}>
          <Stack spacing={2}>
            {messages.map((item, index) => (
              <Box key={`${item.role}-${index}`} sx={{ display: 'flex', justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <Box sx={{ maxWidth: { xs: '92%', md: '80%' }, minWidth: 0 }}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      whiteSpace: 'pre-wrap',
                      overflowWrap: 'anywhere',
                      bgcolor: item.role === 'user' ? 'primary.main' : 'grey.100',
                      color: item.role === 'user' ? 'primary.contrastText' : 'text.primary',
                      borderRadius: 1.5
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>{item.content}</Typography>
                  </Paper>
                  {item.citations?.length > 0 && (
                    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1 }}>
                      {item.citations.map((citation, citationIndex) => citation.url ? (
                        <Link key={`${citation.url}-${citationIndex}`} href={citation.url} target="_blank" rel="noreferrer" variant="caption">
                          {citation.title || 'Web source'}
                        </Link>
                      ) : (
                        <Chip key={`${citation.title}-${citationIndex}`} size="small" variant="outlined" label={citation.title || 'Company records'} />
                      ))}
                    </Stack>
                  )}
                  {item.exportRows?.length > 0 && (
                    <Button size="small" startIcon={<DownloadIcon />} onClick={() => handleExport(item.exportRows)} sx={{ mt: 0.5 }}>
                      Export {item.exportRows.length} results
                    </Button>
                  )}
                </Box>
              </Box>
            ))}
            {sending && <Stack direction="row" alignItems="center" spacing={1} color="text.secondary"><CircularProgress size={16} /><Typography variant="caption">Researching records and sources...</Typography></Stack>}
            <div ref={bottomRef} />
          </Stack>
        </Box>
        <Divider />
        <Box component="form" onSubmit={handleSend} sx={{ display: 'flex', alignItems: 'flex-end', gap: 1, p: 1.5 }}>
          <TextField
            fullWidth
            multiline
            maxRows={5}
            size="small"
            placeholder="Ask about your companies..."
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            inputProps={{ maxLength: 4000, 'aria-label': 'Ask Company AI' }}
            disabled={sending}
          />
          <Button type="submit" variant="contained" aria-label="Send message" disabled={!draft.trim() || sending} sx={{ minWidth: 48, width: 48, height: 40 }}>
            <SendIcon />
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default CompanyAssistant;