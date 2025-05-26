import React, { useState } from 'react';
import axios from 'axios';

const ProductCreate = () => {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: '',
        category: '',  // ID категории
        status: 'available'
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/api/products/create/', formData);
            alert('Товар успешно создан!');
        } catch (error) {
            console.error('Ошибка при создании товара:', error);
            alert('Не удалось создать товар.');
        }
    };

    return (
        <div>
            <h2>Добавить товар</h2>
            <form onSubmit={handleSubmit}>
                <input name="name" value={formData.name} onChange={handleChange} placeholder="Название" required />
                <textarea name="description" value={formData.description} onChange={handleChange} placeholder="Описание" rows="4" required />
                <input type="number" name="price" value={formData.price} onChange={handleChange} placeholder="Цена" required />
                <input name="category" value={formData.category} onChange={handleChange} placeholder="ID категории" required />

                <button type="submit">Сохранить</button>
            </form>
        </div>
    );
};

export default ProductCreate;