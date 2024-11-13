'use client';
import { useState } from 'react';

const VideoUpload = () => {
  const [message, setMessage] = useState<string>('');
  const [videoData, setVideoData] = useState<{
    title: string;
    group_name: string;
    video_url: string;
  } | null>(null);

  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("title", "Sample Title"); // 動画タイトルをここに追加
    formData.append("group_name", "Sample Group"); // グループ名をここに追加
    const fileInput = (event.target as HTMLFormElement).video as HTMLInputElement;
    if (fileInput.files) {
      formData.append("video", fileInput.files[0]);
    } else {
      setMessage("No video file selected.");
      return;
    }

    setMessage("Uploading video...");

    try {
      const response = await fetch("http://localhost:5000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessage("Video uploaded successfully!");
        setVideoData(data);
      } else {
        setMessage("Failed to upload video.");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessage("Error uploading video.");
    }
  };

  return (
    <div className="text-center">
      <form onSubmit={handleUpload}>
        <input 
          type="file" 
          name="video" 
          accept="video/*" 
          required 
          className="block mx-auto my-2"
        />
        <button 
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Upload Video
        </button>
      </form>
      <p>{message}</p>
      {videoData && (
        <div>
          <p>Video Title: {videoData.title}</p>
          <p>Group Name: {videoData.group_name}</p>
          <p>
            <a href={videoData.video_url} target="_blank" rel="noopener noreferrer">
              Watch Video
            </a>
          </p>
        </div>
      )}
    </div>
  );
};

export default VideoUpload;
