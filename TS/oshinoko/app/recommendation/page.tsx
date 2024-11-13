'use client';
import { backendUrl } from '@/app/lib/config';
import { useState } from 'react';
import axios from 'axios';
import Header from '@/app/ui/Header';

const RecommendationPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [celebrityName, setCelebrityName] = useState<string | null>(null);
  const [celebrityPhoto, setCelebrityPhoto] = useState<string | null>(null); // 写真のURLを保持する状態変数

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
      setSelectedFile(file);
    } else {
      alert('Only JPEG and PNG files are allowed.');
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('image', selectedFile);

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
      // レスポンスデータから名前と写真のURLを取得
      setCelebrityName(response.data.idol_name);
      setCelebrityPhoto(response.data.idol_photo_url); // 写真のURLを保存
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload the file. Please try again.');
    }
  };

  return (
    <div>
      <Header />
      <div>Recommendation Page</div>
      <input
        type="file"
        accept="image/jpeg, image/png"
        onChange={handleFileChange}
      />
      <button
        onClick={handleUpload}
        className="bg-blue-500 text-white py-2 px-4 rounded-lg mt-4 hover:bg-blue-600 transition duration-200"
      >
        Upload
      </button>
      {/* 名前と写真が両方存在する場合のみ表示 */}
      {celebrityName && (
        <div>
          <div>Similar Celebrity: {celebrityName}</div>
          {celebrityPhoto && (
            <img
              src={celebrityPhoto}
              alt={`Image of ${celebrityName}`}
              className="w-48 h-auto mt-4"
            />
          )}
        </div>
      )}
    </div>
  );
};

export default RecommendationPage;
