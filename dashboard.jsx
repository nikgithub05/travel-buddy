import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styled from 'styled-components';

const DashboardContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #6a11cb, #2575fc);
  font-family: Arial, sans-serif;
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
  transition: transform 0.3s ease-in-out;
  &:hover {
    transform: translateY(-10px);
  }
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
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  transition: background 0.3s ease-in-out, transform 0.3s ease-in-out;
  &:focus {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.02);
  }
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
  transition: background 0.3s ease-in-out, transform 0.3s ease-in-out;
  &:hover {
    background: #45a049;
    transform: scale(1.02);
  }
`;

const CurrentPreferences = styled.div`
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: opacity 0.3s ease-in-out;
  opacity: 0;
  animation: fadeIn 0.5s forwards;

  @keyframes fadeIn {
    to {
      opacity: 1;
    }
  }
`;

const PreferenceItem = styled.p`
  margin: 0.5rem 0;
  font-size: 1rem;
`;

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')));
  const [tripPreferences, setTripPreferences] = useState({});
  const [formData, setFormData] = useState({
    user_id: user ? user.user_id : 1, // Static user_id for now (replace with dynamic if needed)
    destination: '',
    start_date: '',
    end_date: '',
    budget: '',
    activities: [],
    group_size: '',
  });

  const activitiesOptions = ['Hiking', 'Beach', 'City Tour', 'Adventure', 'Relaxation'];

  useEffect(() => {
    if (user) {
      fetchTripPreferences(user.user_id);
    }
  }, [user]);

  const fetchTripPreferences = async (userId) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/trip-preferences/${userId}`);
      setTripPreferences(response.data);
      setFormData({
        user_id: userId,
        destination: response.data.destination || '',
        start_date: response.data.start_date || '',
        end_date: response.data.end_date || '',
        budget: response.data.budget || '',
        activities: response.data.activities || [],
        group_size: response.data.group_size || '',
      });
    } catch (error) {
      console.error("Error fetching trip preferences:", error);
    }
  };

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

  const readySetGo = async () => {
    try {
      const response = await axios.post(
        'http://localhost:5000/generate-itinerary',
        formData,
        { withCredentials: true }
      );
      alert("Preferences saved and itinerary generated successfully!");
      navigate('/tripplan', { state: { itinerary: response.data } });
    } catch (error) {
      console.error("Error saving preferences and generating itinerary:", error);
      alert("Failed to save preferences and generate itinerary.");
    }
  };

  return (
    <DashboardContainer>
      <FormWrapper>
        <Title>Travel Preferences Form</Title>
        <form onSubmit={(e) => e.preventDefault()}>
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
              name="group_size"
              value={formData.group_size}
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

          <SubmitButton type="button" onClick={readySetGo}>Ready. Set. GO</SubmitButton>
        </form>

        {/* {tripPreferences && Object.keys(tripPreferences).length > 0 && (
          <CurrentPreferences>
            <h3>Current Trip Preferences</h3>
            <PreferenceItem><strong>Destination:</strong> {tripPreferences.destination}</PreferenceItem>
            <PreferenceItem><strong>Start Date:</strong> {tripPreferences.start_date}</PreferenceItem>
            <PreferenceItem><strong>End Date:</strong> {tripPreferences.end_date}</PreferenceItem>
            <PreferenceItem><strong>Budget:</strong> {tripPreferences.budget}</PreferenceItem>
            <PreferenceItem><strong>Activities:</strong> {tripPreferences.activities.join(', ')}</PreferenceItem>
            <PreferenceItem><strong>Group Size:</strong> {tripPreferences.group_size}</PreferenceItem>
          </CurrentPreferences>
        )} */}
      </FormWrapper>
    </DashboardContainer>
  );
};

export default Dashboard;
