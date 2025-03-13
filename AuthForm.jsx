import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const AuthContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;  
  background: linear-gradient(135deg,rgb(0, 0, 0),rgb(104, 52, 52));
`;

const StyledAuthForm = styled.div`  
  background: rgba(159, 158, 91, 0.74);
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 400px;
  text-align: center;
  backdrop-filter: blur(10px);
`;

const FormTitle = styled.h1`
  margin-bottom: 2rem;
  font-size: 2.5rem;
  color:rgb(0, 0, 0);
`;

const FormInput = styled.input`
  width: 100%;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  background: #f0f2f5;
  transition: background 0.3s ease;

  &:focus {
    background: #e2e6f0;
  }
`;

const FormButton = styled.button`
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  border: none;
  border-radius: 12px;
  background: #6a11cb;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background 0.3s ease;

  &:hover {
    background: #4e54c8;
  }
`;

const SwitchButton = styled.button`
  margin-top: 1rem;
  border: none;
  background: none;
  color: #4e54c8;
  font-size: 1rem;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

const AuthForm = () => {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = isSignUp ? '/api/signup' : '/api/login';

    try {
      const response = await axios.post(`http://localhost:5000${endpoint}`, formData);
      alert(response.data.message);

      if (!isSignUp) {
        localStorage.setItem('token', response.data.token);
        navigate('/dashboard');
      }
    } catch (error) {
      alert('Error: ' + (error.response?.data?.error || 'Request failed'));
    }
  };

  return (
    <AuthContainer>
      <StyledAuthForm>
        <FormTitle>{isSignUp ? 'Create Account' : 'Welcome Back!'}</FormTitle>
        <form onSubmit={handleSubmit}>
          {isSignUp && (
            <FormInput
              type="text"
              name="username"
              placeholder="Name"
              value={formData.username}
              onChange={handleChange}
              required
            />
          )}
          <FormInput
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          {isSignUp && (
            <FormInput
              type="text"
              name="phone"
              placeholder="Phone Number"
              value={formData.phone}
              onChange={handleChange}
              required
            />
          )}
          <FormInput
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <FormButton type="submit">{isSignUp ? 'Sign Up' : 'Login'}</FormButton>
        </form>
        <SwitchButton onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp ? 'Already have an account? Login' : "Don't have an account? Sign Up"}
        </SwitchButton>
      </StyledAuthForm>
    </AuthContainer>
  );
};

export default AuthForm;
