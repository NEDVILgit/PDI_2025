import React, { useState } from 'react';
import ImageUploader from '../ImageUploader';

const ArithmeticControls = ({ onProcess, isProcessing }) => {
    const [operation, setOperation] = useState('add_avg');
    const [secondImage, setSecondImage] = useState(null);

    const handleProcess = () => {
        if (!secondImage) {
            alert("Por favor cargue una segunda imagen para operaciones aritméticas.");
            return;
        }
        const formData = new FormData();
        formData.append('operation', operation);
        formData.append('file2', secondImage); // Main image is file1, handled by parent
        onProcess('arithmetic', formData);
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
                    <option value="add_avg">Suma Promediada</option>
                    <option value="add_clamp">Suma Clampeada</option>
                    <option value="sub_avg">Resta Promediada</option>
                    <option value="sub_clamp">Resta Clampeada</option>
                </select>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Segunda Imagen</label>
                <ImageUploader onUpload={setSecondImage} label={secondImage ? secondImage.name : "Cargar Imagen 2"} />
            </div>

            <button
                onClick={handleProcess}
                disabled={isProcessing || !secondImage}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isProcessing ? 'Procesando...' : 'Aplicar Aritmética'}
            </button>
        </div>
    );
};

export default ArithmeticControls;
