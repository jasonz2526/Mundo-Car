import './App.css';
import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import PlayerStats from './PlayerStats';
import axios from 'axios';
import splashArtsData from './splash_arts.json';

/*function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>League of Legends Player Stats</h1>
        <PlayerStats />
      </header>
    </div>
  );
}*/
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
  //const [backgroundImage, setBackgroundImage] = useState(splashArts[0]);
  //const [backgroundImage, setBackgroundImage] = useState('');
  //const [splashArts, setSplashArts] = useState([]);
  const evelynnSplashArts = splashArtsData['Evelynn'];
  const initialBackgroundImage = evelynnSplashArts[0];
  const [backgroundImage, setBackgroundImage] = useState(initialBackgroundImage);
  const [splashArts, setSplashArts] = useState(evelynnSplashArts);
  const [summonerName, setSummonerName] = useState('');
  const [tagline, setTagline] = useState('');
  const [role, setRoles] = useState('');
  const [region, setRegion] = useState('');
  const [selectedChampion, setSelectedChampion] = useState({ label: 'Evelynn', value: 'Evelynn' });

  /*useEffect(() => {
    const interval = setInterval(() => {
      setBackgroundImage((prevImage) => {
        //const currentIndex = splashArts.indexOf(prevImage);
        //const nextIndex = (currentIndex + 1) % splashArts.length;
        //return splashArts[nextIndex];
        const randomIndex = Math.floor(Math.random() * splashArts.length);
        return splashArts[randomIndex];
      });
    }, 10000); // Change the background every 10 seconds

    return () => clearInterval(interval);
  }, []);*/

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
    }, 5000); // Change background every 10 seconds

    return () => clearInterval(interval);
  }, [splashArts]);

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

  
  const handleSubmit = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/get_everything', {
        summonerName,
        tagline,
        role,
        region,
        selectedChampion
      });

      if (response.status === 404) {
        alert('One of the fields is invalid. Please check your input.');
        return;
      }

      console.log('Response from server:', response.data);
      
    } catch (error) {
      console.error('Error submitting data:', error);
    }
  };

  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    const input = inputValue.toLowerCase();
    const label = option.label.toLowerCase();
    return label.includes(input);
  };

  return (
    <div className="App" style={{ backgroundImage: `url(${backgroundImage})` }}>
     <div className="top-inputs">
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
        <button onClick={handleSubmit} className="submit-button">Submit</button>
      </div>
    </div>
  );
}

export default App;