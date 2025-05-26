
import { useAuth } from '../context/AuthContext';
import Login from '../components/Login';
import Register from '../components/Register';

// Предположим, что у вас есть компоненты Login и Register
// Также создайте ProfileContent — он будет отображаться после входа
import ProfileContent from './ProfileContent';

const Profile = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Загрузка...</div>;
    }

    return (
        <div>
            <h2>Личный кабинет</h2>
            {!user ? (
                <div>
                    <h3>Войдите или зарегистрируйтесь</h3>
                    <Login />
                    <hr />
                    <h3>Нет аккаунта?</h3>
                    <Register />
                </div>
            ) : (
                <ProfileContent /> // Покажем данные пользователя
            )}
        </div>
    );
};

export default Profile;