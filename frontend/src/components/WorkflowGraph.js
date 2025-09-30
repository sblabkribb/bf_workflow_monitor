import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { forceCluster } from 'd3-force-cluster';

const WorkflowGraph = ({ experiments, onNodeClick, selectedNodeId }) => {
    const svgRef = useRef();

    useEffect(() => {
        if (!experiments || experiments.length === 0) return;

        // 1. 데이터 변환: D3가 이해할 수 있는 nodes와 links로 가공
        const nodes = [];
        const links = [];
        
        // 모든 실험 데이터를 순회
        experiments.forEach(experiment => {
            let lastNodeOfPrevWorkflow = null;
            const experimentGroupId = experiment.folder_name;

            experiment.workflows.forEach((workflow, wf_idx) => {
            let lastNodeInCurrentWorkflow = null;
            if (workflow.unit_operations.length > 0) {
                workflow.unit_operations.forEach((uo, index) => {
                    // 고유 ID 생성: experiment-workflow-uo
                    const nodeId = `${experiment.folder_name}_${workflow.file_name}_${uo.id}_${index}`;
                    const node = {
                        id: nodeId,
                        name: uo.name,
                        // 상세 패널에 필요한 모든 정보 전달
                        ...uo,
                        group: experiment.title, // 실험 제목을 그룹으로 사용
                    };
                    nodes.push(node);

                    // 같은 워크플로우 내의 UO들을 연결
                    if (lastNodeInCurrentWorkflow) {
                        links.push({ source: lastNodeInCurrentWorkflow.id, target: node.id });
                    }
                    lastNodeInCurrentWorkflow = node;
                });

                // 다른 워크플로우와 연결
                const firstNodeOfCurrentWorkflow = nodes[nodes.length - workflow.unit_operations.length];
                if (lastNodeOfPrevWorkflow && firstNodeOfCurrentWorkflow) {
                    links.push({ 
                        source: lastNodeOfPrevWorkflow.id, 
                        target: firstNodeOfCurrentWorkflow.id,
                        type: 'inter-workflow'
                    });
                }
                lastNodeOfPrevWorkflow = lastNodeInCurrentWorkflow;

            } else {
                // UO가 없는 워크플로우는 워크플로우 자체를 노드로 표현
                const nodeId = `${experiment.folder_name}_${workflow.file_name}`;
                const node = {
                    id: nodeId,
                    name: workflow.title,
                    group: experiment.title,
                    status: workflow.status,
                };
                nodes.push(node);
                if (lastNodeOfPrevWorkflow) {
                    links.push({ source: lastNodeOfPrevWorkflow.id, target: node.id });
                }
                lastNodeOfPrevWorkflow = node;
            }
        });
        });

        // 2. D3.js 설정
        const width = 1200;
        const height = 800;

        const svg = d3.select(svgRef.current)
            .attr('width', width)
            .attr('height', height)
            .html(''); // 이전 렌더링 내용 삭제

        // 화살표 마커 정의
        svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 23) // 노드 반지름(8) + 화살표 크기
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 10)
            .attr('markerHeight', 10)
            .attr('xoverflow', 'visible')
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', '#999')
            .style('stroke', 'none');

        // 색상 스케일
        const groupColor = d3.scaleOrdinal(d3.schemeCategory10);
        const statusColor = d3.scaleOrdinal()
            .domain(["Completed", "In Progress", "Planned"])
            .range(["#28a745", "#007bff", "#e0e0e0"]);

        // Force Simulation 설정
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(d => d.type === 'inter-workflow' ? 150 : 80))
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(width / 2, height / 2).strength(0.1))
            // 그룹별로 묶이도록 force 추가
            .force("group", forceCluster().centers(d => {
                const groupIndex = Array.from(new Set(nodes.map(n => n.group))).indexOf(d.group);
                const numGroups = Array.from(new Set(nodes.map(n => n.group))).length;
                return { x: (width / (numGroups + 1)) * (groupIndex + 1), y: height / 2 };
            }).strength(0.05))
            .force("x", d3.forceX())
            .force("y", d3.forceY());

        // 링크(선) 그리기
        const link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke-width", 1.5)
            .attr('marker-end', 'url(#arrowhead)');

        // 노드(원) 그리기
        const node = svg.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", 15)
            .attr("fill", d => groupColor(d.group))
            .attr("stroke", d => statusColor(d.status))
            .attr("stroke-width", 4)
            .style("cursor", "pointer")
            .on("click", (event, d) => {
                onNodeClick(d);
            })
            .call(drag(simulation)); // 드래그 기능 추가

        // 노드에 마우스 올리면 툴팁 표시
        node.append("title")
            .text(d => `Experiment: ${d.group}\nUO: ${d.name}\nStatus: ${d.status}`);

        // 선택된 노드 하이라이트
        node.filter(d => d.id === selectedNodeId).attr('stroke', '#f39c12').attr('stroke-width', 6);

        // 노드 레이블(텍스트) 그리기
        const labels = svg.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(nodes)
            .enter().append("text")
            .attr("text-anchor", "middle")
            .attr("dy", -20) // 원 위에 위치
            .attr("font-size", "10px")
            .attr("fill", "#333")
            .text(d => d.name);

        // 시뮬레이션의 'tick' 이벤트마다 화면 업데이트
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });

        // 드래그 기능 정의
        function drag(simulation) {
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }

    }, [experiments, selectedNodeId, onNodeClick]); // 의존성 배열 업데이트

    return (
        <div className="graph-container">
            <svg ref={svgRef}></svg>
        </div>
    );
};

export default WorkflowGraph;
