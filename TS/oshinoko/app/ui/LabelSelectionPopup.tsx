'use client';
import { useState } from 'react';
import { LabelInfo } from '@/app/lib/types';


interface LabelSelectionPopupProps {
  label_info: LabelInfo[];
  onConfirm: (label: number) => void;
  onCancel: () => void;
}

const LabelSelectionPopup: React.FC<LabelSelectionPopupProps> = ({ label_info, onConfirm, onCancel }) => {
  const [selectedLabel, setSelectedLabel] = useState<LabelInfo | null>(null);

  return (
    <div className="fixed top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded shadow-md">
        <h3 className="mb-4 text-lg font-bold">Select Label</h3>
        <div className="mb-4">
          {label_info.map((label) => (
            <div key={label.label_id} className="mb-2">
              <label>
                <input
                  type="radio"
                  name="label"
                  value={label.label_name}
                  checked={selectedLabel?.label_id === label.label_id}
                  onChange={() => setSelectedLabel(label)}
                />
                {label.label_name}
              </label>
            </div>
          ))}
        </div>
        <div className="flex justify-end space-x-4">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            onClick={() => selectedLabel && onConfirm(selectedLabel.label_id)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            disabled={!selectedLabel}
          >
            OK
          </button>
        </div>
      </div>
    </div>
  );
};

export default LabelSelectionPopup;

