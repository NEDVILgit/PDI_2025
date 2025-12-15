import React, { useState } from 'react';

const ConvolutionControls = ({ onProcess, isProcessing }) => {
    const [kernel, setKernel] = useState('flat');
    const [size, setSize] = useState(3);
    const [direction, setDirection] = useState('north');

    const handleProcess = () => {
        const formData = new FormData();
        formData.append('kernel', kernel);
        formData.append('size', size);
        if (kernel === 'sobel') {
            formData.append('direction', direction);
        }
        onProcess('convolution', formData);
    };

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Tipo de Kernel</label>
                <select
                    value={kernel}
                    onChange={(e) => setKernel(e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                >
                    <option value="flat">Plano (Promedio)</option>
                    <option value="bartlett">Bartlett</option>
                    <option value="gaussian">Gaussiano</option>
                    <option value="laplacian">Laplaciano</option>
                    <option value="sobel">Sobel</option>
                </select>
            </div>

            {kernel !== 'sobel' && (
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Tamaño del Kernel</label>
                    <div className="flex flex-wrap gap-4">
                        {['3', '5', '7'].map((s) => (
                            <label key={s} className="flex items-center">
                                <input
                                    type="radio"
                                    name="conv_size"
                                    value={s}
                                    checked={size == s}
                                    onChange={(e) => setSize(e.target.value)}
                                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                                />
                                <span className="ml-2 text-sm text-gray-300">{s}x{s}</span>
                            </label>
                        ))}
                        {kernel === 'laplacian' && (
                            <>
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        name="conv_size"
                                        value="4"
                                        checked={size == 4}
                                        onChange={(e) => setSize(e.target.value)}
                                        className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                                    />
                                    <span className="ml-2 text-sm text-gray-300">v4 (3x3)</span>
                                </label>
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        name="conv_size"
                                        value="8"
                                        checked={size == 8}
                                        onChange={(e) => setSize(e.target.value)}
                                        className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 focus:ring-blue-500"
                                    />
                                    <span className="ml-2 text-sm text-gray-300">v8 (3x3)</span>
                                </label>
                            </>
                        )}
                    </div>
                </div>
            )}

            {kernel === 'sobel' && (
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">Dirección</label>
                    <select
                        value={direction}
                        onChange={(e) => setDirection(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5"
                    >
                        <option value="north">Norte</option>
                        <option value="south">Sur</option>
                        <option value="east">Este</option>
                        <option value="west">Oeste</option>
                        <option value="northeast">Noreste</option>
                        <option value="southeast">Sudeste</option>
                        <option value="northwest">Noroeste</option>
                        <option value="southwest">Sudoeste</option>
                    </select>
                </div>
            )}

            <button
                onClick={handleProcess}
                disabled={isProcessing}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isProcessing ? 'Procesando...' : 'Aplicar Convolución'}
            </button>
        </div>
    );
};

export default ConvolutionControls;
