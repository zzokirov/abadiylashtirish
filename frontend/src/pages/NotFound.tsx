import React from 'react';
import { Container, Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm" sx={{ py: 10, textAlign: 'center' }}>
      <Typography variant="h2" sx={{ color: '#1E3A2F', fontWeight: 700, mb: 1 }}>
        404
      </Typography>
      <Typography variant="h5" sx={{ color: '#3A4D43', mb: 2 }}>
        Sahifa topilmadi
      </Typography>
      <Typography variant="body1" sx={{ color: '#6A7D74', mb: 4 }}>
        Siz qidirayotgan QR-kod yoki manzil mavjud emas yoxud o‘chirilgan bo‘lishi mumkin.
      </Typography>
      <Button
        variant="contained"
        onClick={() => navigate('/')}
        sx={{ bgcolor: '#1E3A2F' }}
      >
        Bosh sahifaga qaytish
      </Button>
    </Container>
  );
};
