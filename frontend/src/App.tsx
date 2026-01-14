import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { WeatherPage } from './pages/WeatherPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/weather" element={<WeatherPage />} />
        <Route path="/" element={<Navigate to="/weather" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
