import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';

const TripPlanContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #6a11cb, #2575fc);
  font-family: Arial, sans-serif;
`;

const ItineraryWrapper = styled.div`
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 100%;
  color: #fff;
`;

const Title = styled.h2`
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
`;

const DayCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
  animation: slideIn 0.5s forwards;

  @keyframes slideIn {
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const DayHeader = styled.h3`
  font-size: 2rem;
  margin-bottom: 1rem;
`;

const Activity = styled.p`
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
`;

const TripPlan = () => {
  const location = useLocation();
  const [itinerary, setItinerary] = useState(location.state?.itinerary || {});
  const [animatedDays, setAnimatedDays] = useState([]);

  useEffect(() => {
    // Fetch itinerary if not passed via state
    if (!itinerary.itinerary) {
      const fetchItinerary = async () => {
        try {
          const response = await fetch('http://localhost:5000/generate-itinerary');
          const data = await response.json();
          setItinerary(data);
        } catch (error) {
          console.error("Error fetching itinerary:", error);
        }
      };
      fetchItinerary();
    } else {
      // Animate days one after another
      const animateDays = () => {
        const days = itinerary.itinerary;
        let delay = 0;
        const animatedDaysArray = [];
        days.forEach((day, index) => {
          setTimeout(() => {
            setAnimatedDays(prevDays => [...prevDays, day]);
          }, delay);
          delay += 300; // Delay between each day's animation
        });
      };
      animateDays();
    }
  }, [itinerary]);

  return (
    <TripPlanContainer>
      <ItineraryWrapper>
        <Title>Your Trip Itinerary</Title>
        {animatedDays.length > 0 ? (
          animatedDays.map((day, index) => (
            <DayCard key={index} style={{ animationDelay: `${index * 0.3}s` }}>
              <DayHeader>Day {day.day}</DayHeader>
              <Activity>Morning: {day.morning}</Activity>
              <Activity>Afternoon: {day.afternoon}</Activity>
              <Activity>Evening: {day.evening}</Activity>
            </DayCard>
          ))
        ) : (
          <p>Loading itinerary...</p>
        )}
      </ItineraryWrapper>
    </TripPlanContainer>
  );
};

export default TripPlan;
