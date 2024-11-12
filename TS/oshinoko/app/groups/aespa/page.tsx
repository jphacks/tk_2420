'use client';

import { useState } from 'react';
import Link from 'next/link';
import EnhancedVideoPlayer from '@/app/ui/EnhancedVideoPlayer';
import Header from '@/app/ui/Header';
import VideoList from '@/app/ui/VideoList';
import VideoUpload from '@/app/ui/VideoUpload';
import { Video } from '@/app/lib/types';
import { backendUrl } from '@/app/lib/config';

const AespaPage = () => {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  console.log('selectedVideo:', selectedVideo);
  console.log('originalVideoWidth:', selectedVideo?.original_video_width);
  console.log('originalVideoHeight:', selectedVideo?.original_video_height);
  console.log('backendUrl:', backendUrl);

  return (
    <main className="min-h-screen bg-gray-100">
      <Header />
      <div className="container mx-auto py-10 text-center flex">
        <div className="flex-1 text-left">
          <h1 className="text-4xl font-bold">Aespa</h1>
          <p className="mt-4 text-lg text-gray-700">
            A K-pop girl group from SM Entertainment.
          </p>
          <VideoUpload /> {/* TODO: THIS IS NOT WORKING YET.*/}
          {/* Annotate Button */}
          {/* TODO: set currentTime dynamically. */}
          {/* TODO: ボタンじゃなくてSidebarのほうが良い説? */}
          {selectedVideo ? (
            <Link
              href={`/annotation?videoUrl=${encodeURIComponent(selectedVideo.video_url)}&currentTime=10`}
              className="mt-4 inline-block px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Annotate
            </Link>
          ) : (
            <p className="mt-4 text-red-500">動画を選択してください</p>
          )}
          {/* Enhanced Video Player */}
          <div className="mt-8">
            <h2 className="text-2xl font-semibold">
              Watch Aespa’s Latest Video
            </h2>
            {selectedVideo ? (
              <EnhancedVideoPlayer
                src={`${backendUrl}${selectedVideo.video_url}`}
                overlayConfigUrl={`${backendUrl}${selectedVideo.overlay_url}`}
                originalVideoWidth={selectedVideo.original_video_width}
                originalVideoHeight={selectedVideo.original_video_height}
              />
            ) : (
              <p className="mt-4">Select a video from the list to play.</p>
              // <EnhancedVideoPlayer
              //   src={`${backendUrl}/videos/Supernova.mp4`}
              //   overlayConfigUrl={`${backendUrl}/overlays/Supernova_overlay.json`}
              //   originalVideoWidth={640}
              //   originalVideoHeight={360}
              // />
            )}
          </div>
        </div>

        {/* Video List on the right */}
        <VideoList onSelectVideo={setSelectedVideo} groupName="aespa" />
      </div>
    </main>
  );
};

export default AespaPage;
