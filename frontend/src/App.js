import './App.css';
import React, { useState } from 'react';
import Select from 'react-select';
import PlayerStats from './PlayerStats';

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

function App() {
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

  const handleRegionChange = (event) => {
    setRegion(event.target.value);
  };

  const handleChampionChange = (selectedOption) => {
    setSelectedChampion(selectedOption);
  };

  const handleSubmit = () => {
    console.log(`Summoner Name: ${summonerName}, Tagline: ${tagline}, Region: ${region}, Champion Name: ${selectedChampion}`);
  };

  const customFilterOption = (option, inputValue) => {
    if (!inputValue) return true;
    const input = inputValue.toLowerCase();
    const label = option.label.toLowerCase();
    return label.includes(input);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>League of Legends Player Stats</h1>
        <div className="input-container">
          <label>Summoner Name:</label>
          <input
            type="text"
            value={summonerName}
            onChange={handleSummonerNameChange}
            placeholder="Enter Name"
            className="main-input"
          />
        </div>
        <div className="input-container">
          <label>Tagline:</label>
          <input
            type="text"
            value={tagline}
            onChange={handleTaglineChange}
            placeholder="Enter Tagline"
            className="main-input" 
          />
        </div>
        <div className="input-container">
          <label>Region:</label>
          <input
            type="text"
            value={region}
            onChange={handleRegionChange}
            placeholder="Enter Region"
            className="main-input" 
          />
        </div>
        <div className="input-container">
          <label>Champion:</label>
          <Select
            value={championNames.find(champion => champion === selectedChampion)}
            onChange={handleChampionChange}
            options={championNames.map(champion => ({ label: champion, value: champion }))}
            isSearchable
            placeholder="Select a champion..."
            filterOption={customFilterOption}
            className="champ-input"
          />
        </div>
        <button onClick={handleSubmit}>Submit</button>
      </header>
    </div>
  );
}

export default App;