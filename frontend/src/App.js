import './App.css';
import React, { useState, useEffect } from 'react';
import WorkflowGraph from './components/WorkflowGraph';
import DetailsPanel from './components/DetailsPanel';
import GanttChart from './components/GanttChart';

function App() {
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeView, setActiveView] = useState('network'); // 'network' or 'timeline'

  useEffect(() => {
    // Flask API 서버에서 데이터 가져오기
    fetch('http://127.0.0.1:5001/api/experiments')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok. Flask 서버가 실행 중인지 확인하세요.');
        }
        return response.json();
      })
      .then(data => {
        setExperiments(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  }, []); // 컴포넌트가 처음 마운트될 때 한 번만 실행

  const handleNodeClick = (node) => {
    setSelectedNode(node);
  };

  const handleClosePanel = () => {
    setSelectedNode(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>BF Workflow Monitor</h1>
        <p>React & D3.js Visualization</p>
      </header>
      <div className="view-selector">
        <button
          className={`view-tab ${activeView === 'network' ? 'active' : ''}`}
          onClick={() => setActiveView('network')}
        >
          네트워크 뷰
        </button>
        <button
          className={`view-tab ${activeView === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveView('timeline')}
        >
          타임라인 뷰
        </button>
      </div>
      <div className="App-body">
        <main className={`App-main ${selectedNode ? 'panel-open' : ''}`}>
        {loading && <div className="message">Loading data...</div>}
        {error && <div className="message error">Error: {error}</div>}
        {!loading && !error && (activeView === 'network' ? (
            <WorkflowGraph experiments={experiments} onNodeClick={handleNodeClick} selectedNodeId={selectedNode?.id} />) : (<GanttChart experiments={experiments} />)
          )}
      </main>
        {selectedNode && <DetailsPanel node={selectedNode} onClose={handleClosePanel} />}
      </div>
    </div>
  );
}

export default App;
