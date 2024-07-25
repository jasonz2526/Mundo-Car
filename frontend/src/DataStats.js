import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const DataStats = () => {
  const location = useLocation();
  const { summonerName, tagline, role, region, selectedChampion, data } = location.state || {};

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      // Simulate loading time if data is already present
      if (data) {
        setStats(data);
        setLoading(false);    
      }
    };

    if (summonerName && tagline && role && region && selectedChampion) {
      fetchData();
    }
  }, [summonerName, tagline, role, region, selectedChampion, data]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!stats) {
    return <div>No data available</div>;
  }

  return (
    <div>
      <h1>Data Stats</h1>
      {/* Render stats here */}
      <pre>{JSON.stringify(stats, null, 2)}</pre>
    </div>
  );
};

export default DataStats;
