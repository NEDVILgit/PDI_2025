import React, { useState } from 'react';

const ChromaticControls = ({ onProcess, isProcessing }) => {
    const [operation, setOperation] = useState('rgb_to_yiq');
    const [channel, setChannel] = useState(0);

    const handleProcess = () => {
        const formData = new FormData();
        formData.append('operation', operation);
        if (operation === 'channel') {
            formData.append('channel', channel);
        }
        onProcess('chromatic', formData);
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
                    <option value="rgb_to_yiq">RGB a YIQ</option>
                    <option value="yiq_to_rgb">YIQ a RGB</option>
                    <option value="avg">Promediar 3 Canales</option>
                    <option value="channel">Extraer Canal</option>
                </select>
            </div>

            {operation === 'channel' && (
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Canal</label>
                    <div className="flex space-x-4">
                        <label className="flex items-center">
                            <input
                                type="radio"
                                name="channel"
                                value="0"
                                checked={channel == 0}
                                onChange={(e) => setChannel(e.target.value)}
                                className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                            />
                            <span className="ml-2 text-sm text-gray-300">Canal 1 (B)</span>
                        </label>
                        <label className="flex items-center">
                            <input
                                type="radio"
                                name="channel"
                                value="1"
                                checked={channel == 1}
                                onChange={(e) => setChannel(e.target.value)}
                                className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                            />
                            <span className="ml-2 text-sm text-gray-300">Canal 2 (G)</span>
                        </label>
                        <label className="flex items-center">
                            <input
                                type="radio"
                                name="channel"
                                value="2"
                                checked={channel == 2}
                                onChange={(e) => setChannel(e.target.value)}
                                className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                            />
                            <span className="ml-2 text-sm text-gray-300">Canal 3 (R)</span>
                        </label>
                    </div>
                </div>
            )}

            <button
                onClick={handleProcess}
                disabled={isProcessing}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isProcessing ? 'Procesando...' : 'Aplicar Operación'}
            </button>
        </div>
    );
};

export default ChromaticControls;
