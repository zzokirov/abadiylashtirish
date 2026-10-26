import React, { useState } from 'react';
import { Box, Typography, Stack, Divider, Chip } from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import { FamilyTreeData, TreeNode } from '../../types';
import { PersonNode } from './PersonNode';
import { TreeControls } from './TreeControls';

interface FamilyTreeProps {
  treeData: FamilyTreeData;
  onSelectPerson: (person: TreeNode, isFocal?: boolean) => void;
}

export const FamilyTree: React.FC<FamilyTreeProps> = ({
  treeData,
  onSelectPerson,
}) => {
  const [zoom, setZoom] = useState<number>(1);
  const [expandedNodes, setExpandedNodes] = useState<Record<number, boolean>>({});

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.15, 1.6));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.15, 0.65));
  const handleResetZoom = () => setZoom(1);

  const toggleExpand = (nodeId: number) => {
    setExpandedNodes((prev) => ({
      ...prev,
      [nodeId]: !prev[nodeId],
    }));
  };

  const renderAncestorBranch = (node: TreeNode | null, label: string) => {
    if (!node) {
      return (
        <Box
          sx={{
            p: 2,
            border: '1px dashed #CBD5D0',
            borderRadius: 3,
            bgcolor: 'rgba(240, 244, 242, 0.5)',
            textAlign: 'center',
            width: { xs: 180, sm: 200 },
          }}
        >
          <Typography variant="caption" sx={{ color: '#879990', fontStyle: 'italic' }}>
            {label} ma’lumotlari kiritilmagan
          </Typography>
        </Box>
      );
    }

    return (
      <Stack spacing={2} alignItems="center">
        {/* Bobo va Buvi (agar bo'lsa) */}
        {(node.father || node.mother) && (
          <Stack direction="row" spacing={2} alignItems="center">
            {node.father && (
              <PersonNode
                node={node.father}
                relationLabel="Katta Bobo / Bobo"
                onSelect={(p) => onSelectPerson(p, false)}
              />
            )}
            {node.mother && (
              <PersonNode
                node={node.mother}
                relationLabel="Katta Buvi / Buvi"
                onSelect={(p) => onSelectPerson(p, false)}
              />
            )}
          </Stack>
        )}

        {/* Chiziq */}
        {(node.father || node.mother) && (
          <Box sx={{ width: 2, height: 16, bgcolor: '#C5A880' }} />
        )}

        {/* Ota yoki Ona */}
        <PersonNode
          node={node}
          relationLabel={label}
          onSelect={(p) => onSelectPerson(p, false)}
        />
      </Stack>
    );
  };

  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        minHeight: 650,
        overflowX: 'auto',
        overflowY: 'hidden',
        py: 4,
        px: 2,
        bgcolor: '#F7F9F8',
        borderRadius: 4,
      }}
    >
      <Box
        sx={{
          minWidth: 700,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          transform: `scale(${zoom})`,
          transformOrigin: 'top center',
          transition: 'transform 0.2s ease-out',
        }}
      >
        {/* ================= 1. AJDODLAR QATORI ================= */}
        <Box sx={{ mb: 1, textAlign: 'center' }}>
          <Chip
            label="AJDODLAR (OTA VA ONA TOMON)"
            size="small"
            sx={{
              bgcolor: '#EAEFEA',
              color: '#1E3A2F',
              fontWeight: 700,
              fontSize: '0.72rem',
              letterSpacing: 1,
              mb: 2.5,
            }}
          />
        </Box>

        <Stack direction="row" spacing={{ xs: 4, md: 8 }} justifyContent="center" sx={{ mb: 2 }}>
          {/* Ota tarmog'i */}
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="overline" sx={{ color: '#2E5646', fontWeight: 700, display: 'block', mb: 1 }}>
              Ota Tarmog‘i
            </Typography>
            {renderAncestorBranch(treeData.paternal_ancestors, "Otasi")}
          </Box>

          {/* Ajratuvchi chiziq */}
          <Divider orientation="vertical" flexItem sx={{ borderStyle: 'dashed', borderColor: '#CBD5D0' }} />

          {/* Ona tarmog'i */}
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="overline" sx={{ color: '#5A3E56', fontWeight: 700, display: 'block', mb: 1 }}>
              Ona Tarmog‘i
            </Typography>
            {renderAncestorBranch(treeData.maternal_ancestors, "Onasi")}
          </Box>
        </Stack>

        {/* Ajdodlardan markaziy marhumga tushuvchi ulovchi chiziq */}
        <Box sx={{ width: 2, height: 28, bgcolor: '#1E3A2F', my: 0.5 }} />

        {/* ================= 2. MARKAZIY MARHUM VA TURMUSH O'RTOG'I ================= */}
        <Box sx={{ my: 1.5, textAlign: 'center' }}>
          <Chip
            label="MARKAZIY MARHUM"
            size="small"
            sx={{
              bgcolor: '#1E3A2F',
              color: '#C5A880',
              fontWeight: 700,
              fontSize: '0.72rem',
              letterSpacing: 1,
              mb: 1.5,
            }}
          />
        </Box>

        <Stack direction="row" spacing={3} alignItems="center" justifyContent="center">
          {/* Markaziy shaxs */}
          <PersonNode
            node={treeData.focal_person}
            isFocal={true}
            relationLabel="Asosiy Marhum"
            onSelect={(p) => onSelectPerson(p, true)}
          />

          {/* Turmush o'rtoqlari */}
          {treeData.spouses && treeData.spouses.length > 0 && (
            <Stack direction="row" spacing={2} alignItems="center">
              <FavoriteIcon sx={{ color: '#C5A880', fontSize: 20 }} />
              {treeData.spouses.map((spouse) => (
                <PersonNode
                  key={spouse.id}
                  node={spouse}
                  relationLabel="Turmush o‘rtog‘i"
                  onSelect={(p) => onSelectPerson(p, false)}
                />
              ))}
            </Stack>
          )}
        </Stack>

        {/* Markaziy marhumdan avlodlarga tushuvchi ulovchi chiziq */}
        <Box sx={{ width: 2, height: 28, bgcolor: '#1E3A2F', my: 1 }} />

        {/* ================= 3. AVLODLAR (BOLALARI VA NABIRALARI) ================= */}
        <Box sx={{ mt: 1, mb: 1.5, textAlign: 'center' }}>
          <Chip
            label={`AVLODLARI (${treeData.descendants?.length || 0})`}
            size="small"
            sx={{
              bgcolor: '#EAEFEA',
              color: '#1E3A2F',
              fontWeight: 700,
              fontSize: '0.72rem',
              letterSpacing: 1,
              mb: 2,
            }}
          />
        </Box>

        {treeData.descendants && treeData.descendants.length > 0 ? (
          <Stack direction="row" spacing={3} justifyContent="center" flexWrap="wrap" sx={{ gap: 2 }}>
            {treeData.descendants.map((child) => {
              const isExpanded = !!expandedNodes[child.id];
              const hasGrandchildren = child.children && child.children.length > 0;

              return (
                <Stack key={child.id} spacing={1.5} alignItems="center">
                  <PersonNode
                    node={child}
                    relationLabel="Farzandi"
                    onSelect={(p) => onSelectPerson(p, false)}
                    hasChildren={hasGrandchildren}
                    isExpanded={isExpanded}
                    onToggleExpand={toggleExpand}
                  />

                  {/* Nabiralar (ochilganda) */}
                  {hasGrandchildren && isExpanded && (
                    <Box sx={{ pt: 1, pl: 2, borderLeft: '2px solid #C5A880', width: '100%' }}>
                      <Typography variant="caption" sx={{ color: '#72857C', fontWeight: 600, display: 'block', mb: 1 }}>
                        Nabiralari:
                      </Typography>
                      <Stack spacing={1.5}>
                        {child.children!.map((grandchild) => (
                          <PersonNode
                            key={grandchild.id}
                            node={grandchild}
                            relationLabel="Nabirasi"
                            onSelect={(p) => onSelectPerson(p, false)}
                          />
                        ))}
                      </Stack>
                    </Box>
                  )}
                </Stack>
              );
            })}
          </Stack>
        ) : (
          <Box sx={{ p: 2, border: '1px dashed #CBD5D0', borderRadius: 3, bgcolor: '#F0F4F2' }}>
            <Typography variant="caption" sx={{ color: '#879990', fontStyle: 'italic' }}>
              Avlodlar (farzandlar) haqida ma’lumot hali kiritilmagan
            </Typography>
          </Box>
        )}
      </Box>

      {/* Zoom boshqaruvi */}
      <TreeControls
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onReset={handleResetZoom}
        zoomLevel={zoom}
      />
    </Box>
  );
};
