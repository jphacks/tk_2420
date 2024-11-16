'use client';
import { useState } from 'react';
import { Video } from '@/app/lib/types';
import axios from 'axios';
import { backendUrl, videoUrlPrefix } from '@/app/lib/config';
import EnhancedVideoPlayer from '@/app/ui/EnhancedVideoPlayer';

const VideoUploadByYoutube = () => {
  const [message, setMessage] = useState<string>('');
  const [videoData, setVideoData] = useState<Video | null>(null);

  const [youtubeUrl, setYoutubeUrl] = useState<string>('');
  const [isYouTubeDownload, setIsYouTubeDownload] = useState<boolean>(false);
  const [mp4Path, setMp4Path] = useState<string | null>(null);

  // YouTubeからMP4に変換する処理
  const handleYouTubeDownload = async () => {
    if (!youtubeUrl) {
      setMessage('YouTube URL is required.');
      return;
    }

    setMessage('Downloading video from YouTube, please wait...');
    try {
      // ここで/uploads/videoにmp4が入る
      const response = await axios.post(
        `${backendUrl}/${videoUrlPrefix}/upload/youtube`,
        { youtubeUrl },
      );

      const downloadedMp4Path = response.data.mp4Path;
      setMp4Path(downloadedMp4Path); // MP4ファイルパスを保存
      setMessage('YouTube video processed successfully! Ready for upload.');
      console.log(`downloadedMp4Path: ${downloadedMp4Path}`)
    } catch (error) {
      setMessage('Failed to download and process YouTube video.');
      console.error(error);
    }
  };

  // YouTubeからダウンロードしたMP4をappで処理
  // この関数がうまく動いていない VideoUpload.tsxと同じように処理したい
  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('title', 'Sample Video'); 
    formData.append('group_name', 'aespa'); 

    if (isYouTubeDownload && mp4Path) {
      try {
        // YouTube動画をBlobとして取得
        const videoResponse = await axios.get(mp4Path, { responseType: 'blob' });
        const videoFile = new File([videoResponse.data], 'youtube_video.mp4', {
          type: 'video/mp4',
        });
        console.log(`videoFile: ${videoFile}`)
        formData.append('video', videoFile); // FormDataに追加
      } catch (error) {
        setMessage('Failed to load the downloaded YouTube video.');
        console.error(error);
        return;
      }
    } else {
      setMessage('Please download a YouTube video first.');
      return;
    }

    setMessage('Uploading video, please wait...');

    try {
      // Send file to the backend for processing
      const response = await axios.post(
        `${backendUrl}/${videoUrlPrefix}/upload/mp4`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        },
      );
      console.log(`response: ${response}`);

      setMessage('Video processed successfully!');
      setVideoData(response.data);
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        setMessage(
          `Failed to upload the video. Error: ${error.response.status}`,
        );
      } else {
        setMessage('An error occurred. Please try again.');
      }
    }
  };


  // この部分も複雑になりすぎている
  return (
    <div className="text-center">
      <form className="mb-4">
        <label className="block mb-2 font-medium">YouTube URL (Optional)</label>
        <input
          type="text"
          value={youtubeUrl}
          onChange={(e) => setYoutubeUrl(e.target.value)}
          className="w-full p-2 mb-4 border rounded"
          placeholder="Enter YouTube URL if you want to download"
        />
        <div className="mb-4">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={isYouTubeDownload}
              onChange={() => {
                setIsYouTubeDownload(!isYouTubeDownload);
                setMp4Path(null); 
              }}
              className="mr-2"
            />
            Download from YouTube
          </label>
          {isYouTubeDownload && (
            <button
              type="button"
              onClick={handleYouTubeDownload}
              className="bg-blue-500 text-white px-4 py-2 rounded ml-4"
            >
              Download from YouTube
            </button>
          )}
        </div>
      </form>
      <button
        type="button"
        onClick={handleUpload}
        className="bg-green-500 text-white px-4 py-2 rounded"
      >
        Upload Converted MP4
      </button>
      <p>{message}</p>
      {videoData && (
        <EnhancedVideoPlayer
          src={`${backendUrl}${videoData.video_url}`}
          overlayConfigUrl={`${backendUrl}${videoData.overlay_url}`}
          originalVideoWidth={videoData.original_video_width}
          originalVideoHeight={videoData.original_video_height}
        />
      )}
    </div>
  );
};

export default VideoUploadByYoutube;
