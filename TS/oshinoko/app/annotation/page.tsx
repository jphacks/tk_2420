'use client';

import { useState } from 'react';
import Header from '@/app/ui/Header';
import PreviewSnapshots from '@/app/ui/PreviewSnapshots';

import AnnotationStudio from '@/app/ui/AnnotationStudio';
import VideoList from '@/app/ui/VideoList';
import { AnnotatedSnapshot, LabelInfo } from '@/app/lib/types';
import { convertSnapshotToFiles } from '@/app/lib/snapshotUtils';
import { backendUrl } from '@/app/lib/config';
import axios from 'axios';

const dummyLabels: LabelInfo[] = [
    { label_id: 0, label_name: "Person", label_color: "red" },
    { label_id: 1, label_name: "Car", label_color: "green" },
    { label_id: 2, label_name: "Bicycle", label_color: "blue" },
];


const AnnotationPage: React.FC = () => {
    const [isAnnotationMode, setIsAnnotationMode] = useState(false);
    const [annotatedSnapshots, setAnnotatedSnapshots] = useState<AnnotatedSnapshot[]>([]);
    const addAnnotatedSnapshot = (snapshot: AnnotatedSnapshot) => {
        setAnnotatedSnapshots((prev) => [...prev, snapshot]);
    };
    const [labels, setLabels ] = useState<LabelInfo[]>(dummyLabels);

    const uploadAnnotatedSnapshots = async () => {
        if (annotatedSnapshots.length === 0) {
            alert('No snapshots to upload.');
            return;
        }
            try {
                for (const snapshot of annotatedSnapshots) {
                    const { imageFile, annotationFile } = convertSnapshotToFiles(snapshot);

                    // Prepare FormData
                    const formData = new FormData();
                    formData.append('image', imageFile);
                    formData.append('annotation', annotationFile);

                    // Send to backend
                    await axios.post(`${backendUrl}/api/upload_annotation`, formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data',
                        },
                    });
                }
                console.log('All snapshots uploaded successfully.');
                setAnnotatedSnapshots([]);
            } catch (error) {
                console.error('Error uploading snapshots:', error);
                alert("Failed to upload snapshots. Please try again.");
            }
    };

    return (
        <div className="flex flex-col min-h-screen">
            {/* Header */}
            <Header />

            {/* Main Content */}
            <div className="flex flex-1">
                {/* Left Side: Video Player and Annotation Tools */}
                <div className="w-3/4 p-4 flex flex-col space-y-4 relative">
                    <AnnotationStudio addAnnotatedSnapshot={addAnnotatedSnapshot}
                        isAnnotationMode={isAnnotationMode}
                        setIsAnnotationMode={setIsAnnotationMode}
                        labels={labels} />
                </div>

                {/* Right Side: Video List or Snapshot Preview */}
                <div className="w-1/4 p-4 bg-gray-50">
                    {isAnnotationMode || annotatedSnapshots.length !== 0 ? (
                        <>
                            <button
                                onClick={uploadAnnotatedSnapshots}
                                className="mt-4 p-2 bg-blue-600 text-white rounded"
                            >
                                Upload Snapshots
                            </button>

                            <PreviewSnapshots snapshots={annotatedSnapshots} labels={labels} />
                        </>
                    ) : (
                        <VideoList
                            onSelectVideo={() => { return; }}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default AnnotationPage;
