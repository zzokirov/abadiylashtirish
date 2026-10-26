import { createTheme } from '@mui/material/styles';

export const memorialTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1E3A2F', // To'q yashil, chuqur va viqorli
      light: '#2E5646',
      dark: '#11231C',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#C5A880', // Oltin/mis ohangidagi sokin urg'u
      light: '#DBC5A6',
      dark: '#9A7A54',
      contrastText: '#1E3A2F',
    },
    background: {
      default: '#F7F9F8',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1A231F',
      secondary: '#4A5B52',
    },
    divider: '#E2E8E5',
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontFamily: '"Cormorant Garamond", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '0.02em',
    },
    h2: {
      fontFamily: '"Cormorant Garamond", Georgia, serif',
      fontWeight: 700,
    },
    h3: {
      fontFamily: '"Cormorant Garamond", Georgia, serif',
      fontWeight: 600,
    },
    h4: {
      fontFamily: '"Cormorant Garamond", Georgia, serif',
      fontWeight: 600,
    },
    h5: {
      fontFamily: '"Cormorant Garamond", Georgia, serif',
      fontWeight: 600,
    },
    subtitle1: {
      letterSpacing: '0.01em',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      borderRadius: 10,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '8px 18px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(30, 58, 47, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 20px rgba(18, 38, 30, 0.05)',
          border: '1px solid rgba(226, 232, 229, 0.8)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderTopLeftRadius: 24,
          borderTopRightRadius: 24,
        },
      },
    },
  },
});
