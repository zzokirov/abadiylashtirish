import axios from 'axios';
import { PublicDeceased, FamilyTreeData } from '../types';

// Docker/nginx ortida API shu domenning o'zida (/api/v1) joylashgan.
// Alohida dev serverda ishlatish uchun: VITE_API_URL=http://localhost:8000/api/v1
export const API_BASE_URL: string = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // Django sessiyasi (admin login) va CSRF himoyasi bilan ishlash uchun
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Skanerlanganda keshni butunlay chetlab o'tish uchun har safar timestamp qo'shamiz.
// (Maxsus Cache-Control so'rov sarlavhalari CORS preflight'ni keltirib chiqarardi.)
apiClient.interceptors.request.use((config) => {
  if (!config.method || config.method.toLowerCase() === 'get') {
    config.params = {
      ...config.params,
      _t: Date.now(),
    };
  }
  return config;
});

export const memorialApi = {
  /**
   * Marhumning asosiy ma'lumotlarini yuklash
   */
  async getDeceasedByToken(token: string): Promise<PublicDeceased> {
    const response = await apiClient.get<PublicDeceased>(`/public/deceased/${token}/`);
    return response.data;
  },

  /**
   * Marhumning dinamik shajarasini yuklash
   */
  async getFamilyTreeByToken(token: string): Promise<FamilyTreeData> {
    const response = await apiClient.get<FamilyTreeData>(`/public/deceased/${token}/tree/`);
    return response.data;
  },
};
