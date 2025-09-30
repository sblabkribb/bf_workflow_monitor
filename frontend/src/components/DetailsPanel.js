import React from 'react';
import './DetailsPanel.css';

const DetailItem = ({ label, value }) => {
    if (!value) return null;
    return (
        <div className="detail-item">
            <span className="detail-label">{label}</span>
            <span className="detail-value">{value}</span>
        </div>
    );
};

const DetailsPanel = ({ node, onClose }) => {
    if (!node) return null;

    return (
        <div className="details-panel">
            <button onClick={onClose} className="close-btn">&times;</button>
            <h3>{node.name}</h3>
            <p className="subtitle">{node.group}</p>

            <div className="details-section">
                <h4>Meta</h4>
                <DetailItem label="Status" value={node.status} />
                <DetailItem label="Experimenter" value={node.experimenter} />
                <DetailItem label="Start Date" value={node.start_date} />
                <DetailItem label="End Date" value={node.end_date} />
            </div>

            <div className="details-section">
                <h4>Automation</h4>
                <DetailItem label="Level" value={node.automation_level} />
            </div>

            {node.kpis && node.kpis.length > 0 && (
                <div className="details-section">
                    <h4>KPIs</h4>
                    {node.kpis.map((kpi, index) => (
                        <DetailItem
                            key={index}
                            label={kpi.name}
                            value={`${kpi.value} ${kpi.unit || ''}`}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default DetailsPanel;