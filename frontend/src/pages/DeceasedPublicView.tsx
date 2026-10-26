import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Paper,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import AutoStoriesOutlinedIcon from '@mui/icons-material/AutoStoriesOutlined';
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';

import { PublicDeceased, FamilyTreeData, TreeNode } from '../types';
import { memorialApi } from '../api/client';
import { MemorialHeader } from '../components/MemorialHeader';
import { FamilyTree } from '../components/FamilyTree/FamilyTree';
import { PersonDrawer } from '../components/PersonDrawer';

export const DeceasedPublicView: React.FC = () => {
  const { token } = useParams<{ token: string }>();

  const [person, setPerson] = useState<PublicDeceased | null>(null);
  const [treeData, setTreeData] = useState<FamilyTreeData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<number>(0);
  const [selectedPerson, setSelectedPerson] = useState<TreeNode | null>(null);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const [isFocalSelected, setIsFocalSelected] = useState<boolean>(false);

  useEffect(() => {
    if (!token) {
      setError("QR-kod tokeni mavjud emas.");
      setLoading(false);
      return;
    }

    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [deceasedRes, treeRes] = await Promise.all([
          memorialApi.getDeceasedByToken(token),
          memorialApi.getFamilyTreeByToken(token),
        ]);
        setPerson(deceasedRes);
        setTreeData(treeRes);
      } catch (err: any) {
        console.error("Ma'lumotlarni yuklashda xatolik:", err);
        if (err.response?.status === 404) {
          setError("Ushbu QR-kodga tegishli marhum sahifasi topilmadi yoki hali ommaga e’lon qilinmagan.");
        } else {
          setError("Server bilan bog‘lanishda xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.");
        }
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [token]);

  const handleSelectPerson = (personNode: TreeNode, isFocal: boolean = false) => {
    setSelectedPerson(personNode);
    setIsFocalSelected(isFocal);
    setDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setDrawerOpen(false);
    setSelectedPerson(null);
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '80vh',
          gap: 2,
        }}
      >
        <CircularProgress sx={{ color: '#1E3A2F' }} size={48} />
        <Typography variant="body1" sx={{ color: '#5A6E63', fontWeight: 500 }}>
          Xotira sahifasi yuklanmoqda...
        </Typography>
      </Box>
    );
  }

  if (error || !person) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Alert
          severity="info"
          sx={{
            borderRadius: 3,
            bgcolor: '#F3F6F4',
            color: '#1E3A2F',
            border: '1px solid #D6DDD9',
            '& .MuiAlert-icon': { color: '#1E3A2F' },
          }}
        >
          {error || "Ma’lumot topilmadi."}
        </Alert>
      </Container>
    );
  }

  return (
    <Box sx={{ bgcolor: '#F7F9F8', minHeight: '100vh', pb: 8 }}>
      {/* 1. Yuqori viqorli qism */}
      <MemorialHeader person={person} />

      {/* 2. Navigatsiya Tablari */}
      <Container maxWidth="md" sx={{ mt: -2.5, position: 'relative', zIndex: 2 }}>
        <Paper
          elevation={2}
          sx={{
            borderRadius: 3,
            p: 0.5,
            bgcolor: '#FFFFFF',
            border: '1px solid #E2E8E5',
          }}
        >
          <Tabs
            value={activeTab}
            onChange={(_, val) => setActiveTab(val)}
            variant="fullWidth"
            textColor="primary"
            indicatorColor="primary"
            sx={{
              '& .MuiTab-root': {
                fontWeight: 600,
                fontSize: { xs: '0.85rem', sm: '0.95rem' },
                py: 1.5,
              },
            }}
          >
            <Tab
              icon={<AutoStoriesOutlinedIcon sx={{ fontSize: 20 }} />}
              iconPosition="start"
              label="Tarjimai holi"
            />
            <Tab
              icon={<AccountTreeOutlinedIcon sx={{ fontSize: 20 }} />}
              iconPosition="start"
              label="Elektron Shajara"
            />
          </Tabs>
        </Paper>

        {/* ================= TAB 0: TARJIMAI HOL ================= */}
        {activeTab === 0 && (
          <Box sx={{ mt: 3 }}>
            <Card sx={{ p: { xs: 2.5, sm: 3.5 }, borderRadius: 4 }}>
              <CardContent sx={{ p: 0 }}>
                <Typography
                  variant="h5"
                  sx={{
                    fontFamily: '"Cormorant Garamond", Georgia, serif',
                    fontWeight: 700,
                    color: '#1E3A2F',
                    mb: 2,
                  }}
                >
                  Hayot yo‘li va Ibratli Xotiralar
                </Typography>
                <Divider sx={{ mb: 2.5 }} />

                <Typography
                  variant="body1"
                  sx={{
                    color: '#2C3A33',
                    lineHeight: 1.85,
                    fontSize: { xs: '0.98rem', sm: '1.05rem' },
                    whiteSpace: 'pre-line',
                  }}
                >
                  {person.biography || "Tarjimai hol ma’lumotlari hali kiritilmagan."}
                </Typography>

                {/* Sokin duoyi xayr yoki xotira iborasi */}
                <Box
                  sx={{
                    mt: 4,
                    p: 2.5,
                    bgcolor: '#F3F6F4',
                    borderRadius: 3,
                    borderLeft: '4px solid #C5A880',
                    textAlign: 'center',
                  }}
                >
                  <Typography
                    variant="subtitle1"
                    sx={{
                      fontStyle: 'italic',
                      fontFamily: '"Cormorant Garamond", Georgia, serif',
                      color: '#1E3A2F',
                      fontWeight: 600,
                      fontSize: '1.15rem',
                    }}
                  >
                    «Oxiratlari obod, joylari jannatda bo‘lsin. Yaxshi amallari o‘zlariga hamroh bo‘lsin.»
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* ================= TAB 1: INTERAKTIV SHAJARA ================= */}
        {activeTab === 1 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" sx={{ color: '#5A6E63', mb: 1.5, textAlign: 'center' }}>
              💡 Shajaradagi har qanday shaxs ustiga bosib uning qabri va tarjimai holini ko‘rishingiz mumkin.
            </Typography>

            {treeData ? (
              <FamilyTree
                treeData={treeData}
                onSelectPerson={handleSelectPerson}
              />
            ) : (
              <Alert severity="info">Shajara ma’lumotlari topilmadi.</Alert>
            )}
          </Box>
        )}
      </Container>

      {/* 3. Karta bosilganda pastdan chiquvchi ma'lumotlar oynasi (Drawer) */}
      <PersonDrawer
        person={selectedPerson}
        open={drawerOpen}
        onClose={handleCloseDrawer}
        isFocal={isFocalSelected}
      />
    </Box>
  );
};
