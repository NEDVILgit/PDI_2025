import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const HistogramViewer = ({ data }) => {
    if (!data) return null;

    // Data format: { gray: [...], r: [...], g: [...], b: [...] }
    // We need to transform it for Recharts: [{ index: 0, gray: 10, r: 5... }, ...]

    const chartData = [];
    const length = data.gray ? data.gray.length : (data.b ? data.b.length : 0);

    for (let i = 0; i < length; i++) {
        const item = { index: i };
        if (data.gray) item.gray = data.gray[i];
        if (data.r) item.r = data.r[i];
        if (data.g) item.g = data.g[i];
        if (data.b) item.b = data.b[i];
        chartData.push(item);
    }

    return (
        <div className="w-full h-64 bg-gray-800 p-4 rounded-lg border border-gray-700">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <XAxis 
                        dataKey="index" 
                        tick={{ fill: '#9ca3af', fontSize: 10 }} 
                        interval={31} // Show every ~32nd tick (0, 32, 64...)
                    />
                    <YAxis 
                        tick={{ fill: '#9ca3af', fontSize: 10 }} 
                        width={40}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#fff' }}
                        itemStyle={{ fontSize: '12px' }}
                        labelStyle={{ color: '#9ca3af', marginBottom: '5px' }}
                    />
                    {data.gray && <Bar dataKey="gray" fill="#9ca3af" name="Gris" />}
                    {/* Remove stackId to overlay bars for better comparison, use opacity */}
                    {data.r && <Bar dataKey="r" fill="#ef4444" opacity={0.5} name="Rojo" />}
                    {data.g && <Bar dataKey="g" fill="#22c55e" opacity={0.5} name="Verde" />}
                    {data.b && <Bar dataKey="b" fill="#3b82f6" opacity={0.5} name="Azul" />}
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default HistogramViewer;
