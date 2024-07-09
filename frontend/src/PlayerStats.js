import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const PlayerStats = () => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const fetchPlayerStats = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/player-stats');
        console.log('Response data:', response.data);
        if (Array.isArray(response.data)) {
          generateChartData(response.data);
        } else {
          console.error('Expected an array but got:', response.data);
        }
      } catch (error) {
        console.error('Error fetching player stats:', error);
      }
    };

    fetchPlayerStats();
  }, []);

  const generateChartData = (data) => {
    const chartPoints = data.map((item) => ({
      x: item.Duration,
      y: item.win_rate,
      r: item.radius,
    }));

    setChartData({
      datasets: [
        {
          label: 'Win Percentage vs. Duration',
          data: chartPoints,
          backgroundColor: 'rgba(75,192,192,0.6)',
          borderColor: 'rgba(75,192,192,1)',
        },
      ],
    });
  };

  return (
    <div style={{ width: '80vw', height: '80vh' }}>
      {chartData ? (
        <Scatter
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
              },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    return `Duration: ${context.raw.x} mins, Win Rate: ${context.raw.y.toFixed(
                      2
                    )}%, Matches: ${Math.round(context.raw.r / 2) ** 2}`;
                  },
                },
              },
            },
            scales: {
              x: {
                type: 'linear',
                position: 'bottom',
                title: {
                  display: true,
                  text: 'Duration (minutes)',
                },
                min: 0,
                max: 60,
                ticks: {
                  autoSkip: false
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
                  autoSkip: false,
                  stepSize: 10,
                },
              },
            },
          }}
        />
      ) : (
        <p>Loading chart...</p>
      )}
    </div>
  );
};

export default PlayerStats;
