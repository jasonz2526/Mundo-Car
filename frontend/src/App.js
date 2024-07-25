import './App.css';
import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import PlayerStats from './PlayerStats';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import axios from 'axios';
import splashArtsData from './splash_arts.json';
import { io } from 'socket.io-client';
import DataStats from './DataStats';

const championNames = ['N/A', ...Object.keys(splashArtsData)];

const regionOptions = [
  { value: 'NA', label: 'North America' },
  { value: 'JP', label: 'Japan' },
  { value: 'EUW', label: 'Europe West' },
  { value: 'EUNE', label: 'Europe Nordic & East' },
  { value: 'BR', label: 'Brazil' },
  { value: 'KR', label: 'Korea' }
];

const roleOptions = [
  { value: 'N/A', label: 'N/A' },
  { value: 'TOP', label: 'Top' },
  { value: 'JGL', label: 'Jungle' },
  { value: 'MID', label: 'Middle' },
  { value: 'BOT', label: 'Bottom' },
  { value: 'SUP', label: 'Support' }
]

function App() {
  const navigate = useNavigate();
  //const socket = io('http://127.0.0.1:5000');
  const socket = io();
  const evelynnSplashArts = splashArtsData['Evelynn'];
  const initialBackgroundImage = evelynnSplashArts[0];
  const [backgroundImage, setBackgroundImage] = useState(initialBackgroundImage);
  const [splashArts, setSplashArts] = useState(evelynnSplashArts);
  const [summonerName, setSummonerName] = useState('');
  const [tagline, setTagline] = useState('');
  const [role, setRoles] = useState('');
  const [region, setRegion] = useState('');
  const [selectedChampion, setSelectedChampion] = useState({ label: 'Evelynn', value: 'Evelynn' });
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (selectedChampion.value && splashArtsData[selectedChampion.value]) {
      setSplashArts(splashArtsData[selectedChampion.value]);
    }
  }, [selectedChampion]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (splashArts.length > 0) {
        const randomIndex = Math.floor(Math.random() * splashArts.length);
        setBackgroundImage(splashArts[randomIndex]);
      }
    }, 5000); // Change background every 5 seconds

    return () => clearInterval(interval);
  }, [splashArts]);

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    socket.on('progress', (data) => {
      console.log('Progress data received:', data);
      setProgress(data.progress);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    return () => {
      socket.off('connect');
      socket.off('progress');
      socket.off('disconnect');
    };
  }, [socket]);

  const handleSummonerNameChange = (event) => {
    setSummonerName(event.target.value);
  };

  const handleTaglineChange = (event) => {
    setTagline(event.target.value);
  };

  const handleRoleChange = (selectedOption) => {
    setRoles(selectedOption.value);
  }

  const handleRegionChange = (selectedOption) => {
    setRegion(selectedOption.value);
  };

  const handleChampionChange = (selectedOption) => {
    setSelectedChampion(selectedOption);
  };
  
  const handleSubmit = async (event) => {
    event.preventDefault(); 
    if (loading) return; 
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/get_everything', {
        summonerName,
        tagline,
        role,
        region,
        selectedChampion: selectedChampion.value // Ensure only value is sent
      });

      if (response.status === 404) {
        alert('One of the fields is invalid. Please check your input.');
        return;
      }

      navigate('/data-stats', {
        state: {
          summonerName,
          tagline,
          role,
          region,
          selectedChampion: selectedChampion.value,
          data: response.data // Pass the server response to the next page
        }
      });
      
    } catch (error) {
      console.error('Error submitting data:', error);
      alert('Error submitting data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    const input = inputValue.toLowerCase();
    const label = option.label.toLowerCase();
    return label.startsWith(input); 
  };  

  return (
    <div className="App" style={{ backgroundImage: `url(${backgroundImage})` }}>
     <div className={`top-inputs ${loading ? 'loading-active' : ''}`}>
        <input
          type="text"
          value={summonerName}
          onChange={handleSummonerNameChange}
          placeholder="Summoner Name"
          className="name-input"
        />
        <input
          type="text"
          value={tagline}
          onChange={handleTaglineChange}
          placeholder="Tagline"
          className="tag-input"
        />
        <Select
          value={roleOptions.find(option => option.value === role)}
          onChange={handleRoleChange}
          options={roleOptions}
          placeholder="Role"
          className="select-input"
        />
        <Select
          value={regionOptions.find(option => option.value === region)}
          onChange={handleRegionChange}
          options={regionOptions}
          placeholder="Region"
          className="select-input"
        />
        <Select
          value={championNames.find(champion => champion === selectedChampion)}
          onChange={handleChampionChange}
          options={championNames.map(champion => ({ label: champion, value: champion }))}
          isSearchable
          placeholder="Champion"
          filterOption={customFilterOption}
          className="select-input"
        />
        <button onClick={handleSubmit} className="submit-button">Search</button>
      </div>
      {loading && (
        <div className="loading-container">
          <div className="loading-bar" style={{ width: `${progress}%` }}></div>
        </div>
      )}
    </div>
  );
}

function RootApp() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/data-stats" element={<DataStats />} />
      </Routes>
    </Router>
  );
}

export default RootApp;