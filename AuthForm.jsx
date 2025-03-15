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
  background: linear-gradient(135deg, rgb(0, 0, 0), rgb(104, 52, 52));
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

const FormTitle = styled.h2`
  margin-bottom: 2rem;
  font-size: 2.5rem;
  color: rgb(0, 0, 0);
`;

const StyledLabel = styled.label`
  display: block;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: rgb(0, 0, 0);
`;

const StyledInput = styled.input`
  width: 100%;
  padding: 1rem;
  margin-top: 0.5rem;
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

const SubmitButton = styled.button`
  width: 100%;
  padding: 1rem;
  margin-top: 2rem;
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

const ForgotPasswordLink = styled.a`
  display: block;
  margin-top: 1rem;
  color: #4e54c8;
  text-decoration: none;
  cursor: pointer;

  &:hover {
    text-decoration: underline;
  }
`;

const AuthForm = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState('login'); // 'login', 'signup', 'forgot-password'
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    phone: '',
    password: '',
    new_password: ''
  });
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false); // To prevent multiple submissions

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading) return; // Prevent multiple submissions
    setIsLoading(true);

    let endpoint, data;

    switch (mode) {
      case 'signup':
        endpoint = '/api/signup';
        data = {
          username: formData.username,
          email: formData.email,
          phone: formData.phone,
          password: formData.password
        };
        break;
      case 'login':
        endpoint = '/api/login';
        data = {
          email: formData.email,
          password: formData.password
        };
        break;
      case 'forgot-password':
        endpoint = '/api/forgot-password';
        data = {
          email: formData.email
        };
        break;
      default:
        setIsLoading(false);
        return;
    }

    try {
      const response = await axios.post(`http://localhost:5000${endpoint}`, data, { withCredentials: true });

      if (response.data.message === "User registered successfully!") {
        alert('User registered successfully!');
        setMode('login'); // Switch to login form after successful signup
      } else if (response.data.message === "Login successful!") {
        alert('Login successful!');
        localStorage.setItem('user', JSON.stringify(response.data));
        navigate('/dashboard');
      } else if (response.data.message === "Password reset email sent successfully!") {
        alert('Password reset email sent successfully!');
        setMode('login'); // Switch to login form after successful password reset email sent
      } else {
        setErrorMessage(response.data.error || 'Failed to register, login, or reset password.');
      }
    } catch (error) {
      console.error('Full error:', error);
      setErrorMessage(error.response?.data?.error || 'Request failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setFormData({
      username: '',
      email: '',
      phone: '',
      password: '',
      new_password: ''
    });
    setErrorMessage('');
  };

  return (
    <AuthContainer>
      <StyledAuthForm>
        <FormTitle>
          {mode === 'signup' ? 'Create Account' : mode === 'login' ? 'Welcome Back!' : 'Reset Password'}
        </FormTitle>
        {errorMessage && <p style={{ color: 'red', marginBottom: '1rem' }}>{errorMessage}</p>}
        <form onSubmit={handleSubmit}>
          {mode === 'signup' && (
            <StyledLabel>
              Name:
              <StyledInput
                type="text"
                name="username"
                placeholder="Name"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </StyledLabel>
          )}
          <StyledLabel>
            Email:
            <StyledInput
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </StyledLabel>
          {mode === 'signup' && (
            <StyledLabel>
              Phone Number:
              <StyledInput
                type="text"
                name="phone"
                placeholder="Phone Number"
                value={formData.phone}
                onChange={handleChange}
                required
              />
            </StyledLabel>
          )}
          {(mode === 'signup' || mode === 'login') && (
            <StyledLabel>
              Password:
              <StyledInput
                type="password"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </StyledLabel>
          )}
          {mode === 'forgot-password' && (
            <StyledLabel>
              Email:
              <StyledInput
                type="email"
                name="email"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </StyledLabel>
          )}
          <SubmitButton type="submit" disabled={isLoading}>
            {isLoading ? 'Loading...' : (mode === 'signup' ? 'Sign Up' : mode === 'login' ? 'Login' : 'Reset Password')}
          </SubmitButton>
          {mode === 'login' && (
            <ForgotPasswordLink onClick={() => handleModeChange('forgot-password')}>
              Forgot Password?
            </ForgotPasswordLink>
          )}
          <SwitchButton onClick={() => handleModeChange(mode === 'signup' ? 'login' : 'signup')}>
            {mode === 'signup' ? 'Already have an account? Login' : "Don't have an account? Sign Up"}
          </SwitchButton>
        </form>
      </StyledAuthForm>
    </AuthContainer>
  );
};

export default AuthForm;
