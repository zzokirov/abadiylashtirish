import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { memorialTheme } from './theme/theme';
import { DeceasedPublicView } from './pages/DeceasedPublicView';
import { AdminDashboard } from './pages/AdminDashboard';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  return (
    <ThemeProvider theme={memorialTheme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          {/* Asosiy doimiy QR sahifa: https://domain.uz/m/{token} */}
          <Route path="/m/:token" element={<DeceasedPublicView />} />

          {/* Admin boshqaruv paneli */}
          <Route path="/admin-panel" element={<AdminDashboard />} />

          {/* Standart yo'naltirish */}
          <Route path="/" element={<Navigate to="/admin-panel" replace />} />

          {/* 404 sahifa */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
