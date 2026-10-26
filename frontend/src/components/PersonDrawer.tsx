import React from 'react';
import {
  Drawer,
  Box,
  Typography,
  Avatar,
  Stack,
  IconButton,
  Button,
  Divider,
  Chip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';
import PlaceIcon from '@mui/icons-material/Place';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import { useNavigate } from 'react-router-dom';
import { TreeNode } from '../types';

interface PersonDrawerProps {
  person: TreeNode | null;
  open: boolean;
  onClose: () => void;
  isFocal?: boolean;
}

export const PersonDrawer: React.FC<PersonDrawerProps> = ({
  person,
  open,
  onClose,
  isFocal = false,
}) => {
  const navigate = useNavigate();

  if (!person) return null;

  const handleNavigateToTree = () => {
    if (person.public_token) {
      onClose();
      navigate(`/m/${person.public_token}`);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const yearsDisplay = `${person.birth_year || '?'} — ${person.death_year || '?'}`;

  return (
    <Drawer
      anchor="bottom"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          maxHeight: '85vh',
          p: { xs: 2.5, sm: 3.5 },
          backgroundColor: '#FFFFFF',
          maxWidth: 600,
          mx: 'auto',
          boxShadow: '0 -10px 40px rgba(0, 0, 0, 0.15)',
        },
      }}
    >
      {/* Yuqori kichik tortish chizig'i (Drag handle) */}
      <Box
        sx={{
          width: 44,
          height: 5,
          bgcolor: '#D0D6D3',
          borderRadius: 3,
          mx: 'auto',
          mb: 2,
        }}
      />

      {/* Yopish tugmasi */}
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Typography variant="overline" sx={{ color: '#C5A880', fontWeight: 700, letterSpacing: 1.5 }}>
          {person.relation || (isFocal ? "Markaziy Marhum" : "Qarindoshlik")}
        </Typography>
        <IconButton onClick={onClose} size="small" sx={{ color: '#6A7D74' }}>
          <CloseIcon />
        </IconButton>
      </Stack>

      {/* Marhum profili */}
      <Stack direction="row" spacing={2.5} alignItems="center" sx={{ mt: 1, mb: 2.5 }}>
        <Avatar
          src={person.photo_url || undefined}
          alt={person.full_name}
          sx={{
            width: 76,
            height: 76,
            border: '2px solid #C5A880',
            bgcolor: '#1E3A2F',
            fontSize: '1.8rem',
            fontFamily: '"Cormorant Garamond", Georgia, serif',
            color: '#FFFFFF',
          }}
        >
          {person.first_name?.[0]}
        </Avatar>

        <Box sx={{ flex: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#1A231F', lineHeight: 1.2 }}>
            {person.full_name}
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.5 }}>
            <CalendarTodayIcon sx={{ fontSize: 15, color: '#C5A880' }} />
            <Typography variant="body2" sx={{ color: '#5A6E63', fontWeight: 600 }}>
              {yearsDisplay}
            </Typography>
          </Stack>
        </Box>
      </Stack>

      {/* Joylashuv ma'lumotlari */}
      {(person.cemetery_name || person.grave_number) && (
        <Stack direction="row" spacing={1} sx={{ mb: 2.5 }} flexWrap="wrap">
          {person.cemetery_name && (
            <Chip
              icon={<PlaceIcon sx={{ fontSize: 16 }} />}
              label={person.cemetery_name}
              size="small"
              sx={{ bgcolor: '#F0F4F2', color: '#1E3A2F', fontWeight: 500 }}
            />
          )}
          {person.grave_number && (
            <Chip
              label={`Qabr: ${person.grave_number}`}
              size="small"
              sx={{ bgcolor: '#F0F4F2', color: '#1E3A2F', fontWeight: 600 }}
            />
          )}
        </Stack>
      )}

      <Divider sx={{ mb: 2.5 }} />

      {/* Tarjimai hol */}
      <Box sx={{ overflowY: 'auto', pr: 0.5, mb: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1E3A2F', mb: 1 }}>
          Tarjimai holi va xotiralar:
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#3C4B43',
            lineHeight: 1.7,
            whiteSpace: 'pre-line',
          }}
        >
          {person.biography_preview || "Ushbu shaxs haqida qo‘shimcha tarjimai hol kiritilmagan."}
        </Typography>
      </Box>

      {/* Agar ushbu shaxsning o'z QR kodi bo'lsa va u hozirgi markaz bo'lmasa */}
      {!isFocal && person.public_token && (
        <Button
          fullWidth
          variant="contained"
          color="primary"
          onClick={handleNavigateToTree}
          startIcon={<AccountTreeOutlinedIcon />}
          sx={{
            py: 1.4,
            fontSize: '0.95rem',
            background: 'linear-gradient(135deg, #1E3A2F 0%, #2A4F40 100%)',
          }}
        >
          Ushbu marhum shajarasiga o‘tish
        </Button>
      )}
    </Drawer>
  );
};
