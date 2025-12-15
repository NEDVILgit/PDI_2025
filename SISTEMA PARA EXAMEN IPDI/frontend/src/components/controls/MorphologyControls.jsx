import React, { useState } from 'react';

const MorphologyControls = ({ onProcess, isProcessing }) => {
    const [operation, setOperation] = useState('erosion');
    const [size, setSize] = useState(3);

    const handleProcess = () => {
        const formData = new FormData();
        formData.append('operation', operation);
        formData.append('size', size);
        onProcess('morphology', formData);
    };

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Operación</label>
                <select
                    value={operation}
                    onChange={(e) => setOperation(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                >
                    <option value="erosion">Erosión</option>
                    <option value="dilation">Dilatación</option>
                    <option value="opening">Apertura</option>
                    <option value="closing">Cierre</option>
                    <option value="boundary_external">Borde Exterior</option>
                    <option value="boundary_internal">Borde Interior</option>
                </select>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Tamaño del Kernel</label>
                <div className="flex space-x-4">
                    <label className="flex items-center">
                        <input
                            type="radio"
                            name="size"
                            value="3"
                            checked={size == 3}
                            onChange={(e) => setSize(e.target.value)}
                            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-300">3x3</span>
                    </label>
                    <label className="flex items-center">
                        <input
                            type="radio"
                            name="size"
                            value="5"
                            checked={size == 5}
                            onChange={(e) => setSize(e.target.value)}
                            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-300">5x5</span>
                    </label>
                </div>
            </div>
            <button
                onClick={handleProcess}
                disabled={isProcessing}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isProcessing ? 'Procesando...' : 'Aplicar Morfología'}
            </button>
        </div>
    );
};

export default MorphologyControls;
