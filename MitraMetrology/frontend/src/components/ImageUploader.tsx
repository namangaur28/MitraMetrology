import React, { useRef, useState } from 'react';
import { Upload, Camera, X, Loader } from 'lucide-react';

interface ImageUploaderProps {
  onImagesSelected: (files: File[]) => void;
  isLoading?: boolean;
  maxFiles?: number;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onImagesSelected,
  isLoading = false,
  maxFiles = 5,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;

    const newFiles = Array.from(files).filter((file) => {
      return file.type.startsWith('image/') && ['image/jpeg', 'image/png'].includes(file.type);
    });

    const totalFiles = selectedFiles.length + newFiles.length;
    if (totalFiles > maxFiles) {
      alert(`Maximum ${maxFiles} images allowed`);
      return;
    }

    const combined = [...selectedFiles, ...newFiles];
    setSelectedFiles(combined);
    onImagesSelected(combined);
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.currentTarget.files);
  };

  const removeFile = (index: number) => {
    const updated = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(updated);
    onImagesSelected(updated);
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
      >
        <div className="space-y-3">
          <Upload className="mx-auto text-gray-400" size={40} />
          <div>
            <p className="text-lg font-medium text-gray-900">
              Drag and drop images here
            </p>
            <p className="text-sm text-gray-600">or click to browse</p>
          </div>
          <p className="text-xs text-gray-500">
            Supported formats: JPG, PNG (max {maxFiles} images)
          </p>

          <div className="flex gap-2 justify-center pt-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <Upload size={18} />
              Select Files
            </button>

            {navigator.mediaDevices?.getUserMedia !== undefined && (
              <button
                onClick={() => cameraInputRef.current?.click()}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                <Camera size={18} />
                Camera
              </button>
            )}
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/jpeg,image/png"
          onChange={handleFileInput}
          disabled={isLoading}
          className="hidden"
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileInput}
          disabled={isLoading}
          className="hidden"
        />
      </div>

      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900">
            Selected Images ({selectedFiles.length}/{maxFiles})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {selectedFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="relative bg-gray-100 rounded-lg overflow-hidden group"
              >
                <img
                  src={URL.createObjectURL(file)}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-32 object-cover"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <button
                    onClick={() => removeFile(index)}
                    disabled={isLoading}
                    className="p-2 bg-red-600 text-white rounded-full hover:bg-red-700"
                  >
                    <X size={18} />
                  </button>
                </div>
                <p className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 truncate">
                  {file.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center gap-2 text-blue-600">
          <Loader size={20} className="animate-spin" />
          <span>Processing images...</span>
        </div>
      )}
    </div>
  );
};
