import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';
import Collection1 from './pages/Collection1';
import Collection2 from './pages/Collection2';
import Collection3 from './pages/Collection3';
import Login from './components/Login';
import Register from './components/Register';
import ProductCreate from './pages/ProductCreate';
import ProductEdit from './pages/ProductEdit';
import Profile from './pages/Profile';
import AdminRoute from './components/AdminRoute';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Navbar />
                  <Routes>
                      <Route path="/profile/" element={<Profile />} />
                      <Route path="/" element={<Home />} />
                      <Route path="/about" element={<About />} />
                      <Route path="/collection1" element={<Collection1 />} />
                      <Route path="/collection2" element={<Collection2 />} />
                      <Route path="/collection3" element={<Collection3 />} />

                      <Route path="/login" element={<Login />} />
                      <Route path="/register" element={<Register />} />
                      <Route path="/profile/" element={<Profile />} />
                        {/* Только для админов */}
                      <Route path="/products/create/" element={
                              <AdminRoute>
                                  <ProductCreate />
                              </AdminRoute>
                          }/>
                      <Route path="/products/edit/:id" element={
                              <AdminRoute>
                                  <ProductEdit />
                              </AdminRoute>
                          } />
                  </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;