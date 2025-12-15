import React, { useState } from 'react';

const LuminanceControls = ({ onProcess, isProcessing }) => {
    const [operation, setOperation] = useState('sqrt');
    const [ymin, setYmin] = useState(0);
    const [ymax, setYmax] = useState(255);

    const handleProcess = () => {
        const formData = new FormData();
        formData.append('operation', operation);
        if (operation === 'linear') {
            // Construct points from Ymin and Ymax: [[0, ymin], [255, ymax]]
            const points = JSON.stringify([[0, parseInt(ymin)], [255, parseInt(ymax)]]);
            formData.append('points', points);
        }
        onProcess('luminance', formData);
    };

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Tipo de Transformación</label>
                <select
                    value={operation}
                    onChange={(e) => setOperation(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                >
                    <option value="sqrt">Raíz Cuadrada</option>
                    <option value="square">Cuadrado</option>
                    <option value="linear">Lineal a Trozos</option>
                </select>
            </div>

            {operation === 'linear' && (
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">Ymin</label>
                        <input
                            type="number"
                            min="0"
                            max="255"
                            value={ymin}
                            onChange={(e) => setYmin(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">Ymax</label>
                        <input
                            type="number"
                            min="0"
                            max="255"
                            value={ymax}
                            onChange={(e) => setYmax(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                        />
                    </div>
                </div>
            )}

            <button
                onClick={handleProcess}
                disabled={isProcessing}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isProcessing ? 'Procesando...' : 'Aplicar Transformación'}
            </button>
        </div>
    );
};

export default LuminanceControls;
