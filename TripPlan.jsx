import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './tripplan.css';

// Custom icon for markers
import L from 'leaflet';
import markerIconUrl from 'leaflet/dist/images/marker-icon.png';

const DefaultIcon = L.icon({
  iconUrl: markerIconUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const TripPlanContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg,rgba(85, 14, 160, 0.84),rgba(28, 81, 171, 0.81));
  font-family: Arial, sans-serif;
  flex-direction: column;
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
  margin-bottom: 2rem;
`;

const MapWrapper = styled.div`
  width: 100%;
  height: 400px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
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
  const [center, setCenter] = useState([51.505, -0.09]); // Default center

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

      // Set map center to the first day's location if available
      if (itinerary.itinerary.length > 0 && itinerary.itinerary[0].morning_location) {
        setCenter(itinerary.itinerary[0].morning_location);
      }
    }
  }, [itinerary]);

  return (
    <TripPlanContainer>
      <MapWrapper>
        <MapContainer center={center} zoom={13} scrollWheelZoom={false}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {animatedDays.map((day, index) => (
            <>
              {day.morning_location && (
                <Marker key={`morning-${index}`} position={day.morning_location}>
                  <Popup>
                    Day {day.day} Morning: {day.morning}
                  </Popup>
                </Marker>
              )}
              {day.afternoon_location && (
                <Marker key={`afternoon-${index}`} position={day.afternoon_location}>
                  <Popup>
                    Day {day.day} Afternoon: {day.afternoon}
                  </Popup>
                </Marker>
              )}
              {day.evening_location && (
                <Marker key={`evening-${index}`} position={day.evening_location}>
                  <Popup>
                    Day {day.day} Evening: {day.evening}
                  </Popup>
                </Marker>
              )}
            </>
          ))}
        </MapContainer>
      </MapWrapper>
      <ItineraryWrapper>
        <Title>Your Trip Itinerary</Title>
        {animatedDays.length > 0 ? (
          animatedDays.map((day, index) => (
            <DayCard key={index} style={{ animationDelay: `${index * 0.3}s` }}>
              <DayHeader>Day {day.day}</DayHeader>
              {day.morning && <Activity>Morning: {day.morning}</Activity>}
              {day.afternoon && <Activity>Afternoon: {day.afternoon}</Activity>}
              {day.evening && <Activity>Evening: {day.evening}</Activity>}
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
