import './PlayerStats.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const PlayerStats = () => {
  const [chartDataNormal, setChartDataNormal] = useState(null);
  const [chartDataPro, setChartDataPro] = useState(null);

  useEffect(() => {
    const fetchPlayerStats = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/player-stats');
        if (response.data) {
          generateChartData(response.data.normal, setChartDataNormal);
          generateChartData(response.data.pro, setChartDataPro);
        }
      } catch (error) {
        console.error('Error fetching player stats:', error);
      }
    };

    fetchPlayerStats();
  }, []);

  const generateChartData = (data, setChartData) => {
    // Ensure data is sorted by the custom buckets
    const sortedData = data.sort((a, b) => {
      const order = ['15 and less', '15-20', '20-25', '25-30', '30-35', '35-40', '40 and more'];
      return order.indexOf(a.duration_bucket) - order.indexOf(b.duration_bucket);
    });

    const labels = sortedData.map(item => item.duration_bucket);
    const winRates = sortedData.map(item => item.win_rate);

    setChartData({
      labels: labels,
      datasets: [
        {
          label: 'Win Percentage',
          data: winRates,
          backgroundColor: 'rgba(75,192,192,0.6)',
          borderColor: 'rgba(75,192,192,1)',
          borderWidth: 1,
        },
      ],
    });
  };

  return (
    <div className='duration-charts-container'>
      {chartDataNormal && (
        <div className="chart-container">
          <h2>Normal Player Stats</h2>
          <Bar
            data={chartDataNormal}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: {
                  title: {
                    display: true,
                    text: 'Duration (minutes)',
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: 'Win Percentage (%)',
                  },
                  min: 0,
                  max: 100,
                  ticks: {
                    stepSize: 10,
                  },
                },
              },
            }}
          />
        </div>
      )}
      {chartDataPro && (
        <div className="chart-container">
          <h2>Pro Player Stats</h2>
          <Bar
            data={chartDataPro}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: {
                  title: {
                    display: true,
                    text: 'Duration (minutes)',
                  },
                },
                y: {
                  title: {
                    display: true,
                    text: 'Win Percentage (%)',
                  },
                  min: 0,
                  max: 100,
                  ticks: {
                    stepSize: 10,
                  },
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
