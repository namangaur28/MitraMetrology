import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ScanResponse {
  scan_id: string;
  created_at: string;
  images: any[];
  compliance_result: any | null;
}

export interface UploadResponse {
  scan_id: string;
  image_id: string;
  message: string;
}

export interface ComplianceResult {
  result_id: string;
  scan_id: string;
  rules_version: string;
  compliance_checks: ComplianceCheck[];
  overall_status: string;
  summary: string;
  disclaimer: string;
}

export interface ComplianceCheck {
  rule_id: string;
  field: string;
  name: string;
  status: string;
  details: string;
  confidence?: number;
}

export interface ExtractedField {
  field_name: string;
  value: string | null;
  confidence: number;
  source_text: string;
  bbox: number[] | null;
  extraction_method: string;
}

export interface ScanDetails {
  scan_id: string;
  created_at: string;
  images: ImageDetail[];
  compliance_result: ComplianceResult | null;
}

export interface ImageDetail {
  image_id: string;
  filename: string;
  file_size: number;
  width: number;
  height: number;
  ocr_results: OCRResult[];
  extracted_fields: ExtractedField[];
}

export interface OCRResult {
  text_blocks: TextBlock[];
  raw_text: string;
  confidence_avg: number;
}

export interface TextBlock {
  text: string;
  confidence: number;
  bbox: number[];
}

// API Functions
export const scanAPI = {
  // Create a new scan session
  createScan: async (): Promise<ScanResponse> => {
    const response = await api.post('/scan');
    return response.data;
  },

  // Upload image to a scan
  uploadImage: async (scanId: string, file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/upload?scan_id=${scanId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Extract fields from all images in a scan
  extractFields: async (scanId: string): Promise<any> => {
    const response = await api.post(`/extract?scan_id=${scanId}`);
    return response.data;
  },

  // Check compliance for a scan
  checkCompliance: async (scanId: string): Promise<ComplianceResult> => {
    const response = await api.post(`/compliance/check?scan_id=${scanId}`);
    return response.data;
  },

  // Get detailed scan results
  getScanDetails: async (scanId: string): Promise<ScanDetails> => {
    const response = await api.get(`/scan/${scanId}`);
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
