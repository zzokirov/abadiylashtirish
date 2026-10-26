import React from 'react';
import {
  Card,
  CardActionArea,
  Box,
  Typography,
  Avatar,
  IconButton,
  Chip,
  Stack,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { TreeNode } from '../../types';

interface PersonNodeProps {
  node: TreeNode;
  isFocal?: boolean;
  relationLabel?: string;
  onSelect: (node: TreeNode) => void;
  // Collapsible avlodlar uchun
  isExpanded?: boolean;
  onToggleExpand?: (nodeId: number) => void;
  hasChildren?: boolean;
}

export const PersonNode: React.FC<PersonNodeProps> = ({
  node,
  isFocal = false,
  relationLabel,
  onSelect,
  isExpanded,
  onToggleExpand,
  hasChildren = false,
}) => {
  const years = `${node.birth_year || '?'} — ${node.death_year || '?'}`;

  return (
    <Card
      sx={{
        width: { xs: 200, sm: 220 },
        bgcolor: isFocal ? '#1E3A2F' : '#FFFFFF',
        color: isFocal ? '#FFFFFF' : '#1A231F',
        border: isFocal ? '2px solid #C5A880' : '1px solid #D6DDD9',
        borderRadius: 3,
        transition: 'all 0.25s ease-in-out',
        position: 'relative',
        boxShadow: isFocal
          ? '0 8px 24px rgba(30, 58, 47, 0.28)'
          : '0 3px 12px rgba(0, 0, 0, 0.04)',
        '&:hover': {
          transform: 'translateY(-3px)',
          boxShadow: isFocal
            ? '0 12px 28px rgba(30, 58, 47, 0.35)'
            : '0 8px 20px rgba(0, 0, 0, 0.08)',
          borderColor: isFocal ? '#DBC5A6' : '#1E3A2F',
        },
      }}
    >
      <CardActionArea onClick={() => onSelect(node)} sx={{ p: 1.5, pb: hasChildren ? 0.8 : 1.5 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Avatar
            src={node.photo_url || undefined}
            alt={node.full_name}
            sx={{
              width: 44,
              height: 44,
              bgcolor: isFocal ? '#C5A880' : (node.gender === 'MALE' ? '#2E5646' : '#5A3E56'),
              color: '#FFFFFF',
              fontSize: '1.1rem',
              fontWeight: 700,
            }}
          >
            {node.first_name?.[0]}
          </Avatar>

          <Box sx={{ flex: 1, minWidth: 0, textAlign: 'left' }}>
            {relationLabel && (
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  color: isFocal ? '#DBC5A6' : '#72857C',
                  fontWeight: 600,
                  fontSize: '0.68rem',
                  textTransform: 'uppercase',
                  letterSpacing: 0.5,
                  lineHeight: 1,
                  mb: 0.3,
                }}
              >
                {relationLabel}
              </Typography>
            )}
            <Typography
              variant="body2"
              noWrap
              sx={{
                fontWeight: 700,
                fontSize: '0.88rem',
                lineHeight: 1.25,
                color: isFocal ? '#FFFFFF' : '#1A231F',
              }}
            >
              {node.full_name}
            </Typography>
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                color: isFocal ? '#DBC5A6' : '#6A7E74',
                fontSize: '0.74rem',
                mt: 0.3,
                fontWeight: 500,
              }}
            >
              {years}
            </Typography>
          </Box>
        </Stack>
      </CardActionArea>

      {/* Avlodlari tugmasi (Collapsible) */}
      {hasChildren && onToggleExpand && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            borderTop: isFocal ? '1px solid rgba(197, 168, 128, 0.3)' : '1px solid #EEF2F0',
            py: 0.3,
            bgcolor: isFocal ? 'rgba(0,0,0,0.1)' : '#F9FAF9',
          }}
        >
          <Chip
            size="small"
            icon={isExpanded ? <ExpandLessIcon sx={{ fontSize: 16 }} /> : <ExpandMoreIcon sx={{ fontSize: 16 }} />}
            label={`Avlodlari (${node.children?.length || 0})`}
            onClick={(e) => {
              e.stopPropagation();
              onToggleExpand(node.id);
            }}
            sx={{
              height: 22,
              fontSize: '0.68rem',
              fontWeight: 600,
              cursor: 'pointer',
              bgcolor: isFocal ? 'rgba(255,255,255,0.15)' : '#E8EFEA',
              color: isFocal ? '#FFFFFF' : '#1E3A2F',
              '&:hover': {
                bgcolor: isFocal ? 'rgba(255,255,255,0.25)' : '#DCE5E0',
              },
            }}
          />
        </Box>
      )}
    </Card>
  );
};
