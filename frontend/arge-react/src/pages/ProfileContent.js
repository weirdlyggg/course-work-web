import React from 'react';
import { useAuth } from '../context/AuthContext';

const ProfileContent = () => {
    const { user } = useAuth();

    return (
        <div>
            <h3>Добро пожаловать, {user.first_name || 'Пользователь'}!</h3>
            <p>Email: {user.email}</p>
            <p>Имя: {user.first_name} {user.last_name}</p>

            {/* Сюда можно добавить дополнительные данные */}
        </div>
    );
};

export default ProfileContent;