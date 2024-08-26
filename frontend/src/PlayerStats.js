import './PlayerStats.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  Title,
  Tooltip,
  Legend,
  PointElement
);

const PlayerStats = () => {
  const [chartData, setChartData] = useState(null);
  const [metric, setMetric] = useState('cs_diff');

  useEffect(() => {
    const fetchPlayerStats = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/player-stats');
        if (response.data) {
          generateChartData(response.data, metric, setChartData);
        }
      } catch (error) {
        console.error('Error fetching player stats:', error);
      }
    };

    fetchPlayerStats();
  }, [metric]);

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

  const handleMetricChange = (newMetric) => {
    setMetric(newMetric);
  };

  return (
    <div className='metric-charts-container'>
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
    </div>
  );
};

export default PlayerStats;
