import { useState, useRef, useEffect } from "react";
import { LabelInfo, BoundingBox } from "@/app/lib/types";
import { STANDARD_VIDEO_BOX_WIDTH, STANDARD_VIDEO_BOX_HEIGHT } from "@/app/lib/constsnts";
import LabelSelectionPopup from "@/app/ui/LabelSelectionPopup";



interface BoundingBoxDrawerProps {
  labels: LabelInfo[];
  currentBox: BoundingBox | null;
  setCurrentBox: React.Dispatch<React.SetStateAction<BoundingBox | null>>;
  clearCurrentBox: () => void;
  boundingBoxes: BoundingBox[];
  confirmBox: (box: BoundingBox) => void;
}

const BoundingBoxDrawer: React.FC<BoundingBoxDrawerProps> = ({ labels,  
  currentBox, setCurrentBox, clearCurrentBox, boundingBoxes, confirmBox
}) => {

  const [showLabelPopup, setShowLabelPopup] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const startPoint = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const [boxScaleFactor, setBoxScaleFactor] = useState<{ x: number; y: number }>({ x: 1, y: 1 });

  // Update scale factor when the window resizes
  const updateScaleFactor = () => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const videoBoxWidth = STANDARD_VIDEO_BOX_WIDTH
      const videoBoxHeight = STANDARD_VIDEO_BOX_HEIGHT
      setBoxScaleFactor({
        x: rect.width / videoBoxWidth,
        y: rect.height / videoBoxHeight,
      });
    }
  };

  useEffect(() => {
    // Set initial scale factor
    updateScaleFactor();

    // Add resize event listener
    window.addEventListener("resize", updateScaleFactor);

    // Cleanup event listener on unmount
    return () => {
      window.removeEventListener("resize", updateScaleFactor);
    };
  }, []);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const startX = e.clientX - rect.left;
      const startY = e.clientY - rect.top;
      startPoint.current = { x: startX, y: startY };
      setCurrentBox({
        x: startX / boxScaleFactor.x,
        y: startY / boxScaleFactor.y,
        width: 0 / boxScaleFactor.x,
        height: 0 / boxScaleFactor.y,
        color: "white",
      });
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
        x: newX / boxScaleFactor.x,
        y: newY/ boxScaleFactor.y,
        width: newWidth/ boxScaleFactor.x,
        height: newHeight/ boxScaleFactor.y,
      });
    }
  };

  const handleMouseUp = () => {
    console.log('boxScaleFactor', boxScaleFactor);
    if (currentBox) {
      setShowLabelPopup(true);
    }
  };

  const handleLabelConfirm = (selectedLabelId: number) => {
    const labelInfo = labels.find((label) => label.label_id === selectedLabelId);
    console.log('labelInfo', labelInfo);
    if (currentBox && labelInfo) {
      confirmBox({
        ...currentBox,
        label_id: labelInfo.label_id,
        color: labelInfo.label_color,
      });
    }
    console.log(boundingBoxes);
    setShowLabelPopup(false);
  };

  const handleLabelCancel = () => {
    clearCurrentBox();
    setShowLabelPopup(false);
  };


  return (
    <div>
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
              left: currentBox.x * boxScaleFactor.x,
              top: currentBox.y * boxScaleFactor.y,
              width: currentBox.width * boxScaleFactor.x,
              height: currentBox.height * boxScaleFactor.y,
              border: `5px dashed ${currentBox.color}`,
            }}
          />
        )}
        {/* 確定済みのボックス */}
        {boundingBoxes.map((box, index) => (
          <div
            key={index}
            style={{
            position: 'absolute',
              left: box.x * boxScaleFactor.x,
              top: box.y * boxScaleFactor.y,
              width: box.width * boxScaleFactor.x,
              height: box.height * boxScaleFactor.y,
              border: `5px solid ${box.color}`,
            }}
          >
            <span
              className="absolute text-s bg-black text-white p-1"
              style={{ top: '0', left: '0' }}
            >
              {labels.find((label) => label.label_id === box.label_id)?.label_name}
            </span>
          </div>
        ))}
      </div>

      {/* ラベル選択ポップアップ */}
      {showLabelPopup && (
        <LabelSelectionPopup
          label_info={labels}
          onConfirm={handleLabelConfirm}
          onCancel={handleLabelCancel}
        />
      )}
    </div>
  );
};

export default BoundingBoxDrawer;
