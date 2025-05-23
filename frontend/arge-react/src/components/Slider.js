import React from 'react';
import { Link } from 'react-router-dom';

const Slider = ({ slides }) => {
  return (
    <div className="slider">
      {slides.map(product => (
        <div key={product.id} className="slide">
            {product.images.length > 0 && (
            <img src={product.images[0].img} alt={product.name} style={{ width: '200px' }} />
            )}
            <h3>{product.name}</h3>
            <p>{product.price} ₽</p>
        </div>
      ))}
    </div>
  );
};


export default Slider;