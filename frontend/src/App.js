import './App.css';
import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import PlayerStats from './PlayerStats';
import splashArts from './splashArts';
import axios from 'axios';

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
const championNames = [
  'Aatrox', 'Ahri', 'Akali', 'Akshan', 'Alistar', 'Amumu', 'Anivia', 'Annie', 'Aphelios', 'Ashe', 'Aurelion Sol',
  'Azir', 'Bard', 'Bel\'Veth', 'Blitzcrank', 'Brand', 'Braum', 'Briar', 'Caitlyn', 'Camille', 'Cassiopeia', 'Cho\'Gath',
  'Corki', 'Darius', 'Diana', 'Dr. Mundo', 'Draven', 'Ekko', 'Elise', 'Evelynn', 'Ezreal', 'Fiddlesticks',
  'Fiora', 'Fizz', 'Galio', 'Gangplank', 'Garen', 'Gnar', 'Gragas', 'Graves', 'Gwen', 'Hecarim', 'Heimerdinger', 'Hwei',
  'Illaoi', 'Irelia', 'Ivern', 'Janna', 'Jarvan IV', 'Jax', 'Jayce', 'Jhin', 'Jinx', 'K\'Sante', 'Kai\'Sa',
  'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Katarina', 'Kayle', 'Kayn', 'Kennen', 'Kha\'Zix', 'Kindred',
  'Kled', 'Kog\'Maw', 'LeBlanc', 'Lee Sin', 'Leona', 'Lillia', 'Lissandra', 'Lucian', 'Lulu', 'Lux',
  'Malphite', 'Malzahar', 'Maokai', 'Master Yi', 'Milio', 'Miss Fortune', 'Mordekaiser', 'Morgana', 'Naafiri', 'Nami', 'Nasus', 'Nautilus',
  'Neeko', 'Nidalee', 'Nilah', 'Nocturne', 'Nunu & Willump', 'Olaf', 'Orianna', 'Ornn', 'Pantheon', 'Poppy', 'Pyke',
  'Qiyana', 'Quinn', 'Rakan', 'Rammus', 'Rek\'Sai', 'Rell', 'Renata Glasc', 'Renekton', 'Rengar', 'Riven', 'Rumble',
  'Ryze', 'Samira', 'Sejuani', 'Senna', 'Seraphine', 'Sett', 'Shaco', 'Shen', 'Shyvana', 'Singed',
  'Sion', 'Sivir', 'Skarner', 'Smolder', 'Sona', 'Soraka', 'Swain', 'Sylas', 'Syndra', 'Tahm Kench', 'Taliyah',
  'Talon', 'Taric', 'Teemo', 'Thresh', 'Tristana', 'Trundle', 'Tryndamere', 'Twisted Fate', 'Twitch', 'Udyr',
  'Urgot', 'Varus', 'Vayne', 'Veigar', 'Vel\'Koz', 'Vex', 'Vi', 'Viego', 'Viktor', 'Vladimir', 'Volibear',
  'Warwick', 'Wukong', 'Xayah', 'Xerath', 'Xin Zhao', 'Yasuo', 'Yone', 'Yorick', 'Yuumi', 'Zac',
  'Zed', 'Zeri', 'Ziggs', 'Zilean', 'Zoe', 'Zyra'
];

const regionOptions = [
  { value: 'NA', label: 'North America' },
  { value: 'JP', label: 'Japan' },
  { value: 'EUW', label: 'Europe West' },
  { value: 'EUNE', label: 'Europe Nordic & East' },
  { value: 'BR', label: 'Brazil' },
  { value: 'KR', label: 'Korea' }
];

function App() {
  const [backgroundImage, setBackgroundImage] = useState(splashArts[0]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBackgroundImage((prevImage) => {
        const currentIndex = splashArts.indexOf(prevImage);
        const nextIndex = (currentIndex + 1) % splashArts.length;
        return splashArts[nextIndex];
      });
    }, 10000); // Change the background every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const [summonerName, setSummonerName] = useState('');
  const [tagline, setTagline] = useState('');
  const [region, setRegion] = useState('');
  const [selectedChampion, setSelectedChampion] = useState('');

  const handleSummonerNameChange = (event) => {
    setSummonerName(event.target.value);
  };

  const handleTaglineChange = (event) => {
    setTagline(event.target.value);
  };

  const handleRegionChange = (selectedOption) => {
    setRegion(selectedOption.value);
  };

  const handleChampionChange = (selectedOption) => {
    setSelectedChampion(selectedOption);
  };

  
  const handleSubmit = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/get_puuid', {
        summonerName,
        tagline,
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
          filterOption={(option, inputValue) => {
            if (!inputValue) return true;
            const input = inputValue.toLowerCase();
            const label = option.label.toLowerCase();
            return label.includes(input);
          }}
          className="select-input"
        />
        <button onClick={handleSubmit} className="submit-button">Submit</button>
      </div>
    </div>
  );
}

export default App;