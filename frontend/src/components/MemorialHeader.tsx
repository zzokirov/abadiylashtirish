import React from 'react';
import {
  Box,
  Typography,
  Avatar,
  Chip,
  Button,
  Stack,
  Divider,
} from '@mui/material';
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined';
import PlaceIcon from '@mui/icons-material/Place';
import CalendarMonthOutlinedIcon from '@mui/icons-material/CalendarMonthOutlined';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { PublicDeceased } from '../types';

interface MemorialHeaderProps {
  person: PublicDeceased;
}

export const MemorialHeader: React.FC<MemorialHeaderProps> = ({ person }) => {
  const openMap = () => {
    if (person.cemetery?.latitude && person.cemetery?.longitude) {
      const url = `https://www.google.com/maps/search/?api=1&query=${person.cemetery.latitude},${person.cemetery.longitude}`;
      window.open(url, '_blank');
    }
  };

  return (
    <Box
      sx={{
        background: 'linear-gradient(180deg, #1E3A2F 0%, #152921 100%)',
        color: '#FFFFFF',
        pt: { xs: 4, md: 6 },
        pb: { xs: 5, md: 7 },
        px: { xs: 2, sm: 3 },
        borderBottomLeftRadius: { xs: 28, md: 36 },
        borderBottomRightRadius: { xs: 28, md: 36 },
        boxShadow: '0 10px 30px rgba(17, 35, 28, 0.25)',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Orqa fondagi islimiy sokin naqsh effekti */}
      <Box
        sx={{
          position: 'absolute',
          top: -40,
          right: -40,
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(197, 168, 128, 0.12) 0%, rgba(30, 58, 47, 0) 70%)',
          pointerEvents: 'none',
        }}
      />

      <Stack spacing={2} alignItems="center" sx={{ position: 'relative', zIndex: 1 }}>
        {/* Surat yoki viqorli bosh harflar */}
        <Avatar
          src={person.photo || undefined}
          alt={person.full_name}
          sx={{
            width: { xs: 110, sm: 130 },
            height: { xs: 110, sm: 130 },
            border: '4px solid #C5A880',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.35)',
            bgcolor: '#2E5646',
            fontSize: '2.5rem',
            fontFamily: '"Cormorant Garamond", Georgia, serif',
            color: '#FFFFFF',
          }}
        >
          {person.first_name?.[0]}
        </Avatar>

        {/* F.I.Sh */}
        <Box>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontWeight: 700,
              color: '#FFFFFF',
              fontSize: { xs: '1.75rem', sm: '2.4rem' },
              lineHeight: 1.2,
              mb: 0.5,
            }}
          >
            {person.full_name}
          </Typography>

          {/* Tug'ilgan va Vafot sanalari */}
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            justifyContent="center"
            sx={{ mt: 1, color: '#DBC5A6' }}
          >
            <CalendarMonthOutlinedIcon fontSize="small" sx={{ opacity: 0.9 }} />
            <Typography variant="subtitle1" sx={{ fontWeight: 600, fontSize: { xs: '1rem', sm: '1.15rem' } }}>
              {person.years}
            </Typography>
          </Stack>
        </Box>

        {/* Qabr joylashuvi va qabriston ma'lumotlari */}
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1}
          alignItems="center"
          justifyContent="center"
          sx={{ pt: 1 }}
        >
          {person.cemetery && (
            <Chip
              icon={<PlaceIcon sx={{ color: '#C5A880 !important' }} />}
              label={person.cemetery.name}
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.12)',
                color: '#FFFFFF',
                backdropFilter: 'blur(8px)',
                fontWeight: 500,
              }}
            />
          )}

          {person.grave_number && (
            <Chip
              label={`Qabr: ${person.grave_number}`}
              sx={{
                bgcolor: 'rgba(197, 168, 128, 0.2)',
                color: '#FFFFFF',
                border: '1px solid rgba(197, 168, 128, 0.4)',
                fontWeight: 600,
              }}
            />
          )}
        </Stack>

        {/* Agar xarita koordinatasi mavjud bo'lsa */}
        {person.cemetery?.latitude && person.cemetery?.longitude && (
          <Button
            variant="outlined"
            size="small"
            onClick={openMap}
            startIcon={<LocationOnOutlinedIcon />}
            endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
            sx={{
              color: '#DBC5A6',
              borderColor: 'rgba(197, 168, 128, 0.5)',
              mt: 1,
              '&:hover': {
                borderColor: '#C5A880',
                bgcolor: 'rgba(197, 168, 128, 0.1)',
              },
            }}
          >
            Qabristonni xaritadan ko‘rish
          </Button>
        )}
      </Stack>
    </Box>
  );
};
