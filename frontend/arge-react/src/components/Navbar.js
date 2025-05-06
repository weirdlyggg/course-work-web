import React from 'react';
import './Navbar.css'
import { Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <div className='category'>
            <Link className='menu__link' to="/Home">главная</Link>
            <Link className='menu__link' to="/">категории</Link>
            <Link className='menu__link' to="/About">о нас</Link>
            
        </div>
    );
};

export default Navbar;