import json
import math

def calcular_v_aiken(datos, valor_minimo=1, valor_maximo=5):
    """
    datos: Lista de listas, donde cada sublista son las calificaciones de los expertos para un ítem.
    valor_minimo: El valor más bajo de la escala (l_0).
    valor_maximo: El valor más alto de la escala.
    """
    n_expertos = len(datos[0])
    k = valor_maximo - valor_minimo
    resultados = []

    for i, item_ratings in enumerate(datos):
        S = sum([r - valor_minimo for r in item_ratings])
        v = S / (n_expertos * k)
        
        # Error estándar (opcional)
        # s_v = math.sqrt( (v * (1 - v)) / (n_expertos * k) )
        
        resultados.append({
            "item": i + 1,
            "v_aiken": round(v, 4),
            "S": S,
            "promedio": round(sum(item_ratings) / n_expertos, 2),
            "status": "Aceptable" if v >= 0.70 else "Revisar"
        })
    
    return resultados

def generar_html(resultados, n_expertos):
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis V de Aiken - Juicio de Expertos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
        }}
        .glass {{
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        }}
        .gradient-text {{
            background: linear-gradient(90deg, #4f46e5, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .bar {{
            fill: url(#barGradient);
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .bar:hover {{
            filter: brightness(1.1);
            opacity: 0.8;
        }}
        .axis-label {{
            font-size: 10px;
            fill: #64748b;
            font-weight: 500;
        }}
        .grid-line {{
            stroke: #e2e8f0;
            stroke-width: 1px;
            stroke-dasharray: 4;
        }}
        #tooltip {{
            position: absolute;
            background: rgba(15, 23, 42, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 50;
        }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div id="tooltip"></div>
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="mb-10 text-center">
            <h1 class="text-4xl md:text-5xl font-bold gradient-text mb-4">Reporte de Validez de Contenido</h1>
            <p class="text-slate-600 text-lg">Coeficiente V de Aiken - Juicio de {n_expertos} Expertos</p>
            <div class="mt-4 flex justify-center gap-4">
                <span class="px-4 py-2 glass rounded-full text-sm font-medium text-slate-700">Expertos: {n_expertos}</span>
                <span class="px-4 py-2 glass rounded-full text-sm font-medium text-slate-700">Criterio: > 0.70 Valido</span>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            <!-- Estadísticas Generales -->
            <div class="lg:col-span-1 flex flex-col gap-6">
                <div class="glass p-6 rounded-3xl">
                    <h3 class="text-xl font-bold text-slate-800 mb-4">Resumen</h3>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-slate-500">Total Ítems</span>
                            <span class="text-2xl font-bold text-indigo-600">{len(resultados)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-500">V Promedio</span>
                            <span class="text-2xl font-bold text-cyan-500">{round(sum(r['v_aiken'] for r in resultados) / len(resultados), 3)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-slate-500">Válidos</span>
                            <span class="text-2xl font-bold text-emerald-500">{len([r for r in resultados if r['status'] == 'Aceptable'])}</span>
                        </div>
                    </div>
                </div>

                <div class="glass p-6 rounded-3xl">
                    <h3 class="text-xl font-bold text-slate-800 mb-4">Distribución de V</h3>
                    <div id="vD3Chart" class="w-full"></div>
                </div>
            </div>

            <!-- Tabla de Resultados -->
            <div class="lg:col-span-2">
                <div class="glass overflow-hidden rounded-3xl">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-50/50">
                                <th class="p-4 font-bold text-slate-700 border-b border-slate-100">Ítem</th>
                                <th class="p-4 font-bold text-slate-700 border-b border-slate-100 uppercase tracking-wider text-xs">V de Aiken</th>
                                <th class="p-4 font-bold text-slate-700 border-b border-slate-100 uppercase tracking-wider text-xs">Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f'''
                            <tr class="hover:bg-white/40 transition-colors">
                                <td class="p-4 font-semibold text-slate-800"># {r['item']}</td>
                                <td class="p-4">
                                    <div class="flex items-center gap-3">
                                        <div class="w-full bg-slate-200 rounded-full h-2 max-w-[100px]">
                                            <div class="bg-indigo-500 h-2 rounded-full" style="width: {r['v_aiken'] * 100}%"></div>
                                        </div>
                                        <span class="font-mono font-bold text-slate-700">{r['v_aiken']}</span>
                                    </div>
                                </td>
                                <td class="p-4">
                                    <span class="px-3 py-1 rounded-full text-xs font-bold {'text-emerald-700 bg-emerald-100' if r['status'] == 'Aceptable' else 'text-rose-700 bg-rose-100'}">
                                        {r['status']}
                                    </span>
                                </td>
                            </tr>
                            ''' for r in resultados])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Footer Info -->
        <footer class="text-center text-slate-400 text-sm mt-12 pb-8">
            <p>Generado con Python & D3.js - Antigravity AI</p>
        </footer>
    </div>

    <script>
        const data = {json.dumps(resultados)};
        const margin = {{top: 20, right: 20, bottom: 40, left: 40}};
        const container = document.getElementById('vD3Chart');
        const width = container.offsetWidth - margin.left - margin.right;
        const height = 250 - margin.top - margin.bottom;

        const svg = d3.select("#vD3Chart")
            .append("svg")
            .attr("viewBox", `0 0 ${{width + margin.left + margin.right}} ${{height + margin.top + margin.bottom}}`)
            .append("g")
            .attr("transform", `translate(${{margin.left}}, ${{margin.top}})`);

        // Gradient
        const defs = svg.append("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", "barGradient")
            .attr("x1", "0%").attr("y1", "100%")
            .attr("x2", "0%").attr("y2", "0%");

        gradient.append("stop").attr("offset", "0%").attr("stop-color", "#6366f1");
        gradient.append("stop").attr("offset", "100%").attr("stop-color", "#06b6d4");

        const x = d3.scaleBand()
            .range([0, width])
            .domain(data.map(d => d.item))
            .padding(0.3);

        const y = d3.scaleLinear()
            .domain([0, 1])
            .range([height, 0]);

        // Grid lines
        svg.append("g")
            .attr("class", "grid")
            .call(d3.axisLeft(y)
                .ticks(5)
                .tickSize(-width)
                .tickFormat("")
            )
            .selectAll(".tick line")
            .attr("class", "grid-line");

        svg.append("g")
            .attr("transform", `translate(0, ${{height}})`)
            .call(d3.axisBottom(x).tickSize(0))
            .attr("class", "axis-label")
            .select(".domain").remove();

        svg.append("g")
            .call(d3.axisLeft(y).ticks(5).tickSize(0))
            .attr("class", "axis-label")
            .select(".domain").remove();

        const tooltip = d3.select("#tooltip");

        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("rx", 6)
            .attr("x", d => x(d.item))
            .attr("width", x.bandwidth())
            .attr("y", height)
            .attr("height", 0)
            .on("mouseover", (event, d) => {{
                tooltip.style("opacity", 1)
                       .html(`Ítem #${{d.item}}<br>V: ${{d.v_aiken}}`);
            }})
            .on("mousemove", (event) => {{
                tooltip.style("left", (event.pageX + 10) + "px")
                       .style("top", (event.pageY - 20) + "px");
            }})
            .on("mouseout", () => tooltip.style("opacity", 0))
            .transition()
            .duration(800)
            .attr("y", d => y(d.v_aiken))
            .attr("height", d => height - y(d.v_aiken));

    </script>
</body>
</html>
    """
    with open("reporte_aiken.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Reporte generado con éxito: reporte_aiken.html")

if __name__ == "__main__":
    # Datos de ejemplo: 10 ítems evaluados por 3 expertos en escala de 1 a 5
    # Cada sublista representa las calificaciones de los 3 expertos para un ítem específico.
    muestra_datos = [
        [5, 5, 4], # Item 1
        [4, 5, 4], # Item 2
        [3, 2, 4], # Item 3
        [5, 4, 5], # Item 4
        [5, 5, 5], # Item 5
        [4, 4, 3], # Item 6
        [5, 5, 4], # Item 7
        [2, 3, 2], # Item 8
        [4, 5, 5], # Item 9
        [5, 4, 4], # Item 10
    ]
    
    n_expertos = len(muestra_datos[0])
    resultados = calcular_v_aiken(muestra_datos, valor_minimo=1, valor_maximo=5)
    generar_html(resultados, n_expertos=n_expertos)
