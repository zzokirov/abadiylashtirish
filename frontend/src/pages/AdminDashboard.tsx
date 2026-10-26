import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stack,
  Alert,
  ButtonGroup,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import QrCode2Icon from '@mui/icons-material/QrCode2';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import LinkIcon from '@mui/icons-material/Link';
import { apiClient, API_BASE_URL } from '../api/client';

export const AdminDashboard: React.FC = () => {
  const [persons, setPersons] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [openCreateModal, setOpenCreateModal] = useState<boolean>(false);
  const [openRelationModal, setOpenRelationModal] = useState<boolean>(false);

  // Form states
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    middle_name: '',
    birth_date: '',
    death_date: '',
    gender: 'MALE',
    grave_number: '',
    biography: '',
  });

  const [relationData, setRelationData] = useState({
    child_id: '',
    parent_id: '',
    relationship_type: 'PARENT',
  });

  const [formError, setFormError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadPersons = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/admin/deceased/');
      setPersons(res.data.results || res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPersons();
  }, []);

  const handleCreateSubmit = async () => {
    setFormError(null);
    try {
      await apiClient.post('/admin/deceased/', formData);
      setSuccessMsg("Yangi marhum muvaffaqiyatli saqlandi va doimiy QR-kod shakllantirildi!");
      setOpenCreateModal(false);
      setFormData({
        first_name: '',
        last_name: '',
        middle_name: '',
        birth_date: '',
        death_date: '',
        gender: 'MALE',
        grave_number: '',
        biography: '',
      });
      loadPersons();
    } catch (err: any) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : "Xatolik yuz berdi";
      setFormError(msg);
    }
  };

  const handleRelationSubmit = async () => {
    setFormError(null);
    try {
      await apiClient.post('/admin/relationships/', {
        person: relationData.child_id,
        related_person: relationData.parent_id,
        relationship_type: relationData.relationship_type,
      });
      setSuccessMsg("Qarindoshlik aloqasi (shajara bo‘g‘ini) muvaffaqiyatli o‘rnatildi!");
      setOpenRelationModal(false);
    } catch (err: any) {
      const msg = err.response?.data ? JSON.stringify(err.response.data) : "Xatolik yuz berdi";
      setFormError(msg);
    }
  };

  const getDownloadUrl = (token: string, format: string) => {
    return `${API_BASE_URL}/qr/${token}/download/${format}/`;
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#1E3A2F' }}>
            Boshqaruv Paneli
          </Typography>
          <Typography variant="body2" sx={{ color: '#5A6E63' }}>
            Marhumlar ro‘yxati, shajara aloqalari va qabr toshiga QR-kodlarni eksport qilish
          </Typography>
        </Box>

        <Stack direction="row" spacing={1.5}>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<LinkIcon />}
            onClick={() => setOpenRelationModal(true)}
          >
            Ota-onani biriktirish
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setOpenCreateModal(true)}
            sx={{ bgcolor: '#1E3A2F' }}
          >
            Yangi Marhum Qo‘shish
          </Button>
        </Stack>
      </Stack>

      {successMsg && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMsg(null)}>
          {successMsg}
        </Alert>
      )}

      {/* Ro'yxat jadvali */}
      <TableContainer component={Paper} sx={{ borderRadius: 3, border: '1px solid #E2E8E5' }}>
        <Table>
          <TableHead sx={{ bgcolor: '#F0F4F2' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700, color: '#1E3A2F' }}>F.I.Sh</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1E3A2F' }}>Jinsi</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1E3A2F' }}>Yillari</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1E3A2F' }}>Qabr raqami</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1E3A2F' }}>QR Token</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#1E3A2F', textAlign: 'center' }}>
                Toshga QR Yuklab olish
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {persons.map((p) => (
              <TableRow key={p.id} hover>
                <TableCell sx={{ fontWeight: 600 }}>{p.full_name}</TableCell>
                <TableCell>
                  <Chip
                    label={p.gender === 'MALE' ? 'Erkak' : 'Ayol'}
                    size="small"
                    sx={{
                      bgcolor: p.gender === 'MALE' ? '#E8EFEA' : '#F7EDF5',
                      color: p.gender === 'MALE' ? '#1E3A2F' : '#683660',
                      fontWeight: 600,
                    }}
                  />
                </TableCell>
                <TableCell>
                  {(p.birth_date ? p.birth_date.slice(0, 4) : '?')} — {p.death_date?.slice(0, 4)}
                </TableCell>
                <TableCell>{p.grave_number || '—'}</TableCell>
                <TableCell>
                  <code style={{ fontSize: '0.8rem', color: '#1E3A2F' }}>{p.public_token}</code>
                </TableCell>
                <TableCell sx={{ textAlign: 'center' }}>
                  <ButtonGroup size="small" variant="outlined">
                    <Button
                      href={getDownloadUrl(p.public_token, 'png')}
                      target="_blank"
                      sx={{ color: '#1E3A2F', borderColor: '#1E3A2F' }}
                    >
                      PNG (300DPI)
                    </Button>
                    <Button
                      href={getDownloadUrl(p.public_token, 'svg')}
                      target="_blank"
                      sx={{ color: '#2C5282', borderColor: '#2C5282' }}
                    >
                      SVG Lazer
                    </Button>
                    <Button
                      href={getDownloadUrl(p.public_token, 'pdf')}
                      target="_blank"
                      startIcon={<PictureAsPdfIcon />}
                      sx={{ color: '#744210', borderColor: '#744210' }}
                    >
                      PDF
                    </Button>
                  </ButtonGroup>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* ================= MARHUM QO'SHISH MODAL ================= */}
      <Dialog open={openCreateModal} onClose={() => setOpenCreateModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700, color: '#1E3A2F' }}>
          Yangi Marhum Ma’lumotlarini Kiritish
        </DialogTitle>
        <DialogContent dividers>
          {formError && <Alert severity="error" sx={{ mb: 2 }}>{formError}</Alert>}

          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction="row" spacing={2}>
              <TextField
                fullWidth
                label="Familiyasi *"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              />
              <TextField
                fullWidth
                label="Ismi *"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              />
            </Stack>

            <TextField
              fullWidth
              label="Otasining ismi"
              value={formData.middle_name}
              onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
            />

            <Stack direction="row" spacing={2}>
              <TextField
                fullWidth
                type="date"
                label="Tug‘ilgan sanasi"
                InputLabelProps={{ shrink: true }}
                value={formData.birth_date}
                onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
              />
              <TextField
                fullWidth
                type="date"
                label="Vafot etgan sanasi *"
                InputLabelProps={{ shrink: true }}
                value={formData.death_date}
                onChange={(e) => setFormData({ ...formData, death_date: e.target.value })}
              />
            </Stack>

            <Stack direction="row" spacing={2}>
              <TextField
                select
                fullWidth
                label="Jinsi"
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              >
                <MenuItem value="MALE">Erkak</MenuItem>
                <MenuItem value="FEMALE">Ayol</MenuItem>
              </TextField>

              <TextField
                fullWidth
                label="Qabr raqami / Sektor"
                value={formData.grave_number}
                onChange={(e) => setFormData({ ...formData, grave_number: e.target.value })}
              />
            </Stack>

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Tarjimai holi va ibratli xotiralari"
              value={formData.biography}
              onChange={(e) => setFormData({ ...formData, biography: e.target.value })}
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenCreateModal(false)}>Bekor qilish</Button>
          <Button variant="contained" onClick={handleCreateSubmit} sx={{ bgcolor: '#1E3A2F' }}>
            Saqlash va QR Yaratish
          </Button>
        </DialogActions>
      </Dialog>

      {/* ================= QARINDOSHLIK BIRIKTIRISH MODAL ================= */}
      <Dialog open={openRelationModal} onClose={() => setOpenRelationModal(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700, color: '#1E3A2F' }}>
          Ota-ona yoki Turmush o‘rtoq biriktirish
        </DialogTitle>
        <DialogContent dividers>
          {formError && <Alert severity="error" sx={{ mb: 2 }}>{formError}</Alert>}

          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <TextField
              select
              fullWidth
              label="Farzand (Shaxs) *"
              value={relationData.child_id}
              onChange={(e) => setRelationData({ ...relationData, child_id: e.target.value })}
            >
              {persons.map((p) => (
                <MenuItem key={p.id} value={p.id}>
                  {p.full_name} ({p.death_date?.slice(0, 4)})
                </MenuItem>
              ))}
            </TextField>

            <TextField
              select
              fullWidth
              label="Ota / Ona yoki Jufti *"
              value={relationData.parent_id}
              onChange={(e) => setRelationData({ ...relationData, parent_id: e.target.value })}
            >
              {persons
                .filter((p) => p.id !== Number(relationData.child_id))
                .map((p) => (
                  <MenuItem key={p.id} value={p.id}>
                    {p.full_name} ({p.death_date?.slice(0, 4)})
                  </MenuItem>
                ))}
            </TextField>

            <TextField
              select
              fullWidth
              label="Aloqa turi"
              value={relationData.relationship_type}
              onChange={(e) => setRelationData({ ...relationData, relationship_type: e.target.value })}
            >
              <MenuItem value="PARENT">Ota / Ona</MenuItem>
              <MenuItem value="SPOUSE">Turmush o‘rtog‘i</MenuItem>
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenRelationModal(false)}>Bekor qilish</Button>
          <Button variant="contained" onClick={handleRelationSubmit} sx={{ bgcolor: '#1E3A2F' }}>
            Biriktirish
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};
