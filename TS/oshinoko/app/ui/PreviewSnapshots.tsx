import { useEffect, useRef, useState } from 'react';
import { YOLOAnnotation, AnnotatedSnapshot, LabelInfo, BoundingBox } from '@/app/lib/types';
import { generateBoundingBoxesFromYOLO } from '@/app/lib/yoloUtils';

interface PreviewSnapshotsProps {
    snapshots: AnnotatedSnapshot[];
    labels: LabelInfo[];
}

const PreviewSnapshots: React.FC<PreviewSnapshotsProps> = ({ snapshots, labels }) => {
    const imageRef = useRef<HTMLImageElement | null>(null);
    const [imageUrls, setImageUrls] = useState<{ id: string; url: string }[]>([]);
    const [boundingBoxes, setBoundingBoxes] = useState<{ [key: string]: BoundingBox[] }>({});

    useEffect(() => {
        // Generate URLs from Blobs
        const urls = snapshots.map((snapshot) => ({
            id: snapshot.id,
            url: URL.createObjectURL(snapshot.imageBlob),
        }));
        setImageUrls(urls);

        // Clean up Blob URLs when component unmounts
        return () => {
            urls.forEach(({ url }) => URL.revokeObjectURL(url));
        };
    }, [snapshots]);

    useEffect(() => {
        // Update bounding boxes when snapshots or image dimensions change
        const updateBoundingBoxes = () => {
            if (imageRef.current) {
                const { width: imageWidth, height: imageHeight } = imageRef.current;
                const boxes: { [key: string]: BoundingBox[] } = {};

                snapshots.forEach((snapshot) => {
                    boxes[snapshot.id] = generateBoundingBoxesFromYOLO(
                        snapshot.annotations,
                        labels,
                        imageWidth,
                        imageHeight
                    );
                });
                setBoundingBoxes(boxes);
            }
        };

        updateBoundingBoxes();

        // ResizeObserver to watch for image size changes
        const resizeObserver = new ResizeObserver(() => {
            // Use requestAnimationFrame to prevent rapid updates causing vibration
            window.requestAnimationFrame(() => {
                updateBoundingBoxes();
            });
        });

        if (imageRef.current) {
            resizeObserver.observe(imageRef.current);
        }

        return () => {
            if (imageRef.current) {
                resizeObserver.unobserve(imageRef.current);
            }
        };
    }, [snapshots, labels, imageUrls]);

    return (
        <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-2 p-1">
            {imageUrls.map(({ id, url }, index) => (
                <div key={id} className="relative w-full h-full">
                    <img
                        ref={index === 0 ? imageRef : null} // Set ref only on the first image
                        src={url}
                        alt={`snapshot-${id}`}
                        className="w-full h-auto"
                    />
                    {boundingBoxes[id]?.map((box, boxIndex) => (
                        <div
                            key={boxIndex}
                            className="absolute border-2 pointer-events-none"
                            style={{
                                top: `${box.y}px`,
                                left: `${box.x}px`,
                                width: `${box.width}px`,
                                height: `${box.height}px`,
                                borderColor: box.color,
                            }}
                        >
                            <span
                                className="absolute text-xs bg-black text-white p-1"
                                style={{ top: '-0.5rem', left: '0' }}
                            >
                                {labels.find((label) => label.label_id === box.label_id)?.label_name}
                            </span>
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
};

export default PreviewSnapshots;
