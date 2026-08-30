import React from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, AlertCircle, Zap, Shield } from 'lucide-react';

export const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="text-blue-600" size={32} />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  SIH 2026 Compliance Checker
                </h1>
                <p className="text-sm text-gray-600">
                  Legal Metrology Packaged Commodities
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/scan')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              Start Scanning
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            AI-Assisted Compliance Verification
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Scan packaged commodities and get preliminary compliance assessment with legal metrology regulations
          </p>
          <button
            onClick={() => navigate('/scan')}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-lg"
          >
            Begin Scan
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-md p-6">
            <Zap className="text-blue-600 mb-4" size={32} />
            <h3 className="font-bold text-gray-900 mb-2">Fast Analysis</h3>
            <p className="text-gray-600 text-sm">
              Instant OCR and field extraction from product images
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <CheckCircle className="text-green-600 mb-4" size={32} />
            <h3 className="font-bold text-gray-900 mb-2">Comprehensive Check</h3>
            <p className="text-gray-600 text-sm">
              Validates all mandatory and optional compliance fields
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <AlertCircle className="text-yellow-600 mb-4" size={32} />
            <h3 className="font-bold text-gray-900 mb-2">Preliminary Assessment</h3>
            <p className="text-gray-600 text-sm">
              AI-assisted results require human verification
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <Shield className="text-indigo-600 mb-4" size={32} />
            <h3 className="font-bold text-gray-900 mb-2">Rules-Based</h3>
            <p className="text-gray-600 text-sm">
              Based on Legal Metrology Rules 2011 and updates
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-8">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                1
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Upload Image</h4>
              <p className="text-gray-600 text-sm">
                Take a photo or upload an image of the packaged commodity
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                2
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">OCR Analysis</h4>
              <p className="text-gray-600 text-sm">
                System extracts text using advanced computer vision
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                3
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Field Extraction</h4>
              <p className="text-gray-600 text-sm">
                Identifies product name, MRP, manufacturer, and other details
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-lg">
                4
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Compliance Report</h4>
              <p className="text-gray-600 text-sm">
                Get detailed results with human verification required
              </p>
            </div>
          </div>
        </div>

        {/* Important Notice */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded">
          <h4 className="font-bold text-yellow-800 mb-2">⚠️ Important Disclaimer</h4>
          <p className="text-yellow-700 text-sm mb-3">
            This is an <strong>AI-assisted preliminary assessment tool</strong> only.
          </p>
          <ul className="text-yellow-700 text-sm space-y-1 list-disc list-inside">
            <li>Cannot replace human expert verification by legal metrology officers</li>
            <li>All preliminary findings must be verified by authorized personnel</li>
            <li>Based on OCR extraction which may have limitations</li>
            <li>Legal compliance determination requires qualified review</li>
          </ul>
        </div>
      </main>
    </div>
  );
};

export default Landing;
