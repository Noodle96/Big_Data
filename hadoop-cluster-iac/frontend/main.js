const API_BASE = "http://127.0.0.1:5000/api";

let votosTotales = [];
let currentPage = 0;
const pageSize = 5;
let votesRankingPage = 0;
let ganadorRegion = [];
let winnerRegionPage = 0;
const winnerPageSize = 10;
let nulosBlancosRegion = [];
let participacionRegion = [];
let votosProvincia = [];

function formatNumber(value) {
    return Number(value).toLocaleString("es-PE");
}

function formatPercent(value) {
    return `${Number(value).toFixed(2)}%`;
}

async function fetchJSON(url) {
    const response = await fetch(url);
    return await response.json();
}renderWinnerRegionChart

function setupNavigation() {
    const buttons = document.querySelectorAll(".nav-btn");
    const screens = document.querySelectorAll(".screen");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            buttons.forEach((btn) => btn.classList.remove("active"));
            screens.forEach((screen) => screen.classList.remove("active-screen"));

            button.classList.add("active");

            const sectionId = button.dataset.section;
            document.getElementById(sectionId).classList.add("active-screen");
        });
    });
}

function renderSummaryCards(summary) {
    const container = d3.select("#summary-cards");

    const cards = [
        { label: "Total votos", value: formatNumber(summary.total_votos) },
        { label: "Electores hábiles", value: formatNumber(summary.total_electores) },
        { label: "Votos nulos", value: formatNumber(summary.votos_nulos) },
        { label: "Votos blancos", value: formatNumber(summary.votos_blancos) },
        { label: "Participación", value: formatPercent(summary.participacion_general_pct) },
    ];

    container.selectAll(".card")
        .data(cards)
        .join("div")
        .attr("class", "card")
        .html((d) => `
            <h3>${d.label}</h3>
            <p>${d.value}</p>
        `);
}

function renderTopVotesChart() {
    const svg = d3.select("#top-votes-chart");
    svg.selectAll("*").remove();

    const width = svg.node().clientWidth;
    const height = svg.node().clientHeight;
    const margin = { top: 30, right: 30, bottom: 80, left: 230 };

    const start = currentPage * pageSize;
    const pageData = votosTotales.slice(start, start + pageSize);

    const x = d3.scaleLinear()
        .domain([0, d3.max(pageData, d => d.votos)])
        .range([margin.left, width - margin.right]);

    const y = d3.scaleBand()
        .domain(pageData.map(d => d.organizacion))
        .range([margin.top, height - margin.bottom])
        .padding(0.25);

    const tooltip = d3.select("#tooltip");

    svg.append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(".2s")));

    svg.append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y));

    svg.selectAll("rect")
        .data(pageData)
        .join("rect")
        .attr("x", margin.left)
        .attr("y", d => y(d.organizacion))
        .attr("width", d => x(d.votos) - margin.left)
        .attr("height", y.bandwidth())
        .attr("rx", 6)
        .on("mousemove", (event, d) => {
            tooltip
                .style("display", "block")
                .style("left", `${event.pageX + 12}px`)
                .style("top", `${event.pageY + 12}px`)
                .html(`
                    <strong>${d.organizacion}</strong><br>
                    Votos: ${formatNumber(d.votos)}<br>
                    Porcentaje: ${formatPercent(d.porcentaje)}
                `);
        })
        .on("mouseleave", () => {
            tooltip.style("display", "none");
        });

    svg.selectAll(".bar-label")
        .data(pageData)
        .join("text")
        .attr("class", "bar-label")
        .attr("x", d => x(d.votos) + 8)
        .attr("y", d => y(d.organizacion) + y.bandwidth() / 2 + 5)
        .text(d => formatNumber(d.votos))
        .style("font-size", "13px")
        .style("font-weight", "bold");
}

function setupPagination() {
    document.getElementById("prev-btn").addEventListener("click", () => {
        currentPage = Math.max(0, currentPage - 1);
        renderTopVotesChart();
    });

    document.getElementById("next-btn").addEventListener("click", () => {
        const maxPage = Math.floor((votosTotales.length - 1) / pageSize);
        currentPage = Math.min(maxPage, currentPage + 1);
        renderTopVotesChart();
    });
}

function setupVotesRankingPagination() {
    document.getElementById("votes-prev-btn").addEventListener("click", () => {
        votesRankingPage = Math.max(0, votesRankingPage - 1);
        renderVotesRankingChart();
    });

    document.getElementById("votes-next-btn").addEventListener("click", () => {
        const maxPage = Math.floor((votosTotales.length - 1) / pageSize);
        votesRankingPage = Math.min(maxPage, votesRankingPage + 1);
        renderVotesRankingChart();
    });
}

async function init() {
    setupNavigation();
    setupPagination();
    setupVotesRankingPagination();

    const summary = await fetchJSON(`${API_BASE}/resumen`);
    votosTotales = await fetchJSON(`${API_BASE}/votos-totales`);
    ganadorRegion = await fetchJSON(`${API_BASE}/ganador-region`);
    nulosBlancosRegion = await fetchJSON(`${API_BASE}/nulos-blancos-region`);
    participacionRegion = await fetchJSON(`${API_BASE}/participacion-region`);
    votosProvincia = await fetchJSON(`${API_BASE}/votos-provincia`);

    renderSummaryCards(summary);
    renderTopVotesChart();
    renderVotesRankingChart();
    renderWinnerRegionChart();
    renderNulosBlancosChart();
    renderParticipacionRegionChart();
    setupProvinceView();
    setupWinnerRegionPagination();
}

function renderVotesRankingChart() {
    const svg = d3.select("#votes-ranking-chart");
    svg.selectAll("*").remove();

    const width = svg.node().clientWidth;
    const height = svg.node().clientHeight;
    const margin = { top: 30, right: 80, bottom: 70, left: 260 };

    const start = votesRankingPage * pageSize;
    const pageData = votosTotales.slice(start, start + pageSize);

    const x = d3.scaleLinear()
        .domain([0, d3.max(pageData, d => d.votos)])
        .range([margin.left, width - margin.right]);

    const y = d3.scaleBand()
        .domain(pageData.map(d => d.organizacion))
        .range([margin.top, height - margin.bottom])
        .padding(0.25);

    const tooltip = d3.select("#tooltip");

    svg.append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format(".2s")));

    svg.append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y));

    svg.selectAll("rect")
        .data(pageData)
        .join("rect")
        .attr("x", margin.left)
        .attr("y", d => y(d.organizacion))
        .attr("width", d => x(d.votos) - margin.left)
        .attr("height", y.bandwidth())
        .attr("rx", 6)
        .on("mousemove", (event, d) => {
            tooltip
                .style("display", "block")
                .style("left", `${event.pageX + 12}px`)
                .style("top", `${event.pageY + 12}px`)
                .html(`
                    <strong>${d.organizacion}</strong><br>
                    Votos: ${formatNumber(d.votos)}<br>
                    Porcentaje nacional: ${formatPercent(d.porcentaje)}
                `);
        })
        .on("mouseleave", () => {
            tooltip.style("display", "none");
        });

    svg.selectAll(".vote-label")
        .data(pageData)
        .join("text")
        .attr("class", "vote-label")
        .attr("x", d => x(d.votos) + 8)
        .attr("y", d => y(d.organizacion) + y.bandwidth() / 2 + 5)
        .text(d => `${formatNumber(d.votos)} (${formatPercent(d.porcentaje)})`)
        .style("font-size", "13px")
        .style("font-weight", "bold");

    const maxPage = Math.floor((votosTotales.length - 1) / pageSize);
    document.getElementById("votes-page-label").textContent =
        `Página ${votesRankingPage + 1} de ${maxPage + 1}`;
}

function setupWinnerRegionPagination() {
    document.getElementById("winner-prev-btn").addEventListener("click", () => {
        winnerRegionPage = Math.max(0, winnerRegionPage - 1);
        renderWinnerRegionChart();
    });

    document.getElementById("winner-next-btn").addEventListener("click", () => {
        const maxPage = Math.floor((ganadorRegion.length - 1) / winnerPageSize);
        winnerRegionPage = Math.min(maxPage, winnerRegionPage + 1);
        renderWinnerRegionChart();
    });
}

function renderWinnerRegionChart() {
    const svg = d3.select("#winner-region-chart");
    svg.selectAll("*").remove();

    const width = 1100;
    const height = 620;

    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const margin = { top: 30, right: 260, bottom: 60, left: 150 };

    const sortedData = [...ganadorRegion].sort((a, b) => b.votos - a.votos);

    const start = winnerRegionPage * winnerPageSize;
    const data = sortedData.slice(start, start + winnerPageSize);

    const x = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.votos)])
        .range([margin.left, width - margin.right]);

    const y = d3.scaleBand()
        .domain(data.map(d => d.region))
        .range([margin.top, height - margin.bottom])
        .padding(0.25);

    const color = d3.scaleOrdinal(d3.schemeTableau10)
        .domain([...new Set(ganadorRegion.map(d => d.ganador))]);

    const tooltip = d3.select("#tooltip");

    svg.append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format(".2s")));

    svg.append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y));

    svg.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", margin.left)
        .attr("y", d => y(d.region))
        .attr("width", d => x(d.votos) - margin.left)
        .attr("height", y.bandwidth())
        .attr("rx", 6)
        .attr("fill", d => color(d.ganador))
        .on("mousemove", (event, d) => {
            tooltip
                .style("display", "block")
                .style("left", `${event.pageX + 12}px`)
                .style("top", `${event.pageY + 12}px`)
                .html(`
                    <strong>${d.region}</strong><br>
                    Ganador: ${d.ganador}<br>
                    Votos: ${formatNumber(d.votos)}
                `);
        })
        .on("mouseleave", () => tooltip.style("display", "none"));

    svg.selectAll(".winner-label")
        .data(data)
        .join("text")
        .attr("x", d => x(d.votos) + 8)
        .attr("y", d => y(d.region) + y.bandwidth() / 2 + 5)
        .text(d => d.ganador.length > 35 ? d.ganador.slice(0, 35) + "..." : d.ganador)
        .style("font-size", "12px")
        .style("font-weight", "bold");

    const maxPage = Math.floor((sortedData.length - 1) / winnerPageSize);

    document.getElementById("winner-page-label").textContent =
        `Página ${winnerRegionPage + 1} de ${maxPage + 1}`;
}


function renderNulosBlancosChart() {
    const svg = d3.select("#nulos-blancos-chart");
    svg.selectAll("*").remove();

    const width = 1100;
    const height = 620;

    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const margin = { top: 40, right: 40, bottom: 120, left: 90 };

    const grouped = d3.rollups(
        nulosBlancosRegion,
        values => ({
            nulos: values.find(d => d.tipo_voto === "VOTOS NULOS")?.votos || 0,
            blancos: values.find(d => d.tipo_voto === "VOTOS EN BLANCO")?.votos || 0,
        }),
        d => d.region
    ).map(([region, values]) => ({
        region,
        ...values,
    }));

    const data = grouped.sort((a, b) => (b.nulos + b.blancos) - (a.nulos + a.blancos));

    const x0 = d3.scaleBand()
        .domain(data.map(d => d.region))
        .range([margin.left, width - margin.right])
        .padding(0.2);

    const x1 = d3.scaleBand()
        .domain(["Nulos", "Blancos"])
        .range([0, x0.bandwidth()])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => Math.max(d.nulos, d.blancos))])
        .nice()
        .range([height - margin.bottom, margin.top]);

    const tooltip = d3.select("#tooltip");

    svg.append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(x0))
        .selectAll("text")
        .attr("transform", "rotate(-55)")
        .style("text-anchor", "end")
        .style("font-size", "11px");

    svg.append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y).ticks(6).tickFormat(d3.format(".2s")));

    const regionGroups = svg.selectAll(".region-group")
        .data(data)
        .join("g")
        .attr("transform", d => `translate(${x0(d.region)}, 0)`);

    regionGroups.selectAll("rect")
        .data(d => [
            { region: d.region, tipo: "Nulos", votos: d.nulos },
            { region: d.region, tipo: "Blancos", votos: d.blancos },
        ])
        .join("rect")
        .attr("x", d => x1(d.tipo))
        .attr("y", d => y(d.votos))
        .attr("width", x1.bandwidth())
        .attr("height", d => height - margin.bottom - y(d.votos))
        .attr("rx", 4)
        .attr("class", d => d.tipo === "Nulos" ? "bar-nulos" : "bar-blancos")
        .on("mousemove", (event, d) => {
            tooltip
                .style("display", "block")
                .style("left", `${event.pageX + 12}px`)
                .style("top", `${event.pageY + 12}px`)
                .html(`
                    <strong>${d.region}</strong><br>
                    Tipo: ${d.tipo}<br>
                    Votos: ${formatNumber(d.votos)}
                `);
        })
        .on("mouseleave", () => tooltip.style("display", "none"));

    const legend = svg.append("g")
        .attr("transform", `translate(${width - 220}, ${margin.top})`);

    legend.append("rect")
        .attr("width", 14)
        .attr("height", 14)
        .attr("class", "bar-nulos");

    legend.append("text")
        .attr("x", 22)
        .attr("y", 12)
        .text("Votos nulos");

    legend.append("rect")
        .attr("y", 24)
        .attr("width", 14)
        .attr("height", 14)
        .attr("class", "bar-blancos");

    legend.append("text")
        .attr("x", 22)
        .attr("y", 36)
        .text("Votos en blanco");
}

function renderParticipacionRegionChart() {
    const svg = d3.select("#participacion-region-chart");
    svg.selectAll("*").remove();

    const width = 1100;
    const height = 620;

    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const margin = { top: 40, right: 90, bottom: 120, left: 90 };

    const data = [...participacionRegion].sort(
        (a, b) => b.participacion_pct - a.participacion_pct
    );

    const x = d3.scaleBand()
        .domain(data.map(d => d.region))
        .range([margin.left, width - margin.right])
        .padding(0.25);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.participacion_pct)])
        .nice()
        .range([height - margin.bottom, margin.top]);

    const tooltip = d3.select("#tooltip");

    svg.append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "rotate(-55)")
        .style("text-anchor", "end")
        .style("font-size", "11px");

    svg.append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y).ticks(6).tickFormat(d => `${d}%`));

    svg.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", d => x(d.region))
        .attr("y", d => y(d.participacion_pct))
        .attr("width", x.bandwidth())
        .attr("height", d => height - margin.bottom - y(d.participacion_pct))
        .attr("rx", 5)
        .attr("class", "bar-participacion")
        .on("mousemove", (event, d) => {
            tooltip
                .style("display", "block")
                .style("left", `${event.pageX + 12}px`)
                .style("top", `${event.pageY + 12}px`)
                .html(`
                    <strong>${d.region}</strong><br>
                    Participación: ${formatPercent(d.participacion_pct)}<br>
                    Votos emitidos: ${formatNumber(d.total_votos)}<br>
                    Electores hábiles: ${formatNumber(d.total_electores)}
                `);
        })
        .on("mouseleave", () => tooltip.style("display", "none"));

    svg.selectAll(".participacion-label")
        .data(data)
        .join("text")
        .attr("class", "participacion-label")
        .attr("x", d => x(d.region) + x.bandwidth() / 2)
        .attr("y", d => y(d.participacion_pct) - 6)
        .attr("text-anchor", "middle")
        .text(d => `${d.participacion_pct.toFixed(1)}%`)
        .style("font-size", "11px")
        .style("font-weight", "bold");
}

function setupProvinceView() {
    const regions = [...new Set(votosProvincia.map(d => d.region))].sort();

    const select = d3.select("#region-select");

    select.selectAll("option")
        .data(regions)
        .join("option")
        .attr("value", d => d)
        .text(d => d);

    select.on("change", (event) => {
        renderProvinceChart(event.target.value);
    });

    if (regions.length > 0) {
        renderProvinceChart(regions[0]);
    }
}

function renderProvinceChart(selectedRegion) {
    const svg = d3.select("#votos-provincia-chart");
    svg.selectAll("*").remove();

    const width = 1100;
    const height = 640;

    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const margin = { top: 40, right: 80, bottom: 120, left: 220 };

    const filtered = votosProvincia.filter(d => d.region === selectedRegion);

    const provinceTotals = d3.rollups(
        filtered,
        values => d3.sum(values, d => d.votos),
        d => d.provincia
    )
        .map(([provincia, votos]) => ({ provincia, votos }))
        .sort((a, b) => b.votos - a.votos)
        .slice(0, 15);

    const x = d3.scaleLinear()
        .domain([0, d3.max(provinceTotals, d => d.votos)])
        .range([margin.left, width - margin.right]);

    const y = d3.scaleBand()
        .domain(provinceTotals.map(d => d.provincia))
        .range([margin.top, height - margin.bottom])
        .padding(0.25);

    const tooltip = d3.select("#tooltip");

    svg.append("g")
        .attr("transform", `translate(0, ${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.format(".2s")));

    svg.append("g")
        .attr("transform", `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y));

    svg.selectAll("rect")
        .data(provinceTotals)
        .join("rect")
        .attr("x", margin.left)
        .attr("y", d => y(d.provincia))
        .attr("width", d => x(d.votos) - margin.left)
        .attr("height", y.bandwidth())
        .attr("rx", 6)
        .attr("class", "bar-provincia")
        .on("mousemove", (event, d) => {
            tooltip
                .style("display", "block")
                .style("left", `${event.pageX + 12}px`)
                .style("top", `${event.pageY + 12}px`)
                .html(`
                    <strong>${selectedRegion} - ${d.provincia}</strong><br>
                    Total votos: ${formatNumber(d.votos)}
                `);
        })
        .on("mouseleave", () => tooltip.style("display", "none"));

    svg.selectAll(".province-label")
        .data(provinceTotals)
        .join("text")
        .attr("class", "province-label")
        .attr("x", d => x(d.votos) + 8)
        .attr("y", d => y(d.provincia) + y.bandwidth() / 2 + 5)
        .text(d => formatNumber(d.votos))
        .style("font-size", "12px")
        .style("font-weight", "bold");
}

init();