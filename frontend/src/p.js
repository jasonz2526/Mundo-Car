import './p.css';
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { Line, Doughnut } from 'react-chartjs-2';
import splashArtsData from './splash_arts.json';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  ArcElement
);

const PlayerStats = () => {
  const [chartData, setChartData] = useState(null);
  const [metric, setMetric] = useState('cs_diff');
  const [gankStats, setGankStats] = useState(null);
  const [overlayVisible, setOverlayVisible] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);
  const location = useLocation();
  const { summonerName, tagline, selectedChampion } = location.state || {};

  const initialSplashArts = splashArtsData[selectedChampion] || [];
  const initialBackgroundImage = initialSplashArts[0]; 
  const [backgroundImage, setBackgroundImage] = useState(initialBackgroundImage);

  useEffect(() => {
    const fetchPlayerStats = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/player-stats', {
          params: {
            summonerName,
            tagline,
            selectedChampion
          }
        });
  
        if (response.data) {
          const { user, pro, stats } = response.data;
          generateChartData({ user, pro }, metric, setChartData);
          setGankStats(stats);
        }
      } catch (error) {
        console.error('Error fetching player stats:', error);
      }
    };
  
    fetchPlayerStats();
  
    const handleScroll = () => {
      setFadeOut(true);
  
      setTimeout(() => {
        setOverlayVisible(false);
        document.body.classList.remove('no-scroll'); // Allow page scrolling once the overlay is gone
      }, 500); 
    };
  
    // Prevent scrolling on the main page while the overlay is active
    if (overlayVisible) {
      document.body.classList.add('no-scroll');
    }
  
    window.addEventListener('scroll', handleScroll);
  
    return () => {
      document.body.classList.remove('no-scroll'); // Cleanup in case the component unmounts
    };
  }, [summonerName, tagline, selectedChampion, metric, overlayVisible]);
  
  

  const generateChartData = (data, metric, setChartData) => {
    const { user, pro } = data;

    const metricMapping = {
      cs_diff: 'CS Difference',
      gold_diff: 'Gold Difference',
      xp_diff: 'XP Difference'
    };

    const metricLabel = metricMapping[metric] || 'Metric';

    const datasets = [
      {
        label: `${metricLabel} (User Wins)`,
        data: user.wins[metric],
        borderColor: 'rgba(75,192,192,1)',
        backgroundColor: 'rgba(75,192,192,0.2)',
        borderWidth: 2,
        fill: false,
      },
      {
        label: `${metricLabel} (User Losses)`,
        data: user.losses[metric],
        borderColor: 'rgba(45,192,192,1)',
        backgroundColor: 'rgba(75,75,192,0.2)',
        borderWidth: 2,
        fill: false,
      },
      {
        label: `${metricLabel} (Pro Wins)`,
        data: pro.wins[metric],
        borderColor: 'rgba(255,99,132,1)',
        backgroundColor: 'rgba(255,99,132,0.2)',
        borderWidth: 2,
        fill: false,
      },
      {
        label: `${metricLabel} (Pro Losses)`,
        data: pro.losses[metric],
        borderColor: 'rgba(225,99,132,1)',
        backgroundColor: 'rgba(255,159,64,0.2)',
        borderWidth: 2,
        fill: false,
      }
    ];

    setChartData({
      labels: user.wins.time,
      datasets: datasets
    });
  };

  const generateDonutChartData = (stats) => {
    if (!stats) return {};
    return {
      labels: ['Top Ganks', 'Mid Ganks', 'Bot Ganks'],
      datasets: [{
        data: [
          stats['Top Lane Ganks Per Game'],
          stats['Mid Lane Ganks Per Game'],
          stats['Bot Lane Ganks Per Game']
        ],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(75, 192, 192, 0.5)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
      }]
    };
  };

  const handleMetricChange = (newMetric) => {
    setMetric(newMetric);
  };

  return (
    <div className='player-stats-page'>
      {overlayVisible && (
        <div
          className={`overlay ${fadeOut ? 'fade-out' : ''}`}
          style={{ backgroundImage: `url(${backgroundImage})` }}
        >
        <div className="gradient-overlay"></div>
          <h1>Thanks For Waiting, {summonerName}</h1>
          <p>Scroll down to see your {selectedChampion} stats</p>
        </div>
      )}

      <div className={`metric-charts-container ${!overlayVisible ? 'slide-up' : ''}`}>
        <div className="button-container">
          <button className='metricButton' onClick={() => handleMetricChange('cs_diff')}>CS Difference</button>
          <button className='metricButton' onClick={() => handleMetricChange('gold_diff')}>Gold Difference</button>
          <button className='metricButton' onClick={() => handleMetricChange('xp_diff')}>XP Difference</button>
        </div>

        {chartData && (
          <div className="chart-container">
            <h2>{metric === 'cs_diff' ? 'CS Difference Between Lane Opponent' : metric === 'gold_diff' ? 'Gold Difference Between Lane Opponent' : 'XP Difference Between Lane Opponent'}</h2>
            <Line
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  x: {
                    title: {
                      display: true,
                      text: 'Time (minutes)',
                    },
                  },
                  y: {
                    title: {
                      display: true,
                      text: 'Difference',
                    },
                    beginAtZero: true,
                  },
                },
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                  },
                },
              }}
            />
          </div>
        )}

        {gankStats && (
          <div className="donut-chart-container">
            <h2>Ganks per Game (Top, Mid, Bot)</h2>
            <Doughnut
              data={generateDonutChartData(gankStats)}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  tooltip: {
                    enabled: false,
                  },
                },
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerStats;
