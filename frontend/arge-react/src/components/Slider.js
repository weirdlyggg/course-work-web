import React from 'react';
import { Link } from 'react-router-dom';

const Slider = () => {
    const slides = [
        { id: 1, title: 'Коллекция 1', path: '/collection1' },
        { id: 2, title: 'Коллекция 2', path: '/collection2' },
        { id: 3, title: 'Коллекция 3', path: '/collection3' },
    ];

    return (
        <div className="slider">
            {slides.map((slide) => (
                <Link key={slide.id} to={slide.path} className="slide">
                    <h3>{slide.title}</h3>
                </Link>
            ))}
        </div>
    );
};

export default Slider;