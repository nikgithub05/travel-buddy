# Trip Planner

A Flask and React-based project that generates personalized travel itineraries based on user preferences like destination, budget, and activities.

## 📁 Project Structure

```
trip-planner/
├── node_modules/        # React dependencies (auto-generated)
├── public/             # Static assets (React)
│   └── index.html      # Main HTML template for React
└── src/                # React components
    ├── components/     # React UI components
    │     ├── AuthForm.jsx    # User authentication form (e.g., login/signup)
    │     └── Dashboard.jsx   # Main dashboard with travel preference form
    ├── App.js          # Main React component
    └── index.js        # React entry point
├── app.py              # Main Flask app (initializes server and routes)
├── userdb.py           # Handles user-related operations (e.g., storing user data)
├── preference.py       # Handles travel preferences (Flask Blueprint)
├── package.json        # Project metadata and dependencies
```

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd trip-planner
```

### 2. Set Up Flask Backend

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask app:
   ```bash
   python app.py
   ```

### 3. Set Up React Frontend

1. Ensure you're in the project root:
   ```bash
   cd trip-planner
   ```

2. Install React dependencies:
   ```bash
   npm install
   ```

3. Start the React app:
   ```bash
   npm start
   ```

### 4. Access the Application
Visit **http://localhost:3000** to use the trip-planner UI.

## 📌 Key Features

- **AuthForm.jsx**: Provides a user login/signup interface.
- **Dashboard.jsx**: Collects destination, travel dates, budget, activities, and group size. Sends data to `/api/generate-itinerary`.
- **API Integration**: Connects the React UI to Flask for dynamic itinerary generation.

## 📚 Explanation of Core Files

1. **app.py**: Main Flask entry point that initializes the server and registers blueprints.

2. **preference.py**: Handles travel preference logic and processes `/api/generate-itinerary` requests.

3. **userdb.py**: Manages user-related functions like data storage and validation.

4. **React UI**: 
   - `AuthForm.jsx`: User authentication form.
   - `Dashboard.jsx`: Travel preferences form for itinerary generation.

## ✅ Future Improvements
- Enhance itinerary with third-party APIs (e.g., Google Maps).
- Add persistent user authentication and save plans.
- Implement detailed error handling and form validation.
