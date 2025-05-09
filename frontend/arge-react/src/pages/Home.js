import React, { useEffect, useState } from 'react';
import { fetchProducts } from '../api';
import './Home.css';
import Slider from '../components/Slider.js';

const Home = () => {
    const [products, setProducts] = useState([]);
  
    useEffect(() => {
      fetchProducts()
        .then(response => {
          setProducts(response.data.results); // Если используется пагинация
        })
        .catch(error => {
          console.error('Error fetching products:', error);
        });
    }, []);
  
    return (
      <div>
        <div className='first__content'>
          <Slider slides={products} />
        </div>
      </div>
    );
  };
  
  export default Home;