import './App.css';
import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import PlayerStats from './PlayerStats';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import axios from 'axios';
import splashArtsData from './splash_arts.json';
import mundoCarLogo from './assets/pngs/mundo-car-logo.png'
import searchButton from './assets/pngs/search-button.png'
import loadingGif from './assets/gifs/loading-gif-clear.gif'
import mundoGif from './assets/gifs/mundo.mp4'; 
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

const championNames = [...Object.keys(splashArtsData)];

const regionOptions = [
  { value: 'NA', label: 'North America' },
  { value: 'JP', label: 'Japan' },
  { value: 'EUW', label: 'Europe West' },
  { value: 'EUNE', label: 'Europe Nordic & East' },
  { value: 'BR', label: 'Brazil' },
  { value: 'KR', label: 'Korea' }
];

const roleOptions = [
  { value: 'TOP', label: 'Top' },
  { value: 'JGL', label: 'Jungle' },
  { value: 'MID', label: 'Middle' },
  { value: 'BOT', label: 'Bottom' },
  { value: 'SUP', label: 'Support' },
  { value: 'N/A', label: 'Any' }
]

const typeOptions = [
  { value: 'Reg', label: 'Default'},
  { value: 'Pro', label: 'Pro', }
]

function App() {
  const navigate = useNavigate();
  //const socket = io('http://127.0.0.1:5000');
  //const socket = io();
  //const initialSplashArts = splashArtsData['Dr. Mundo'];
  //const initialBackgroundImage = initialSplashArts[0];
  const initialSplashArts = splashArtsData['Morgana'];
  const initialBackgroundImage = initialSplashArts[10];
  //const initialSplashArts = splashArtsData['Syndra'];
  //const initialBackgroundImage = initialSplashArts[11];
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
  const [activeButton, setActiveButton] = useState('what');

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
      }, 6000); // Change background every x milliseconds

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

  const handleButtonClick = (buttonId) => {
    setActiveButton(buttonId);
  };

  const isDisabled = !summonerName.trim() || !tagline.trim();
  
  const handleSubmit = async (event) => {
    if (!summonerName.trim() || !tagline.trim()) {
      alert('Please fill in both Summoner Name and Tagline.');
    } else {
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

      if (type === 'Pro') {
        alert('Type is Pro, staying on the same page.');
      } else {
        navigate('/player-stats', {
          state: {
            summonerName,
            tagline,
            selectedChampion: selectedChampion.value, 
            data: response.data 
          }
        });
      }
      
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
    } }
  };

  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    const input = inputValue.toLowerCase();
    const label = option.label.toLowerCase();
    return label.startsWith(input); 
  };  

  return (
    <div className="App">
      <div className = "background-container">
        <div className="gradient-overlay"></div>
        <div className="splash-section" style={{ backgroundImage: `url(${backgroundImage})` }}></div>
      </div>
      <div className="top-bar">
          <div className="logo-container">
            <img src={mundoCarLogo} alt="Mundo Car Logo" className="logo" />
          </div>
          <div className="toggle-container">
            <span className="status-text">{isPaused ? 'Paused Slideshow' : 'Enabled Slideshow'}</span>
            <label className="toggle-switch">
              <input id = "checkbox" type="checkbox" checked={isPaused} onChange={handleToggleChange} />
              <span className="slider"></span>
            </label>
          </div>
      </div>
      <div className={`main-content ${loading ? 'loading-active' : ''}`}>
        <div className="title-container">
          <h1 className="title-text">MUNDO CAR</h1>
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
              id="name-input"
            />
            <input
              type="text"
              value={tagline}
              onChange={handleTaglineChange}
              placeholder="Tagline"
              className="tag-input"
              id="tag-input"
            />
            <div 
              className={`search-button-container ${isDisabled ? 'disabled' : ''}`} 
              onClick={isDisabled ? handleSubmit : handleSubmit}
              tabIndex="0"
              role="button"
            >
              <img src={searchButton} alt="Search" className="search-button" />
            </div>
        </div>
      </div>
      {loading && (
        <div className="loading-container">
          <img
            src={loadingGif}
            className="loading-gif"
            alt="League Loading GIF"
            style={{ width: '100%', height: 'auto' }}
          />
        </div>
      )}
      <div className="info-section">
        <div className="info-holder">
          <button
            className={`info-button ${activeButton === 'what' ? 'active' : ''}`}
            onClick={() => handleButtonClick('what')}
          >
            What is Mundo?
          </button>
          <button
            className={`info-button ${activeButton === 'how' ? 'active' : ''}`}
            onClick={() => handleButtonClick('how')}
          >
            How does Mundo?
          </button>
          <button
            className={`info-button ${activeButton === 'why' ? 'active' : ''}`}
            onClick={() => handleButtonClick('why')}
          >
            Why use Mundo?
          </button>
          <button
            className={`info-button ${activeButton === 'mundo' ? 'active' : ''}`}
            onClick={() => handleButtonClick('mundo')}
          >
            Why Mundo Car?
          </button>
        </div>
        {/*<div className="content-container">*/}
          {activeButton === 'what' && ( 
            <div className = "content-container">
              <div className = "content-text"> 
                <h2>Simple, Powerful, and Fun. Like Mundo.</h2>
                <p>Mundo Car is the culmination of stuff that I would've loved coming into League. As one of the hardest games to even get started, with only general tier lists and YouTube guides to work with, personally improving and not going 0-10 every game seemed impossible.</p>
                <p>As such, to make the experience as personalized and informative as possible, Mundo utilizes your in-game stats and compares it to the best in the world to answer two simple questions:</p>
                <p>1. What am I doing wrong?</p>
                <p>2. How can I do better?</p>
              </div>
              <div className = "content-image"> 
                <video className = "mundo-vid"
                  src={mundoGif} 
                  width="100%" 
                  height="auto" 
                  autoPlay 
                  muted 
                  onEnded={(e) => e.target.pause()} 
                />
              </div>
            </div>
          )}
          {activeButton === 'how' && (
            <div className = "content-container">
              
            </div>
          )}
          {activeButton === 'why' && (
            <div className = "content-container">
              <div className = "content-text">
                <h2>For New Players, by Old Ones</h2>
              </div>
            </div>
          )}
          {activeButton === 'mundo' && (
            <div className = "content-container">
              
            </div>
          )}
       {/*</div>*/}
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