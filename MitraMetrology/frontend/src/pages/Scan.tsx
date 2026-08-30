import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader } from 'lucide-react';
import { ImageUploader } from '../components/ImageUploader';
import { scanAPI } from '../api/client';
import { useScan } from '../contexts/ScanContext';

export const Scan: React.FC = () => {
  const navigate = useNavigate();
  const { setScan, setScanId } = useScan();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentScanId, setCurrentScanId] = useState<string | null>(null);

  const handleImagesSelected = (files: File[]) => {
    setSelectedFiles(files);
    setError(null);
  };

  const handleStartScan = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one image');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Create scan session
      const scanResponse = await scanAPI.createScan();
      setCurrentScanId(scanResponse.scan_id);
      setScanId(scanResponse.scan_id);

      // Upload images
      for (const file of selectedFiles) {
        await scanAPI.uploadImage(scanResponse.scan_id, file);
      }

      // Extract fields
      await scanAPI.extractFields(scanResponse.scan_id);

      // Check compliance
      const complianceResult = await scanAPI.checkCompliance(scanResponse.scan_id);

      // Get detailed results
      const scanDetails = await scanAPI.getScanDetails(scanResponse.scan_id);
      setScan(scanDetails);

      // Navigate to results
      navigate(`/results/${scanResponse.scan_id}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during scanning';
      setError(errorMessage);
      console.error('Scan error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft size={24} className="text-gray-600" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Product Scan</h1>
              <p className="text-sm text-gray-600">Upload packaged commodity images for analysis</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-md p-8 space-y-6">
          {/* Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">📸 Scanning Instructions</h3>
            <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>Ensure good lighting for clear image capture</li>
              <li>Try to capture the front and back of the packaging</li>
              <li>Make sure text on labels is clearly visible</li>
              <li>You can upload up to 5 images per scan</li>
            </ul>
          </div>

          {/* Image Uploader */}
          <ImageUploader
            onImagesSelected={handleImagesSelected}
            isLoading={isLoading}
            maxFiles={5}
          />

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Scan Button */}
          <div className="flex gap-4 justify-end">
            <button
              onClick={() => {
                setSelectedFiles([]);
                setError(null);
              }}
              disabled={isLoading || selectedFiles.length === 0}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
            >
              Clear
            </button>
            <button
              onClick={handleStartScan}
              disabled={isLoading || selectedFiles.length === 0}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {isLoading && <Loader size={18} className="animate-spin" />}
              {isLoading ? 'Scanning...' : `Scan ${selectedFiles.length} Image${selectedFiles.length !== 1 ? 's' : ''}`}
            </button>
          </div>

          {/* Loading State */}
          {isLoading && currentScanId && (
            <div className="mt-8 space-y-3 text-center">
              <Loader size={48} className="animate-spin mx-auto text-blue-600" />
              <p className="text-gray-600">
                Processing images for compliance analysis...
              </p>
              <p className="text-xs text-gray-500">Scan ID: {currentScanId}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Scan;
