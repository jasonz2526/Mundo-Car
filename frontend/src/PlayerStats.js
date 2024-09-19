import './PlayerStats.css';
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
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
  BarElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  ArcElement,
  BarElement
);

const PlayerStats = () => {
  const [chartData, setChartData] = useState(null);
  const [metric, setMetric] = useState('cs_diff');
  const [gankStats, setGankStats] = useState(null);
  const [proGankStats, setProGankStats] = useState(null);
  const [backgroundImage, setBackgroundImage] = useState('');
  const [scrollY, setScrollY] = useState(0); // Track scroll position
  const location = useLocation();
  const { summonerName, tagline, selectedChampion } = location.state || {};

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
          const { user, pro, stats, pro_stats } = response.data;
          generateChartData({ user, pro }, metric, setChartData);
          setGankStats(stats);
          setProGankStats(pro_stats);
        }
      } catch (error) {
        console.error('Error fetching player stats:', error);
      }
    };

    fetchPlayerStats();
  }, [summonerName, tagline, selectedChampion, metric]);

  useEffect(() => {
    const initialSplashArts = splashArtsData[selectedChampion] || [];
    const initialBackgroundImage = initialSplashArts[0] || '';
    setBackgroundImage(initialBackgroundImage);
  }, [selectedChampion]);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const calculateGradientOpacity = () => {
    const factor = 0.7;
    const maxScroll = (document.body.scrollHeight - window.innerHeight) * 3;
    const opacity = Math.min((scrollY / maxScroll) * factor, factor);
    return `linear-gradient(rgba(0, 0, 0, ${opacity}), rgba(0, 0, 0, ${opacity})`;
  };

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

  const generateDonutChartData = (stats, labelPrefix = '') => {
    if (!stats) return {};
  
    return {
      labels: [`Top Ganks`, `Mid Ganks`, `Bot Ganks`],
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

  const generateBarChartData = (userGankStats, proGankStats) => {
    return {
      labels: ['Top', 'Mid', 'Bot'], 
      datasets: [
        {
          label: 'You', 
          data: [
            parseFloat(userGankStats['Top Lane Ganks Per Game'].toFixed(2)),
            parseFloat(userGankStats['Mid Lane Ganks Per Game'].toFixed(2)),
            parseFloat(userGankStats['Bot Lane Ganks Per Game'].toFixed(2)),
          ],
          backgroundColor: 'rgba(75, 192, 192, 0.5)', 
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
        {
          label: 'Pro',
          data: [
            parseFloat(proGankStats['Top Lane Ganks Per Game'].toFixed(2)),
            parseFloat(proGankStats['Mid Lane Ganks Per Game'].toFixed(2)),
            parseFloat(proGankStats['Bot Lane Ganks Per Game'].toFixed(2)),
          ],
          backgroundColor: 'rgba(255, 99, 132, 0.5)', 
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
        },
      ],
    };
  };

  const handleMetricChange = (newMetric) => {
    setMetric(newMetric);
  };

  const metricLabel = {
    cs_diff: 'CS Difference',
    gold_diff: 'Gold Difference',
    xp_diff: 'XP Difference'
  }[metric] || 'Metric';

  return (
    <div className='player-stats-container'>
      <div className='champion-background-container'>
        {backgroundImage && (
          <div className='background-image' style={{ backgroundImage: `url(${backgroundImage})` }}>
            <div
              className='gradient-overlay'
              style={{ background: calculateGradientOpacity() }}
            />
            <div className='header-text-container' style={{ transform: `translateY(${scrollY * -0.6}px)` }}>
              <h1 className='thanks-text'>
                Thanks For Waiting, {summonerName}
              </h1>
              <p className="scroll-text">
                Scroll down to see your stats on {selectedChampion}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className='metric-charts-container'>
        <div className="button-container">
          <button className='metricButton' onClick={() => handleMetricChange('cs_diff')}>CS Difference</button>
          <button className='metricButton' onClick={() => handleMetricChange('gold_diff')}>Gold Difference</button>
          <button className='metricButton' onClick={() => handleMetricChange('xp_diff')}>XP Difference</button>
        </div>

        {chartData && (
          <div className="chart-container">
            <h2>{metricLabel}</h2>
            <Line
              data={chartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                    labels: {
                      color: 'white',
                    },
                  },
                  tooltip: {
                    callbacks: {
                      label: function (tooltipItem) {
                        return `${tooltipItem.dataset.label}: ${tooltipItem.raw}`;
                      },
                    },
                  },
                },
                scales: {
                  x: {
                    title: {
                      display: true,
                      text: 'Time',
                      color: '#FFFFFF'
                    },
                    ticks: {
                      color: '#FFFFFF', 
                    },
                  },
                  y: {
                    title: {
                      display: true,
                      text: metricLabel,
                      color: '#FFFFFF', 
                    },
                    ticks: {
                      color: '#FFFFFF', 
                    },
                    grid: {
                      color: 'rgba(255, 255, 255, 0.2)',
                    },
                  },
                },
              }}
            />
          </div>
        )}

        {gankStats && proGankStats && (
          <div className="combined-donut-chart-container">
            <h2>Gank Statistics Comparison</h2>
            <div className="donut-chart-container">
              <div className="donut-chart">
                <h3>User Gank Ratio</h3>
                <Doughnut
                  data={generateDonutChartData(gankStats, 'User')}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'top',
                        labels: {
                          color: 'white',
                        }
                      },
                      tooltip: {
                        callbacks: {
                          label: function (tooltipItem) {
                            const dataset = tooltipItem.dataset;
                            const currentValue = dataset.data[tooltipItem.dataIndex];
                            const total = dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = ((currentValue / total) * 100).toFixed(1); 
                
                            return `${tooltipItem.label}: ${percentage}%`;
                          },
                        },
                        backgroundColor: '#333', 
                        titleColor: '#FFD700', 
                        bodyColor: '#FFFFFF', 
                        borderColor: '#4CAF50', 
                        borderWidth: 1
                      },
                    },
                  }}
                />
              </div>
              <div className="donut-chart">
                <h3>Pro Gank Ratio</h3>
                <Doughnut
                  data={generateDonutChartData(proGankStats, 'Pro')}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'top',
                        labels: {
                          color: 'white',
                        }
                      },
                      tooltip: {
                        callbacks: {
                          label: function (tooltipItem) {
                            const dataset = tooltipItem.dataset;
                            const currentValue = dataset.data[tooltipItem.dataIndex];
                            const total = dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = ((currentValue / total) * 100).toFixed(1); 
                
                            return `${tooltipItem.label}: ${percentage}%`;
                          },
                        },
                        backgroundColor: '#333', 
                        titleColor: '#FFD700', 
                        bodyColor: '#FFFFFF', 
                        borderColor: '#4CAF50', 
                        borderWidth: 1
                      },
                    },
                  }}
                />
              </div>
            </div>
            <div className="bar-chart">
              <h3>Gank Frequency Comparison</h3>
              <Bar
                data={generateBarChartData(gankStats, proGankStats)}
                options={{
                  responsive: true,
                  plugins: {
                    legend: { 
                      position: 'top',
                      labels: {
                        color: 'white',
                      }
                    },
                    tooltip: {
                      callbacks: {
                        label: function (tooltipItem) {
                          return `${tooltipItem.dataset.label}: ${tooltipItem.raw}`;
                        },
                      },
                    },
                  },
                  scales: {
                    x: {
                      title: {
                        display: true,
                        text: 'Lanes',
                        color: '#FFFFFF', 
                      },
                      ticks: {
                        color: '#FFFFFF', 
                      },
                    },
                    y: {
                      title: {
                        display: true,
                        text: 'Number of Ganks',
                        color: '#FFFFFF', 
                      },
                      ticks: {
                        color: '#FFFFFF', 
                      },
                      grid: {
                        color: 'rgba(255, 255, 255, 0.2)',
                      },
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerStats;
