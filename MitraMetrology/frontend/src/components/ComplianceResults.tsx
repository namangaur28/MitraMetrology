import React from 'react';
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';
import { ComplianceCheck } from '../api/client';

interface ComplianceStatusProps {
  status: string;
}

export const ComplianceStatusBadge: React.FC<ComplianceStatusProps> = ({ status }) => {
  switch (status) {
    case 'pass':
      return (
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-100">
          <CheckCircle size={16} className="text-green-600" />
          <span className="text-sm text-green-700 font-medium">Detected</span>
        </div>
      );
    case 'flag':
      return (
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-100">
          <AlertCircle size={16} className="text-red-600" />
          <span className="text-sm text-red-700 font-medium">Missing</span>
        </div>
      );
    case 'needs_review':
      return (
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-yellow-100">
          <AlertTriangle size={16} className="text-yellow-600" />
          <span className="text-sm text-yellow-700 font-medium">Needs Review</span>
        </div>
      );
    default:
      return null;
  }
};

interface ComplianceResultsCardProps {
  checks: ComplianceCheck[];
  overallStatus: string;
  summary: string;
}

export const ComplianceResultsCard: React.FC<ComplianceResultsCardProps> = ({
  checks,
  overallStatus,
  summary,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      <div className="space-y-3">
        <h2 className="text-2xl font-bold text-gray-900">Compliance Overview</h2>
        <div className="flex items-center gap-3">
          {overallStatus === 'pass' && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-50 border border-green-200">
              <CheckCircle size={24} className="text-green-600" />
              <span className="text-lg font-semibold text-green-700">Preliminary Pass</span>
            </div>
          )}
          {overallStatus === 'flag' && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-50 border border-red-200">
              <AlertCircle size={24} className="text-red-600" />
              <span className="text-lg font-semibold text-red-700">Issues Detected</span>
            </div>
          )}
          {overallStatus === 'needs_review' && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-yellow-50 border border-yellow-200">
              <AlertTriangle size={24} className="text-yellow-600" />
              <span className="text-lg font-semibold text-yellow-700">Needs Review</span>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <p className="text-sm text-gray-700 whitespace-pre-line">{summary}</p>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900">Field Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {checks.map((check) => (
            <div key={check.rule_id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{check.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{check.details}</p>
                  {check.confidence !== undefined && (
                    <p className="text-xs text-gray-500 mt-2">
                      Confidence: {(check.confidence * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
                <ComplianceStatusBadge status={check.status} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>⚠️ Important Disclaimer:</strong> This is an AI-assisted preliminary assessment only. 
          This system cannot replace human expert verification by legal metrology officers. 
          All preliminary findings must be verified by authorized enforcement personnel.
        </p>
      </div>
    </div>
  );
};
