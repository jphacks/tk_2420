import { useState, useRef } from 'react';

export interface BoundingBox {
  x: number; // 左上のX座標
  y: number; // 左上のY座標
  width: number;
  height: number;
  label: string;
  color: string;
}

interface AnnotationToolsProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  onExit: () => void;
}

const AnnotationTools: React.FC<AnnotationToolsProps> = ({ videoRef, onExit }) => {
  const [currentBox, setCurrentBox] = useState<BoundingBox | null>(null);
  const [boundingBoxes, setBoundingBoxes] = useState<BoundingBox[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);
  const startPoint = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const startX = e.clientX - rect.left;
      const startY = e.clientY - rect.top;
      startPoint.current = { x: startX, y: startY };
      setCurrentBox({ x: startX, y: startY, width: 0, height: 0, label: '', color: 'red' });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (currentBox && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const currentX = e.clientX - rect.left;
      const currentY = e.clientY - rect.top;

      const newX = Math.min(startPoint.current.x, currentX);
      const newY = Math.min(startPoint.current.y, currentY);
      const newWidth = Math.abs(currentX - startPoint.current.x);
      const newHeight = Math.abs(currentY - startPoint.current.y);

      setCurrentBox({
        ...currentBox,
        x: newX,
        y: newY,
        width: newWidth,
        height: newHeight,
      });
    }
  };

  const handleMouseUp = () => {
    if (currentBox) {
      // ラベル設定のポップアップを表示（簡略化のため、confirm を使用）
      if (window.confirm('Add this bounding box?')) {
        setBoundingBoxes((prevBoxes) => [...prevBoxes, { ...currentBox, label: 'default', color: 'blue' }]);
      }
      setCurrentBox(null);
    }
  };

  return (
    <div
      ref={containerRef}
      className="absolute top-0 left-0 w-full h-full"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      style={{ cursor: 'crosshair' }}
    >
      {/* 現在描画中のボックス */}
      {currentBox && (
        <div
          style={{
            position: 'absolute',
            left: currentBox.x,
            top: currentBox.y,
            width: currentBox.width,
            height: currentBox.height,
            border: `2px dashed ${currentBox.color}`,
          }}
        />
      )}
      {/* 確定済みのボックス */}
      {boundingBoxes.map((box, index) => (
        <div
          key={index}
          style={{
            position: 'absolute',
            left: box.x,
            top: box.y,
            width: box.width,
            height: box.height,
            border: `2px solid ${box.color}`,
          }}
        />
      ))}
      {/* アノテーションモード終了ボタン */}
      <button
        onClick={onExit}
        className="absolute top-4 right-4 px-4 py-2 bg-red-500 text-white rounded"
      >
        Exit Annotation Mode
      </button>
    </div>
  );
};

export default AnnotationTools;