import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader, Download, Eye } from 'lucide-react';
import { ComplianceResultsCard } from '../components/ComplianceResults';
import { scanAPI, ScanDetails, ExtractedField } from '../api/client';
import { useScan } from '../contexts/ScanContext';

export const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentScan } = useScan();
  const [scanData, setScanData] = useState<ScanDetails | null>(currentScan || null);
  const [selectedImage, setSelectedImage] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(!currentScan);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!currentScan && id) {
      loadScanDetails();
    }
  }, [id, currentScan]);

  const loadScanDetails = async () => {
    if (!id) return;
    
    try {
      setIsLoading(true);
      const data = await scanAPI.getScanDetails(id);
      setScanData(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load scan results';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader size={48} className="animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600">Loading scan results...</p>
        </div>
      </div>
    );
  }

  if (error || !scanData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <ArrowLeft size={20} />
              Back to Home
            </button>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-700">
            <strong>Error:</strong> {error || 'Scan not found'}
          </div>
        </main>
      </div>
    );
  }

  const currentImageData = scanData.images[selectedImage];
  const currentExtractedFields = currentImageData?.extracted_fields || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/scan')}
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
            >
              <ArrowLeft size={20} />
              New Scan
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Compliance Results</h1>
            <div className="w-24"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Compliance Results */}
        {scanData.compliance_result && (
          <ComplianceResultsCard
            checks={scanData.compliance_result.compliance_checks}
            overallStatus={scanData.compliance_result.overall_status}
            summary={scanData.compliance_result.summary}
          />
        )}

        {/* Image and Field Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Image Gallery */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-lg font-bold text-gray-900">Images ({scanData.images.length})</h2>
            <div className="space-y-2">
              {scanData.images.map((image, index) => (
                <button
                  key={image.image_id}
                  onClick={() => setSelectedImage(index)}
                  className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                    selectedImage === index
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <p className="font-medium text-gray-900 truncate">
                    Image {index + 1}
                  </p>
                  <p className="text-xs text-gray-600">
                    {(image.file_size / 1024).toFixed(2)} KB
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Image Viewer and Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Image Display */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="mb-4">
                <div className="flex items-center gap-2 text-gray-600 text-sm">
                  <Eye size={16} />
                  <span>{currentImageData?.filename}</span>
                </div>
              </div>
              <div className="bg-gray-100 rounded-lg overflow-auto max-h-96">
                <img
                  src={`/api/images/${currentImageData?.image_id}`}
                  alt="Scanned product"
                  className="w-full h-auto"
                  onError={(e) => {
                    // Fallback: show placeholder if image can't be loaded
                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23e5e7eb" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="system-ui" font-size="16" fill="%23999"%3EImage not available%3C/text%3E%3C/svg%3E';
                  }}
                />
              </div>
            </div>

            {/* Extracted Fields */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Extracted Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {currentExtractedFields
                  .filter((field) => field.value)
                  .map((field) => (
                    <div key={field.field_name} className="border border-gray-200 rounded-lg p-3">
                      <p className="text-xs font-semibold text-gray-600 uppercase">
                        {field.field_name.replace(/_/g, ' ')}
                      </p>
                      <p className="text-gray-900 font-medium mt-1">{field.value}</p>
                      <div className="mt-2 space-y-1 text-xs text-gray-600">
                        {field.confidence && (
                          <p>
                            Confidence: <span className="font-medium">{(field.confidence * 100).toFixed(0)}%</span>
                          </p>
                        )}
                        <p>
                          Method: <span className="font-medium capitalize">{field.extraction_method}</span>
                        </p>
                      </div>
                    </div>
                  ))}
              </div>

              {currentExtractedFields.filter((f) => f.value).length === 0 && (
                <p className="text-gray-600 text-center py-6">
                  No fields extracted from this image
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Export/Download */}
        <div className="bg-white rounded-lg shadow-md p-6 flex justify-between items-center">
          <div>
            <h3 className="font-semibold text-gray-900">Scan Information</h3>
            <p className="text-sm text-gray-600 mt-1">
              Scan ID: <code className="bg-gray-100 px-2 py-1 rounded">{scanData.scan_id}</code>
            </p>
            <p className="text-sm text-gray-600">
              Date: {new Date(scanData.created_at).toLocaleString()}
            </p>
          </div>
          <button
            onClick={() => {
              const reportText = JSON.stringify(scanData, null, 2);
              const blob = new Blob([reportText], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `scan-${scanData.scan_id}.json`;
              a.click();
            }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            <Download size={18} />
            Export Report
          </button>
        </div>
      </main>
    </div>
  );
};

export default Results;
