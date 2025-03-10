import React, { useState } from 'react';
import axios from 'axios';

const Dashboard = () => {
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

    const { destination, start_date, end_date, budget, activities, groupSize } = formData;

    if (!destination || !start_date || !end_date || !budget || !groupSize || activities.length === 0) {
      alert('All fields are required!');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5000/api/generate-itinerary', formData, {
        withCredentials: true, // Ensure cookies and headers are sent
      });
      alert('Itinerary generated successfully!');
      console.log(response.data);
    } catch (error) {
      alert('Error: ' + (error.response?.data?.error || 'Request failed'));
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto bg-white shadow-md rounded-2xl">
      <h2 className="text-2xl font-semibold mb-6">Travel Preferences Form</h2>
      <form onSubmit={handleSubmit}>
        <label className="block mb-4">
          Destination:
          <input
            type="text"
            name="destination"
            value={formData.destination}
            onChange={handleChange}
            required
            className="w-full mt-2 p-2 border rounded-lg"
          />
        </label>

        <label className="block mb-4">
          Start Date:
          <input
            type="date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            required
            className="w-full mt-2 p-2 border rounded-lg"
          />
        </label>

        <label className="block mb-4">
          End Date:
          <input
            type="date"
            name="end_date"
            value={formData.end_date}
            onChange={handleChange}
            required
            className="w-full mt-2 p-2 border rounded-lg"
          />
        </label>

        <label className="block mb-4">
          Budget (in INR):
          <input
            type="number"
            name="budget"
            value={formData.budget}
            onChange={handleChange}
            required
            className="w-full mt-2 p-2 border rounded-lg"
          />
        </label>

        <fieldset className="mb-4">
          <legend className="mb-2 font-medium">Activities:</legend>
          {activitiesOptions.map((activity) => (
            <label key={activity} className="inline-flex items-center mr-4">
              <input
                type="checkbox"
                name="activities"
                value={activity}
                checked={formData.activities.includes(activity)}
                onChange={handleChange}
                className="mr-2"
              />
              {activity}
            </label>
          ))}
        </fieldset>

        <label className="block mb-6">
          Group Size:
          <select
            name="groupSize"
            value={formData.groupSize}
            onChange={handleChange}
            required
            className="w-full mt-2 p-2 border rounded-lg"
          >
            <option value="">Select group size</option>
            <option value="1">1 Person</option>
            <option value="2">2 People</option>
            <option value="3-5">3-5 People</option>
            <option value="6+">6+ People</option>
          </select>
        </label>

        <button type="submit" className="bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600">
          Submit
        </button>
      </form>
    </div>
  );
};

export default Dashboard;
