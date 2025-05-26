import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const ProductEdit = () => {
    const { id } = useParams();
    const [product, setProduct] = useState({
        name: '',
        description: '',
        price: '',  // Изначально пустая строка
        category: null,
        images: [],
    });

    useEffect(() => {
        if (id) {
            axios.get(`/api/products/${id}/`)
                .then(response => {
                    const data = response.data;
                    // Конвертируем price в число только для внутреннего состояния, но храним как строку в state
                    setProduct({
                        ...data,
                        price: data.price.toString(),  // Всегда храним как строку в состоянии
                    });
                })
                .catch(error => console.error('Ошибка при загрузке товара:', error));
        }
    }, [id]);

    const handleChange = (e) => {
        const { name, value } = e.target;

        setProduct(prev => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleUpdate = async (e) => {
        e.preventDefault();

        try {
            // Перед отправкой преобразуем price обратно в число
            const payload = {
                ...product,
                price: parseFloat(product.price),
                category: parseInt(product.category),
            };

            await axios.put(`/api/products/${id}/update/`, payload);
            alert('Товар успешно обновлен');
        } catch (error) {
            console.error('Ошибка при обновлении товара:', error);
            alert('Не удалось обновить товар.');
        }
    };

    return (
        <div>
            <h2>Редактирование товара</h2>
            <form onSubmit={handleUpdate}>
                <div>
                    <label>Название:</label>
                    <input
                        type="text"
                        name="name"
                        value={product.name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div>
                    <label>Описание:</label>
                    <textarea
                        name="description"
                        value={product.description}
                        onChange={handleChange}
                        rows="4"
                        required
                    />
                </div>

                <div>
                    <label>Цена:</label>
                    <input
                        type="number"
                        name="price"
                        value={product.price}
                        onChange={handleChange}
                        step="0.01"
                        min="0"
                        required
                    />
                </div>

                <div>
                    <label>Категория:</label>
                    <input
                        type="number"
                        name="category"
                        value={product.category || ''}
                        onChange={handleChange}
                        placeholder="ID категории"
                        required
                    />
                </div>

                <button type="submit">Сохранить изменения</button>
            </form>
        </div>
    );
};

export default ProductEdit;