'use client';
import { useEffect, useState } from 'react';
import { Video } from '@/app/lib/types';
import { backendUrl } from '@/app/lib/config';

interface VideoListProps {
  onSelectVideo: (video: Video) => void;
  groupName: string;
}

const VideoList: React.FC<VideoListProps> = ({ onSelectVideo, groupName }) => {
  const [videos, setVideos] = useState<Video[]>([]);

  useEffect(() => {
    // Fetch the list of videos for the selected group
    fetch(`${backendUrl}/api/videos?group_name=${groupName}`)
      .then((res) => res.json())
      .then((data) => setVideos(data))
      .catch((error) => console.error('Error fetching videos:', error));
  }, [groupName]);

  return (
    <div className="p-4 border-l border-gray-300">
      <h3 className="text-lg font-semibold mb-4">Available Songs</h3>
      <ul>
        {videos.map((video) => (
          <li
            key={video.id}
            className="cursor-pointer hover:underline mb-2"
            onClick={() => onSelectVideo(video)}
          >
            <p>{video.title}</p>
            {video.thumbnail_url ? (
              <img
                src={video.thumbnail_url}
                alt={`${video.title} thumbnail`}
                className="w-full h-auto mt-2 rounded-md shadow"
              />
            ) : (
              <div className="w-full h-32 bg-gray-300 mt-2 rounded-md flex items-center justify-center">
                <span>No Thumbnail Available</span>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default VideoList;
