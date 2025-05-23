import React, { useEffect, useState } from 'react';
import { fetchLatestProducts } from '../api';
import './Home.css';
import Slider from '../components/Slider.js';


const Home = () => {
    const [products, setProducts] = useState([]);
  
    useEffect(() => {
      fetchLatestProducts()
        .then(response => {
          setProducts(response.data); 
         })
        .catch(error => {
          console.error('Ошибка при получении новинок:', error);
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