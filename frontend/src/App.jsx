import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(false);

  // Create API client with auth token
  const createClient = () => {
    const token = localStorage.getItem('access_token');
    return axios.create({
      baseURL: API_BASE_URL,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  };

  // Load vehicles
  const loadVehicles = async () => {
    setLoading(true);
    try {
      const client = createClient();
      const response = await client.get('/tenant/vehicles');
      setVehicles(response.data);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  // Login handler
  const handleLogin = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password,
      });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      setIsLoggedIn(true);
      loadVehicles();
    } catch (error) {
      console.error('Login failed:', error);
      alert('Invalid credentials');
    }
  };

  // Logout handler
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsLoggedIn(false);
    setVehicles([]);
  };

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
      loadVehicles();
    }
  }, []);

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-r from-indigo-600 to-blue-600 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Vehicle Rental SaaS</h1>
          <LoginForm onLogin={handleLogin} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Vehicle Rental SaaS</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </nav>

      {/* Dashboard */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>

        {/* Vehicles Section */}
        <section className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Vehicles</h3>
          {loading ? (
            <p className="text-gray-500">Loading...</p>
          ) : vehicles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {vehicles.map((vehicle) => (
                <div key={vehicle.id} className="border rounded-lg p-4">
                  <h4 className="font-bold text-lg">
                    {vehicle.brand} {vehicle.model}
                  </h4>
                  <p className="text-gray-600">Year: {vehicle.year}</p>
                  <p className="text-gray-600">Plate: {vehicle.license_plate}</p>
                  <p className="text-indigo-600 font-bold">${vehicle.daily_rate}/day</p>
                  <span
                    className={`inline-block mt-2 px-3 py-1 rounded text-white text-sm ${
                      vehicle.status === 'available'
                        ? 'bg-green-600'
                        : vehicle.status === 'rented'
                        ? 'bg-orange-600'
                        : 'bg-gray-600'
                    }`}
                  >
                    {vehicle.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No vehicles found. Create one to get started!</p>
          )}
        </section>
      </main>
    </div>
  );
}

function LoginForm({ onLogin }) {
  const [email, setEmail] = useState('company@example.com');
  const [password, setPassword] = useState('Company@123456');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(email, password);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
        />
      </div>
      <button
        type="submit"
        className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium"
      >
        Login
      </button>
    </form>
  );
}

export default App;
