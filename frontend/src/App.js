import './App.css';
import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import PlayerStats from './PlayerStats';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import axios from 'axios';
import splashArtsData from './splash_arts.json';
import mundoCarLogo from './mundo-car-logo.png'
import searchButton from './search-button.png'
//import { io } from 'socket.io-client';
//import DataStats from './DataStats';

const customSelectStyle = { //default React Select comes with borders + other hard to change components in css
  control: (provided, state) => ({
    ...provided,
    border: 'none',
    backgroundColor: state.isFocused ? '#D3D3D3' : '#F0F8FF', 
    height: 35,
    '&:hover': {
      backgroundColor: '#D3D3D3', 
      boxShadow: '0 0 0 2px rgba(0, 120, 255, 0.5)'
    },
    boxShadow: state.isFocused ? '0 0 0 4px rgba(0, 120, 255, 0.5)' : 'none',
    transition: state.isFocused ? 'box-shadow 0.3s ease' : 'none',
  }),
};

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

const typeOptions = [
  { value: 'Pro', label: 'Pro', },
  { value: 'Reg', label: 'Default'}
]

function App() {
  const navigate = useNavigate();
  //const socket = io('http://127.0.0.1:5000');
  //const socket = io();
  const initialSplashArts = splashArtsData['Dr. Mundo'];
  const initialBackgroundImage = initialSplashArts[0];
  const [backgroundImage, setBackgroundImage] = useState(initialBackgroundImage);
  const [splashArts, setSplashArts] = useState(initialSplashArts);
  const [isPaused, setIsPaused] = useState(true);
  const [summonerName, setSummonerName] = useState('');
  const [tagline, setTagline] = useState('');
  const [role, setRoles] = useState('');
  const [region, setRegion] = useState('');
  const [selectedChampion, setSelectedChampion] = useState({ label: 'Dr. Mundo', value: 'Dr. Mundo' });
  const [type, setType] = useState('');
  const [loading, setLoading] = useState(false);
  //const [progress, setProgress] = useState(0);

  useEffect(() => { //for pre-loading jpgs to avoid loading while they cycle
    splashArts.forEach((image) => {
      const img = new Image();
      img.src = image;
    });
  }, [splashArts]);

  useEffect(() => {
    if (selectedChampion.value && splashArtsData[selectedChampion.value]) {
      setSplashArts(splashArtsData[selectedChampion.value]);
    }
  }, [selectedChampion]);

  useEffect(() => {
    if (!isPaused) {
      const interval = setInterval(() => {
        const randomIndex = Math.floor(Math.random() * splashArts.length); //random splash
        setBackgroundImage(splashArts[randomIndex]); 
      }, 5000); // Change background every 5 seconds

      return () => clearInterval(interval);
    }
  }, [splashArts, isPaused]);

  /* useEffect(() => {
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
  }, [socket]);*/

  const handleToggleChange = () => {
    setIsPaused(!isPaused);
  };

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
  
  const handleTypeChange = (selectedOption) => {
    setType(selectedOption.value)
  }

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
        selectedChampion: selectedChampion.value, 
        type
      });

      if (response.status === 404) {
        alert('One of the fields is invalid. Please check your input.');
        return;
      }

      navigate('/player-stats', {
        state: {
          summonerName,
          tagline,
          role,
          region,
          selectedChampion: selectedChampion.value,
          type, 
          data: response.data // Pass the server response to the next page
        }
      });
      
    } catch (error) {
      if (error.response && error.response.status === 404) {
        alert('Summoner not found. Please check your input.');
      } else {
        console.log(error.response)
        console.log(error.response.data)
        console.error('Error submitting data:', error.response.data['error']);
        alert('Error submitting data, please try again.');
      }
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
    <div className="App">
      <div className="splash-section" style={{ backgroundImage: `url(${backgroundImage})` }}>
        <div className={`top-bar ${loading ? 'loading-active' : ''}`}>
          <div className="logo-container">
            <img src={mundoCarLogo} alt="Mundo Car Logo" className="logo" />
            {/*<span className="logo-text">MUNDO CAR</span> */}
          </div>
          <div className="toggle-container">
            <span className="status-text">{isPaused ? 'Paused' : 'Rotating'}</span>
            <label className="toggle-switch">
              <input type="checkbox" checked={isPaused} onChange={handleToggleChange} />
              <span className="slider"></span>
            </label>
          </div>
        </div>
        <div className="title-container">
          {/*<h1 className="title-text">MUNDO CAR</h1>*/}
        </div>
        <div className="row-inputs">   
          <div className="select-container">
            <Select
              value={roleOptions.find(option => option.value === role)}
              onChange={handleRoleChange}
              options={roleOptions}
              placeholder="Role"
              className="select-input-short"
              styles={customSelectStyle}
            />
          </div>
          <div className="select-container">
            <Select
              value={regionOptions.find(option => option.value === region)}
              onChange={handleRegionChange}
              options={regionOptions}
              placeholder="Region"
              className="select-input"
              styles={customSelectStyle}
            />
          </div>
          <div className="select-container">
            <Select
              value={championNames.find(champion => champion === selectedChampion)}
              onChange={handleChampionChange}
              options={championNames.map(champion => ({ label: champion, value: champion }))}
              isSearchable
              placeholder="Champion"
              filterOption={customFilterOption}
              className="select-input"
              styles={customSelectStyle}
            />
          </div>
          <div className="select-container">
            <Select
              value={typeOptions.find(option => option.value === type)}
              onChange={handleTypeChange}
              options={typeOptions}
              placeholder="Type"
              className="select-input-short"
              styles={customSelectStyle}
            />    
          </div>
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
            <div className="search-button-container" onClick={handleSubmit}>
              <img src={searchButton} alt="Search" className="search-button" />
            </div>
          </div>

        {loading && (
          <div className="loading-container">
            {/*<div className="loading-bar" style={{ width: `${progress}%` }}></div>*/}
          </div>
        )}
      </div>
      <div className="info-section">
        <div className="info-box">
          <h2>What Mundo?</h2>
          <p>This app is designed to compare your data against the very best players in League of Legends.</p>
        </div>
        <div className="info-box">
          <h2>How Mundo?</h2>
          <p>We analyze your gameplay and provide insights based on various in-game statistics.</p>
        </div>
        <div className="info-box">
          <h2>Why Mundo?</h2>
          <p>We aim to help you improve your gameplay and reach your full potential in the game.</p>
        </div>
      </div>
    </div>
  );
}

function RootApp() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/player-stats" element={<PlayerStats />} />
      </Routes>
    </Router>
  );
}

export default RootApp;