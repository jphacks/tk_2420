'use client';

import { useState } from 'react';
import Link from 'next/link';
import EnhancedVideoPlayer from '@/app/ui/EnhancedVideoPlayer';
import Header from '@/app/ui/Header';
import VideoList from '@/app/ui/VideoList';
import VideoUpload from '@/app/ui/VideoUpload';
import ListOshiImages from '@/app/ui/ListOshiImages';
import ModelTraining from '@/app/ui/ModelTraining';
import UpdateOverlay from '@/app/ui/UpdateOverlay';
import { Video } from '@/app/lib/types';
import { backendUrl } from '@/app/lib/config';

const GroupPage = () => {
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const GROUP_NAME = 'illit';
  console.log('selectedVideo:', selectedVideo);
  console.log('originalVideoWidth:', selectedVideo?.original_video_width);
  console.log('originalVideoHeight:', selectedVideo?.original_video_height);
  console.log('backendUrl:', backendUrl);

  return (
    <main className="min-h-screen bg-gray-100">
      <Header />
      <div className="container mx-auto py-10 text-center flex">
        <div className="flex-1 text-left">
          <h1 className="text-4xl font-bold">{GROUP_NAME}</h1>
          <p className="mt-4 text-lg text-gray-700">
            日本の伝統的かつ現代的なミュージカル劇団
          </p>
          <VideoUpload group={GROUP_NAME} />

          {/* Annotate Button */}
          {/* TODO: set currentTime dynamically. */}
          {/* TODO: ボタンじゃなくてSidebarのほうが良い説? */}
          {selectedVideo ? (
            <Link
              href={`/annotation?videoId=${selectedVideo.id}&currentTime=10`}
              className="mt-4 inline-block px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Annotate
            </Link>
          ) : (
            <p className="mt-4 text-red-500">動画を選択してください</p>
          )}

          {/* TODO: model training とupdateOverlayを同時に行ったら壊れる? */}
          {/* Model Training コンポーネント */}
          <ModelTraining groupName={GROUP_NAME} />

          {/* Update Overlay Button */}
          {/* TODO:URLを渡すときに, backendUrlを含めて渡しているのと、含めていないのが混ざっていて気持ち悪い. */}
          {/* TODO: DBを使えば, videoIdだけ渡せば処理は実現できる. */}
          {selectedVideo && (
            <UpdateOverlay
              videoId={selectedVideo.id}
              overlayUrl={selectedVideo.overlay_url}
              videoUrl={selectedVideo.video_url}
              groupName={selectedVideo.group_name}
            />
          )}

          {/* Enhanced Video Player */}
          <div className="mt-8">
            <h2 className="text-2xl font-semibold">
              Watch {GROUP_NAME}’s Latest Video
            </h2>
            {selectedVideo ? (
              <EnhancedVideoPlayer
                src={`${backendUrl}${selectedVideo.video_url}`}
                // TODO: rename overlayConfigUrl to overlayUrl
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
          {/* List Oshi Image*/}
          {selectedVideo && (
            <ListOshiImages
              videoTitle={selectedVideo.title}
              groupName={selectedVideo.group_name}
            />
          )}
        </div>

        {/* Video List on the right */}
        <VideoList onSelectVideo={setSelectedVideo} groupName={GROUP_NAME} />
      </div>
    </main>
  );
};

export default GroupPage;
