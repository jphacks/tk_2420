'use client';
import { useState } from 'react';
import { Video } from '@/app/lib/types';
import axios from 'axios';
import { backendUrl, videoUrlPrefix } from '@/app/lib/config';
import EnhancedVideoPlayer from '@/app/ui/EnhancedVideoPlayer';

interface VideoUploadFromYoutubeProps {
  group: string;
}

const VideoUploadFromYoutube: React.FC<VideoUploadFromYoutubeProps> = ({
  group,
}) => {
  const [message, setMessage] = useState<string>('');
  const [videoData, setVideoData] = useState<Video | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState<string>('');

  const handleYoutubeUpload = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!youtubeUrl.trim()) {
      setMessage('Please enter a YouTube URL.');
      return;
    }

    setMessage('Processing YouTube video, please wait...');

    try {
      // Send YouTube URL to the backend for processing
      const response = await axios.post<Video>(
        `${backendUrl}/${videoUrlPrefix}/upload/youtube`,
        {
          youtubeUrl,
          title: 'YouTube Video',
          group_name: group,
        },
      );

      setMessage('YouTube video processed successfully!');
      setVideoData(response.data);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        setMessage(
          `Failed to process the YouTube video. Error: ${error.response.status}`,
        );
      } else {
        setMessage('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="text-center">
      {/* YouTube URL Upload Form */}
      <form onSubmit={handleYoutubeUpload} className="mb-4">
        <input
          type="url"
          placeholder="Enter YouTube URL"
          value={youtubeUrl}
          onChange={(e) => setYoutubeUrl(e.target.value)}
          required
          className="block mx-auto my-2 px-4 py-2 border rounded"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Process YouTube Video
        </button>
      </form>
      <p
        className={`mt-4 ${
          message.includes('successfully') ? 'text-green-500' : 'text-red-500'
        }`}
      >
        {message}
      </p>
      {videoData ? (
        <EnhancedVideoPlayer
          src={`${backendUrl}${videoData.video_url}`}
          overlayConfigUrl={`${backendUrl}${videoData.overlay_url}`}
          originalVideoWidth={videoData.original_video_width}
          originalVideoHeight={videoData.original_video_height}
        />
      ) : (
        <p className="mt-4">Enter a YouTube URL to process a video.</p>
      )}
    </div>
  );
};

export default VideoUploadFromYoutube;
