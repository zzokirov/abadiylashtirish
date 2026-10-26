import React from 'react';
import { Paper, IconButton, Stack, Tooltip } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

interface TreeControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
  zoomLevel: number;
}

export const TreeControls: React.FC<TreeControlsProps> = ({
  onZoomIn,
  onZoomOut,
  onReset,
  zoomLevel,
}) => {
  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        zIndex: 10,
        borderRadius: 4,
        p: 0.5,
        bgcolor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(8px)',
        border: '1px solid #D6DDD9',
      }}
    >
      <Stack direction="row" spacing={0.5} alignItems="center">
        <Tooltip title="Yaqinlashtirish">
          <IconButton size="small" onClick={onZoomIn} sx={{ color: '#1E3A2F' }}>
            <ZoomInIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Uzoqlashtirish">
          <IconButton size="small" onClick={onZoomOut} sx={{ color: '#1E3A2F' }}>
            <ZoomOutIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Asl holatga qaytarish">
          <IconButton size="small" onClick={onReset} sx={{ color: '#1E3A2F' }}>
            <RestartAltIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Stack>
    </Paper>
  );
};
