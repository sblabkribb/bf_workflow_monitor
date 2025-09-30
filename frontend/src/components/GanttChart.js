import React, { useEffect, useMemo, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
    startOnLoad: false, // We will render it manually
    theme: 'default',
    gantt: {
        axisFormat: '%m-%d',
    },
});

const GanttChart = ({ experiments }) => {
    const chartContainerRef = useRef(null);

    const chartsData = useMemo(() => {
        if (!experiments || experiments.length === 0) return [];

        const allCharts = experiments.map(exp => {
            if (!exp.workflows || !exp.workflows.some(wf => wf.unit_operations && wf.unit_operations.length > 0)) {
                return `
### ${exp.title} (${exp.folder_name})

(표시할 데이터가 없습니다.)
`;              
                return { id: exp.folder_name, title: exp.title, markdown: null };
            }

            const chartLines = [
                'gantt',
                '    dateFormat YYYY-MM-DD',
                '    axisFormat %m-%d',
            ];

            exp.workflows.forEach(wf => {
                if (!wf.unit_operations || wf.unit_operations.length === 0) return;

                chartLines.push(`\n    section ${wf.title}`);

                wf.unit_operations.forEach(uo => {
                    if (!uo.start_date) return;

                    let statusKeyword = '';
                    if (uo.status === 'Completed') statusKeyword = 'done, ';
                    else if (uo.status === 'In Progress') statusKeyword = 'active, ';

                    // 날짜에서 시간 정보 제거
                    const startDate = uo.start_date.split(' ')[0];
                    // 종료 날짜가 없으면 오늘 날짜로 설정
                    const endDate = uo.end_date ? uo.end_date.split(' ')[0] : new Date().toISOString().split('T')[0];

                    const cleanName = uo.name.replace(/:/g, '');
                    const taskName = cleanName.length > 28 ? `${cleanName.substring(0, 25)}...` : cleanName;

                    chartLines.push(`    ${taskName} :${statusKeyword}${uo.id}, ${startDate}, ${endDate}`);
                });
            });

            return {
                id: exp.folder_name,
                title: exp.title,
                markdown: chartLines.join('\n')
            };
        });
        return allCharts;
    }, [experiments]);

    useEffect(() => {
        if (chartContainerRef.current && chartsData.length > 0) {
            chartContainerRef.current.innerHTML = ''; // Clear previous charts
            chartsData.forEach(async (chart, index) => {
                if (chart.markdown) {
                    try {
                        const { svg } = await mermaid.render(`gantt-chart-${chart.id}-${index}`, chart.markdown);
                        const chartDiv = document.createElement('div');
                        chartDiv.className = 'gantt-chart-item';
                        chartDiv.innerHTML = `<h3>${chart.title}</h3>${svg}`;
                        chartContainerRef.current?.appendChild(chartDiv);
                    } catch (e) {
                        console.error(`Error rendering mermaid chart for ${chart.title}:`, e);
                    }
                }
            });
        }
    }, [chartsData]);

    if (chartsData.length === 0) return <div>Gantt Chart 데이터를 불러오는 중입니다...</div>;

    return <div className="mermaid-gantt" ref={chartContainerRef} />;
};

export default GanttChart;