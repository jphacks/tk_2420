'use client';
import { backendUrl } from '@/app/lib/config';
import { useState } from 'react';
import axios from 'axios';
import Header from '@/app/ui/Header';

const RecommendationPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [celebrityName, setCelebrityName] = useState<string | null>(null);
  const [celebrityPhoto, setCelebrityPhoto] = useState<string | null>(null);
  const [previewSrc, setPreviewSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
      setSelectedFile(file);
      setPreviewSrc(URL.createObjectURL(file));
    } else {
      alert('Only JPEG and PNG files are allowed.');
      setSelectedFile(null);
      setPreviewSrc(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('image', selectedFile);
    setLoading(true);

    try {
      const response = await axios.post(
        `${backendUrl}/api/upload_kpop_face_match`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        },
      );
      setCelebrityName(response.data.idol_name);
      setCelebrityPhoto(response.data.idol_photo_url);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload the file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="w-full bg-blue-500 text-white py-4 px-6 shadow-md flex justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Oshi no Ko</h1>
          <h2 className="text-lg">K-Pop Celebrity Matcher</h2>
        </div>
      </header>

      <div className="flex flex-col items-center py-10">
        <div className="text-lg text-gray-700 mt-5">Upload a photo to see your K-pop match!</div>

        <div className="mt-6">
          <input
            type="file"
            accept="image/jpeg, image/png"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer px-6 py-2 bg-blue-500 text-white rounded-lg shadow-lg hover:bg-blue-600 transition duration-200"
          >
            Select Photo
          </label>
        </div>

        {previewSrc && (
          <div className="mt-4">
            <img
              src={previewSrc}
              alt="Selected Preview"
              className="w-48 h-48 rounded-lg shadow-md object-cover"
            />
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className={`mt-6 px-6 py-2 rounded-lg text-white shadow-lg ${
            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'
          } transition duration-200`}
        >
          {loading ? 'Uploading...' : 'Find Match'}
        </button>

        {celebrityName && (
          <div className="mt-10 text-center">
            <div className="text-xl font-medium text-gray-800">Your K-Pop Look-alike: {celebrityName}</div>
            {celebrityPhoto && (
              <img
                src={celebrityPhoto}
                alt={`Image of ${celebrityName}`}
                className="w-48 h-48 mt-4 rounded-lg shadow-md object-cover"
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationPage;
