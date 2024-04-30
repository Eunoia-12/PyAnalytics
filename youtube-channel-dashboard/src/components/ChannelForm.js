import React from 'react';
import '../App.css'

function ChannelForm({ onSubmitChannelId }) {
  return (
    <form class = "channel-form" onSubmit={(e) => {
      e.preventDefault();
      const channelId = e.target.elements.channelId.value;
      onSubmitChannelId(channelId);
    }}>
      <input type="text" name="channelId" placeholder="Enter YouTube Channel ID" required />
      <button type="submit" class = "submit-btn">Get PyAnalytics</button>
    </form>
  );
}

export default ChannelForm;
