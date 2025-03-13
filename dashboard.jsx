// Dashboard.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #6a11cb, #2575fc);
`;

const FormWrapper = styled.div`
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 100%;
  color: #fff;
`;

const Title = styled.h2`
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
`;

const StyledLabel = styled.label`
  display: block;
  margin-bottom: 1rem;
  font-size: 1.1rem;
`;

const StyledInput = styled.input`
  width: 100%;
  padding: 0.8rem;
  margin-top: 0.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
`;

const StyledSelect = styled.select`
  ${StyledInput}
`;

const CheckboxWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SubmitButton = styled.button`
  width: 100%;
  padding: 1rem;
  margin-top: 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1.2rem;
  background: #4caf50;
  color: white;
  cursor: pointer;
  transition: background 0.3s;

  &:hover {
    background: #45a049;
  }
`;

const Dashboard = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    user_id: 1, // Static user_id for now (replace with dynamic if needed)
    destination: '',
    start_date: '',
    end_date: '',
    budget: '',
    activities: [],
    groupSize: '',
  });

  const activitiesOptions = ['Hiking', 'Beach', 'City Tour', 'Adventure', 'Relaxation'];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (type === 'checkbox') {
      setFormData((prev) => ({
        ...prev,
        activities: checked
          ? [...prev.activities, value]
          : prev.activities.filter((activity) => activity !== value),
      }));
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const submissionData = {
      user_id: formData.user_id,
      destination: formData.destination,
      start_date: formData.start_date,
      end_date: formData.end_date,
      budget: formData.budget,
      activities: formData.activities,
      group_size: formData.groupSize,
    };

    if (
      !submissionData.destination ||
      !submissionData.start_date ||
      !submissionData.end_date ||
      !submissionData.budget ||
      !submissionData.group_size ||
      submissionData.activities.length === 0
    ) {
      alert('All fields are required!');
      return;
    }

    try {
      const response = await axios.post(
        'http://localhost:5000/generate-ai-itinerary',
        submissionData,
        { withCredentials: true }
      );

      alert('Itinerary generated successfully!');
      navigate('/tripplan', { state: { itinerary: response.data } });
    } catch (error) {
      console.error('Full error:', error);
      alert('Error: ' + (error.response?.data?.error || 'Request failed'));
    }
  };

  return (
    <DashboardContainer>
      <FormWrapper>
        <Title>Travel Preferences Form</Title>
        <form onSubmit={handleSubmit}>
          <StyledLabel>
            Destination:
            <StyledInput
              type="text"
              name="destination"
              value={formData.destination}
              onChange={handleChange}
              required
            />
          </StyledLabel>

          <StyledLabel>
            Start Date:
            <StyledInput
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleChange}
              required
            />
          </StyledLabel>

          <StyledLabel>
            End Date:
            <StyledInput
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleChange}
              required
            />
          </StyledLabel>

          <StyledLabel>
            Budget (in INR):
            <StyledInput
              type="number"
              name="budget"
              value={formData.budget}
              onChange={handleChange}
              required
            />
          </StyledLabel>

          <StyledLabel>Activities:</StyledLabel>
          <CheckboxWrapper>
            {activitiesOptions.map((activity) => (
              <CheckboxLabel key={activity}>
                <input
                  type="checkbox"
                  name="activities"
                  value={activity}
                  checked={formData.activities.includes(activity)}
                  onChange={handleChange}
                />
                {activity}
              </CheckboxLabel>
            ))}
          </CheckboxWrapper>

          <StyledLabel>
            Group Size:
            <StyledSelect
              name="groupSize"
              value={formData.groupSize}
              onChange={handleChange}
              required
            >
              <option value="">Select group size</option>
              <option value="1">1 Person</option>
              <option value="2">2 People</option>
              <option value="3-5">3-5 People</option>
              <option value="6+">6+ People</option>
            </StyledSelect>
          </StyledLabel>

          <SubmitButton type="submit">Submit</SubmitButton>
        </form>
      </FormWrapper>
    </DashboardContainer>
  );
};

export default Dashboard;
