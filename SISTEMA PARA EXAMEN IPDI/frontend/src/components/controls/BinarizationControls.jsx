import React, { useState } from 'react';

const BinarizationControls = ({ onProcess, isProcessing }) => {
    const [threshold, setThreshold] = useState(128);
    const [invert, setInvert] = useState(false);

    const handleProcess = () => {
        const formData = new FormData();
        formData.append('threshold', threshold);
        formData.append('invert', invert);
        onProcess('binarize', formData);
    };

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Umbral ({threshold})</label>
                <input
                    type="range"
                    min="0"
                    max="255"
                    value={threshold}
                    onChange={(e) => setThreshold(e.target.value)}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
            </div>
            <div className="flex items-center">
                <input
                    type="checkbox"
                    id="invert"
                    checked={invert}
                    onChange={(e) => setInvert(e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-600"
                />
                <label htmlFor="invert" className="ml-2 text-sm font-medium text-gray-300">Invertir Colores</label>
            </div>
            <button
                onClick={handleProcess}
                disabled={isProcessing}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isProcessing ? 'Procesando...' : 'Aplicar Binarización'}
            </button>
        </div>
    );
};

export default BinarizationControls;
