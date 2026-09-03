document.addEventListener('DOMContentLoaded', function() {
    const designForm = document.getElementById('design-form');
    const designResponse = document.getElementById('design-response');
    const deployForm = document.getElementById('deploy-form');
    const deployResponse = document.getElementById('deploy-response');
    const runLog = document.getElementById('run-log');

    // 处理设计表单提交
    const designSpinner = document.getElementById('design-spinner');
    designForm.addEventListener('submit', function(event) {
        event.preventDefault();
        designSpinner.style.display = 'inline-block'; // 显示加载动画
        // 禁用按钮防止重复提交
        const designButton = designForm.querySelector('button[type="submit"]');
        designButton.disabled = true;
        designButton.textContent = 'Processing...';

        const taskDescription = document.getElementById('task_description').value;

        fetch('/design', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `task_description=${encodeURIComponent(taskDescription)}`
        })
        .then(response => response.json())
        .then(data => {
            designResponse.innerText = data.message;
            if(data.status === 'success') {
                loadFSM();
            }
            // 处理完成后隐藏加载动画
            designSpinner.style.display = 'none';
            designButton.disabled = false;
            designButton.textContent = 'Design Multi-Agent System';
        });
    });

    // 处理部署表单提交
    const deploySpinner = document.getElementById('deploy-spinner');
    deployForm.addEventListener('submit', function(event) {
        event.preventDefault();
        deploySpinner.style.display = 'inline-block'; // 显示加载动画
        // 禁用按钮防止重复提交
        const deployButton = deployForm.querySelector('button[type="submit"]');
        deployButton.disabled = true;
        deployButton.textContent = 'Processing...';

        const caseInput = document.getElementById('case_input').value;

        fetch('/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `case_input=${encodeURIComponent(caseInput)}`
        })
        .then(response => response.json())
        .then(data => {
            deployResponse.innerText = data.message;
            if(data.status === 'success') {
                loadLog();
                loadFSM(); // 更新FSM状态
            }
            // 处理完成后隐藏加载动画
            deploySpinner.style.display = 'none';
            deployButton.disabled = false;
            deployButton.textContent = 'Run Test';
        });
    });

    // 加载FSM数据并可视化
    function loadFSM() {
        fetch('/get_fsm')
            .then(response => response.json())
            .then(data => {
                if(data.status === 'error') {
                    alert(data.message);
                    return;
                }
                visualizeFSM(data);
            });
    }

    let currentHighlightedNode = null;

    // 可视化FSM
    function visualizeFSM(data) {
        // 清空之前的图
        d3.select("#fsm-graph").selectAll("*").remove();

        // 添加箭头标记
        const svg = d3.select("#fsm-graph")
                      .append("svg")
                      .attr("width", '100%')
                      .attr("height", '100%')
                      .style("background-color", "transparent");

        const width = document.getElementById('fsm-graph').clientWidth;
        const height = document.getElementById('fsm-graph').clientHeight;

        // Define glow filter
        const defs = svg.append("defs");

        const glowFilter = defs.append("filter")
                               .attr("id", "glow");

        glowFilter.append("feGaussianBlur")
                  .attr("stdDeviation", "3.5")
                  .attr("result", "coloredBlur");

        const feMerge = glowFilter.append("feMerge");
        feMerge.append("feMergeNode")
               .attr("in", "coloredBlur");
        feMerge.append("feMergeNode")
               .attr("in", "SourceGraphic");

        // Arrow markers for links
        defs.append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 15)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
          .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#0ff')
            .style('filter', 'url(#glow)');

        // 准备节点和链接
        const nodes = data.states.states.map(state => ({
            id: state.state_id,
            name: state.state_id,
            instruction: state.instruction,
            agent_id: state.agent_id,
            is_initial: state.is_initial,
            is_final: state.is_final
        }));

        let links = data.states.transitions.map(transition => ({
            source: transition.from_state,
            target: transition.to_state,
            condition: transition.condition
        }));

        // 处理双向边
        const linkCounts = {};
        links.forEach(link => {
            const key = `${link.source}-${link.target}`;
            const reverseKey = `${link.target}-${link.source}`;
            if (link.source !== link.target) {
                if (linkCounts[key]) {
                    link.curve = Math.PI / 4;
                } else if (linkCounts[reverseKey]) {
                    link.curve = -Math.PI / 4;
                } else {
                    link.curve = 0;
                }
                linkCounts[key] = (linkCounts[key] || 0) + 1;
            }
        });

        // 设置SVG画布大小
        svg.attr("width", width).attr("height", height);

        // 设置力导向
        const simulation = d3.forceSimulation(nodes)
                             .force("link", d3.forceLink(links).id(d => d.id).distance(200))
                             .force("charge", d3.forceManyBody().strength(-1000))
                             .force("center", d3.forceCenter(width / 2, height / 2));

        // 绘制链接
        const link = svg.append("g")
                        .attr("class", "links")
                        .selectAll("path")
                        .data(links)
                        .enter()
                        .append("path")
                        .attr("class", "link-path")
                        .attr("stroke", "#0ff")
                        .attr("stroke-width", "1.5px")
                        .attr("fill", "none")
                        .attr("marker-end", "url(#arrow)")
                        .style("filter", "url(#glow)")
                        .on("mouseover", function() {
                            d3.select(this)
                              .attr("stroke-width", "3px");
                        })
                        .on("mouseout", function() {
                            d3.select(this)
                              .attr("stroke-width", "1.5px");
                        })
                        .on("click", function(event, d) {
                            // 移除现有的对话框
                            d3.selectAll(".info-dialog").remove();

                            // 创建对话框
                            const dialog = svg.append("g")
                                              .attr("class", "info-dialog")
                                              .attr("transform", `translate(${d3.pointer(event, svg.node())[0] + 20}, ${d3.pointer(event, svg.node())[1] - 20})`);

                            // 对话框背景
                            dialog.append("rect")
                                  .attr("width", 250)
                                  .attr("height", 150)
                                  .attr("rx", 10)
                                  .attr("ry", 10)
                                  .attr("fill", "rgba(50, 50, 50, 0.95)")
                                  .attr("stroke", "#fff")
                                  .attr("stroke-width", 1.5);

                            // 关闭按钮
                            dialog.append("text")
                                  .attr("x", 290)
                                  .attr("y", 20)
                                  .attr("text-anchor", "end")
                                  .attr("font-size", "16px")
                                  .attr("fill", "#fff")
                                  .style("cursor", "pointer")
                                  .text("✖")
                                  .on("click", function() {
                                      dialog.remove();
                                  });

                            // 信息内容
                            dialog.append("text")
                                  .attr("x", 20)
                                  .attr("y", 30)
                                  .attr("font-size", "14px")
                                  .attr("fill", "#fff")
                                  .text(`Transition Condition:`);

                            dialog.append("foreignObject")
                                  .attr("x", 20)
                                  .attr("y", 40)
                                  .attr("width", 230)
                                  .attr("height", 30)
                                  .append("xhtml:div")
                                  .style("font-size", "12px")
                                  .style("color", "#fff")
                                  .style("overflow-wrap", "break-word")
                                  .html(d.condition);
                        });

        // 绘制节点
        const node = svg.append("g")
                        .attr("class", "nodes")
                        .selectAll("circle")
                        .data(nodes)
                        .enter()
                        .append("circle")
                        .attr("class", "node-circle")
                        .attr("r", 30)
                        .attr("fill", d => {
                            if (d.is_initial) {
                                return "#4CAF50"; // Green for initial nodes
                            } else if (d.is_final) {
                                return "#F44336"; // Red for final nodes
                            } else {
                                return "#2196F3"; // Blue for standard nodes
                            }
                        })
                        .attr("stroke", "#0ff")
                        .attr("stroke-width", 2)
                        .attr("id", d => `node-${d.id}`)
                        .call(d3.drag()
                            .on("start", dragstarted)
                            .on("drag", dragged)
                            .on("end", dragended))
                        .on("mouseover", function() {
                            d3.select(this)
                              .transition()
                              .duration(200)
                              .attr("r", 35);
                        })
                        .on("mouseout", function() {
                            d3.select(this)
                              .transition()
                              .duration(200)
                              .attr("r", 30);
                        })
                        .on("click", function(event, d) {
                            // 移除现有的对话框
                            d3.selectAll(".info-dialog").remove();

                            // 获取节点的位置
                            const [x, y] = [d.x, d.y];

                            // 创建对话框
                            const dialog = svg.append("g")
                                              .attr("class", "info-dialog")
                                              .attr("transform", `translate(${x + 50}, ${y - 60})`);

                            // 对话框背景
                            dialog.append("rect")
                                  .attr("width", 250)
                                  .attr("height", 150)
                                  .attr("rx", 10)
                                  .attr("ry", 10)
                                  .attr("fill", "rgba(50, 50, 50, 0.95)")
                                  .attr("stroke", "#fff")
                                  .attr("stroke-width", 1.5);

                            // 关闭按钮
                            dialog.append("text")
                                  .attr("x", 290)
                                  .attr("y", 20)
                                  .attr("text-anchor", "end")
                                  .attr("font-size", "16px")
                                  .attr("fill", "#fff")
                                  .style("cursor", "pointer")
                                  .text("✖")
                                  .on("click", function() {
                                      dialog.remove();
                                  });

                            // 信息内容
                            dialog.append("text")
                                  .attr("x", 20)
                                  .attr("y", 30)
                                  .attr("font-size", "14px")
                                  .attr("fill", "#fff")
                                  .text(`State ID: ${d.id}`);

                            // 假设有一个agentsMap，可以通过agent_id获取agent信息
                            // 需要在loadFSM之前加载agents数据并创建agentsMap
                            const agent = data.agents.find(a => a.agent_id === d.agent_id);

                            dialog.append("text")
                                  .attr("x", 20)
                                  .attr("y", 60)
                                  .attr("font-size", "14px")
                                  .attr("fill", "#fff")
                                  .text(`Agent Name: ${agent ? agent.name : '未知'}`);

                            dialog.append("text")
                                  .attr("x", 20)
                                  .attr("y", 90)
                                  .attr("font-size", "14px")
                                  .attr("fill", "#fff")
                                  .text(`Instruction:`);

                            dialog.append("foreignObject")
                                  .attr("x", 20)
                                  .attr("y", 100)
                                  .attr("width", 230)
                                  .attr("height", 40)
                                  .append("xhtml:div")
                                  .style("font-size", "12px")
                                  .style("color", "#fff")
                                  .style("overflow-wrap", "break-word")
                                  .html(d.instruction);

                            dialog.append("text")
                                  .attr("x", 20)
                                  .attr("y", 150)
                                  .attr("font-size", "14px")
                                  .attr("fill", "#fff")
                                  .text(`Tools: ${agent && agent.tools ? agent.tools.join(', ') : '无'}`)
                                  .attr("dy", "0.35em");
                        });

        // 更新位置
        simulation.on("tick", () => {
            link.attr("d", d => {
                if (d.source === d.target) {
                    // 自环
                    const x = d.source.x;
                    const y = d.source.y;
                    const loopRadius = 100;
                    return `M${x},${y} 
                            C${x + loopRadius},${y - loopRadius} 
                             ${x + loopRadius},${y + loopRadius} 
                             ${x},${y}`;
                } else {
                    if (d.curve !== undefined) {
                        const dx = d.target.x - d.source.x;
                        const dy = d.target.y - d.source.y;
                        const dr = Math.sqrt(dx * dx + dy * dy);
                        return `M${d.source.x},${d.source.y} 
                                A${dr},${dr} 0 0,${d.curve > 0 ? 1 : 0} 
                                ${d.target.x},${d.target.y}`;
                    } else {
                        // 计算箭头起点和终点在圆边缘
                        const dx = d.target.x - d.source.x;
                        const dy = d.target.y - d.source.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        const sourceX = d.source.x + (dx * 40) / distance;
                        const sourceY = d.source.y + (dy * 40) / distance;
                        const targetX = d.target.x - (dx * 40) / distance;
                        const targetY = d.target.y - (dy * 40) / distance;
                        return `M${sourceX},${sourceY} 
                                L${targetX},${targetY}`;
                    }
                }
            });

            node.attr("cx", d => d.x)
                .attr("cy", d => d.y);

            // Update labels if implemented
        });

        // 拖拽函数
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

        const zoom = d3.zoom()
            .scaleExtent([0.5, 5])
            .on('zoom', (event) => {
                svg.attr('transform', event.transform);
            });

        svg.call(zoom);

        // Add tooltip div
        const tooltip = d3.select("body").append("div")
                      .attr("class", "tooltip")
                      .style("position", "absolute")
                      .style("padding", "8px")
                      .style("background", "rgba(0, 0, 0, 0.8)")
                      .style("color", "#0ff")
                      .style("border-radius", "4px")
                      .style("pointer-events", "none")
                      .style("opacity", 0);

        // Update node mouse events
        node.on("mouseover", function(event, d) {
                d3.select(this)
                  .transition()
                  .duration(200)
                  .attr("r", 35);
                tooltip.transition().duration(200).style("opacity", 0.9);
                tooltip.html(`State ID: ${d.id}<br/>Agent: ${d.agent_id}`)
                       .style("left", (event.pageX + 15) + "px")
                       .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function() {
                d3.select(this)
                  .transition()
                  .duration(200)
                  .attr("r", 30);
                tooltip.transition().duration(500).style("opacity", 0);
            });
    }

    // 加载运行日志
    function loadLog() {
        fetch('/get_log')
            .then(response => response.json())
            .then(data => {
                if(data.status === 'error') {
                    runLog.innerText = data.message;
                    return;
                }
                runLog.innerText = data.log;
            });
    }

    // 加载当前状态并高亮节点
    function loadCurrentState() {
        fetch('/current_state')
            .then(response => response.json())
            .then(data => {
                const currentState = data.current_state;
                if (currentState && currentHighlightedNode !== currentState) {
                    // 取消之前高亮的节点
                    if (currentHighlightedNode) {
                        d3.select(`#node-${currentHighlightedNode}`)
                          .attr("stroke", "#333")
                          .attr("stroke-width", 2);
                    }

                    // 高亮当前节点
                    d3.select(`#node-${currentState}`)
                      .attr("stroke", "yellow")
                      .attr("stroke-width", 4);

                    currentHighlightedNode = currentState;
                }
            });
    }

    // 初始加载FSM和日志
    loadFSM();
    loadLog();

    // 设置每5秒刷新一次日志
    setInterval(loadLog, 5000);

    // 设置每5秒刷新当前状态
    setInterval(loadCurrentState, 5000);

    const generateCasesButton = document.getElementById('generate-cases-button');
    const casesResponse = document.getElementById('cases-response');
    const testCasesDisplay = document.getElementById('test-cases');
    const casesSpinner = document.getElementById('cases-spinner');

    generateCasesButton.addEventListener('click', function() {
        casesSpinner.style.display = 'inline-block';
        generateCasesButton.disabled = true;
        generateCasesButton.textContent = '处理中...';

        fetch('/generate_cases', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            casesResponse.innerText = data.message;
            if(data.status === 'success') {
                loadTestCases();
            }
            casesSpinner.style.display = 'none';
            generateCasesButton.disabled = false;
            generateCasesButton.textContent = '生成测试用例';
        });
    });

    const evolveButton = document.getElementById('evolve-button');
    const evolveResponse = document.getElementById('evolve-response');
    const evolveSpinner = document.getElementById('evolve-spinner');

    evolveButton.addEventListener('click', function() {
        evolveSpinner.style.display = 'inline-block';
        evolveButton.disabled = true;
        evolveButton.textContent = '处理中...';

        fetch('/evolve', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            evolveResponse.innerText = data.message;
            if(data.status === 'success') {
                loadFSM(); // 重新加载更新后的MAS
            }
            evolveSpinner.style.display = 'none';
            evolveButton.disabled = false;
            evolveButton.textContent = '进化多智能体系统';
        });
    });

    function loadTestCases() {
        fetch('/get_test_cases')
            .then(response => response.json())
            .then(data => {
                if(data.status === 'error') {
                    testCasesDisplay.innerText = data.message;
                    return;
                }
                testCasesDisplay.innerText = JSON.stringify(data.test_cases, null, 2);
            });
    }

    // Toggle Deploy Section
    const deployToggleButton = document.getElementById('deploy-toggle-button');
    const deploySection = document.getElementById('deploy-section');

    deployToggleButton.addEventListener('click', function() {
        if (deploySection.style.display === 'none' || deploySection.style.display === '') {
            deploySection.style.display = 'block';
            deployToggleButton.textContent = 'Hide Test Runner';
        } else {
            deploySection.style.display = 'none';
            deployToggleButton.textContent = 'Run Test';
        }
    });

    // Similar toggling for other sections like 'Generate Test Cases' and 'Evolve Multi-Agent System'
});