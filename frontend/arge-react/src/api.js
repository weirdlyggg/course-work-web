import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // URL вашего Django-сервера
  headers: {
    'Content-Type': 'application/json',
  },
});

// Получить список товаров
export const fetchLatestProducts = () => {
  return axios.get('/api/products/latest/');
};

// Получить детали товара
export const fetchProductDetail = (productId) => api.get(`/api/product/${productId}/`);

// Получить список пользователей
export const fetchUsers = () => api.get('/api/members/');

// Регистрация пользователя
export const registerUser = (userData) => api.post('/api/register/', userData);

// Вход пользователя
export const login = (credentials) => api.post('/api/login/', credentials);