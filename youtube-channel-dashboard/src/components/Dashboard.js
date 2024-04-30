import React, { useState } from 'react';
import ChannelForm from './ChannelForm';
import ChannelInfo from './ChannelInfo';
import '../App.css';

function Dashboard() {
  const [channelData, setChannelData] = useState(null);
  const [error, setError] = useState('');

  const handleChannelIdSubmit = async (channelId) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ channel_id: channelId })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
      }

      const data = await response.json();
      setChannelData(data);
      setError('');
    } catch (err) {
      setError('Failed to fetch data. Please check the channel ID and try again.');
      console.error(err);
    }
  };

  return (
    <div>
      <ChannelForm onSubmitChannelId={handleChannelIdSubmit} />
      {error && <p>{error}</p>}
      {channelData && <ChannelInfo channelInfo={channelData.channel_info} analysis={channelData.analysis} topVideos={channelData.top_videos} />}
    </div>
  );
}

export default Dashboard;

