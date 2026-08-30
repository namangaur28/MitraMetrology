import { ReactNode, createContext, useState, useContext } from 'react';
import { ScanDetails } from '../api/client';

interface ScanContextType {
  currentScan: ScanDetails | null;
  setScan: (scan: ScanDetails | null) => void;
  currentScanId: string | null;
  setScanId: (id: string | null) => void;
}

const ScanContext = createContext<ScanContextType | undefined>(undefined);

export const ScanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentScan, setCurrentScan] = useState<ScanDetails | null>(null);
  const [currentScanId, setCurrentScanId] = useState<string | null>(null);

  return (
    <ScanContext.Provider
      value={{
        currentScan,
        setScan: setCurrentScan,
        currentScanId,
        setScanId: setCurrentScanId,
      }}
    >
      {children}
    </ScanContext.Provider>
  );
};

export const useScan = (): ScanContextType => {
  const context = useContext(ScanContext);
  if (!context) {
    throw new Error('useScan must be used within a ScanProvider');
  }
  return context;
};
