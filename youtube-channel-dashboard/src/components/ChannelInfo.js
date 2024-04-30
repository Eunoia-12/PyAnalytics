// src/components/ChannelInfo.js
import React from 'react';

function ChannelInfo({ channelInfo, analysis, topVideos }) {
  return (

    <div>
      <div class="info-container">
        <div class="card-wrap">
          <div class="info-header">Channel Information</div>
          <div class="content-card">
            <div class="text">Channel Name: {channelInfo.title}</div>
            <div class="text">Subscribers: {channelInfo.subscribers}</div>
            <div class="text">Total Videos: {channelInfo.total_videos}</div>
          </div>
        </div>
        <div class="card-wrap">
          <div class="info-header">Analysis Results</div>
          <div class="content-card">
            <div class="text">Average Views: {analysis.average_views}</div>
            <div class="text">Max Likes: {analysis.max_likes}</div>
            <div class="text">Max Comments: {analysis.max_comments}</div>
          </div>
        </div>
      </div>
      <div class="rank-container">
        <div class="rank-card">
          <div class="rank-header">Top 10 Videos by {channelInfo.title}</div>
          <div>
            {topVideos.map((video, index) => (
              <div key={video.video_id} className="item">
                <h3>{index + 1}. {video.title}</h3>
                <div class="vid-info">
                  <div>Category: {video.category_name}</div>
                  <div class="vl">|</div>
                  <div>Views: {video.views}</div>
                  <div class="vl">|</div>
                  <div>Comments: {video.comments}</div>
                  <div class="vl">|</div>
                  <div>Likes: {video.likes}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>




  );
}

export default ChannelInfo;
