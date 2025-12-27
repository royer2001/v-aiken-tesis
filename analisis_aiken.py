import json
import math

def calcular_v_aiken(expertos_evaluaciones, nombres_items, criterios, valor_minimo=1, valor_maximo=4):
    """
    Agrega los datos de los expertos y calcula la V de Aiken.
    """
    n_expertos = len(expertos_evaluaciones)
    k = valor_maximo - valor_minimo
    resultados_items = []
    
    for i, nombre_item in enumerate(nombres_items):
        item_data = {"item_num": i + 1, "nombre": nombre_item, "criterios": {}}
        v_total_item = 0
        
        for crit in criterios:
            # Obtener calificaciones de todos los expertos para este ítem y criterio
            ratings = [exp["evaluaciones"][nombre_item][crit] for exp in expertos_evaluaciones]
            S = sum([r - valor_minimo for r in ratings])
            v = S / (n_expertos * k)
            item_data["criterios"][crit] = round(v, 4)
            v_total_item += v
            
        v_promedio_item = v_total_item / len(criterios)
        item_data["v_aiken_global"] = round(v_promedio_item, 4)
        item_data["status"] = "Aceptable" if v_promedio_item >= 0.70 else "Revisar"
        resultados_items.append(item_data)
        
    return resultados_items

def generar_html(resultados, expertos_evaluaciones):
    criterios = list(resultados[0]["criterios"].keys())
    expertos_nombres = [exp["nombre"] for exp in expertos_evaluaciones]
    n_expertos = len(expertos_nombres)
    v_promedio_global = round(sum(r['v_aiken_global'] for r in resultados) / len(resultados), 3)
    
    # Datos para inyectar en JS
    evaluaciones_json = json.dumps(expertos_evaluaciones)
    resultados_json = json.dumps(resultados)
    criterios_json = json.dumps(criterios)

    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validez de Contenido - V de Aiken</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <!-- SheetJS para Exportar a Excel -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
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
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .tab-btn.active {{
            background: white;
            color: #4f46e5;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .gradient-text {{
            background: linear-gradient(90deg, #4f46e5, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .btn-export {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .btn-export:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4);
        }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <header class="mb-8 flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="text-center md:text-left">
                <h1 class="text-4xl font-bold gradient-text mb-1">Validez de Contenido</h1>
                <p class="text-slate-500 font-medium">Análisis Estadístico - Coeficiente V de Aiken</p>
            </div>
            <button onclick="exportToExcel()" class="btn-export flex items-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-3 rounded-2xl font-bold text-sm shadow-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                Exportar a Excel
            </button>
        </header>

        <!-- Navigation Tabs -->
        <div class="flex justify-center mb-8">
            <div class="glass p-1.5 rounded-2xl flex gap-1">
                <button onclick="showTab('resumen')" id="btn-resumen" class="tab-btn active px-6 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 text-slate-500 hover:text-slate-700">
                    Matriz General (Aiken)
                </button>
                <button onclick="showTab('expertos')" id="btn-expertos" class="tab-btn px-6 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 text-slate-500 hover:text-slate-700">
                    Detalle por Experto
                </button>
            </div>
        </div>

        <!-- Tab: MATRIZ GENERAL -->
        <div id="resumen" class="tab-content active animate-in fade-in duration-500">
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <div class="lg:col-span-1 space-y-6">
                    <div class="glass p-6 rounded-3xl text-center">
                        <div class="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Coeficiente Global</div>
                        <div class="text-4xl font-black text-indigo-600 mb-2">{v_promedio_global}</div>
                        <div class="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-black uppercase">
                            n = {n_expertos} Expertos
                        </div>
                    </div>
                    
                    <div class="glass p-6 rounded-3xl">
                        <h4 class="font-bold text-slate-800 mb-4 text-xs uppercase tracking-widest">Interpretación</h4>
                        <div class="space-y-4">
                            <div class="flex items-center gap-3">
                                <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
                                <span class="text-xs text-slate-600">≥ 0.70 : Válido</span>
                            </div>
                            <div class="flex items-center gap-3">
                                <div class="w-2 h-2 rounded-full bg-rose-500"></div>
                                <span class="text-xs text-slate-600">< 0.70 : Revisar</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-3">
                    <div class="glass overflow-hidden rounded-3xl">
                        <div class="overflow-x-auto">
                            <table id="tableMain" class="w-full text-left">
                                <thead>
                                    <tr class="bg-slate-50/50">
                                        <th class="p-5 font-bold text-slate-700 text-[11px] uppercase tracking-wider">Indicador Evaluado</th>
                                        {"".join([f'<th class="p-5 font-bold text-slate-700 text-[11px] uppercase tracking-wider text-center">{c}</th>' for c in criterios])}
                                        <th class="p-5 font-bold text-indigo-700 text-[11px] uppercase tracking-wider text-center">V Global</th>
                                        <th class="p-5 font-bold text-slate-700 text-[11px] uppercase tracking-wider text-center">Estado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {"".join([f'''
                                    <tr class="hover:bg-white/40 border-b border-slate-50 transition-colors">
                                        <td class="p-5">
                                            <div class="font-bold text-slate-800">{r['nombre']}</div>
                                        </td>
                                        {"".join([f'<td class="p-5 text-center font-mono font-bold text-slate-500">{r["criterios"][c]}</td>' for c in criterios])}
                                        <td class="p-5 text-center">
                                            <span class="font-mono font-black text-indigo-600 text-lg">{r['v_aiken_global']}</span>
                                        </td>
                                        <td class="p-5 text-center">
                                            <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase {'bg-emerald-100 text-emerald-700' if r['status'] == 'Aceptable' else 'bg-rose-100 text-rose-700'}">
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
            </div>
        </div>

        <!-- Tab: DETALLE POR EXPERTO -->
        <div id="expertos" class="tab-content animate-in slide-in-from-bottom-4 duration-500">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-center">
                {"".join([f'''
                <div class="glass p-6 rounded-3xl border-t-4 border-indigo-500">
                    <div class="flex flex-col items-center gap-2 mb-6 text-center">
                        <div class="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 text-2xl font-black">
                            {idx+1}
                        </div>
                        <h3 class="font-bold text-slate-800 text-lg">{exp['nombre']}</h3>
                        <div class="h-0.5 w-12 bg-indigo-100"></div>
                    </div>
                    <div class="space-y-4">
                        {"".join([f"""
                        <div class="bg-white/40 p-3 rounded-2xl border border-white/50">
                            <div class="text-[10px] font-black text-indigo-400 mb-2 uppercase tracking-tighter">{nombre_item}</div>
                            <div class="grid grid-cols-3 gap-2">
                                {"".join([f'''
                                <div>
                                    <div class="text-[8px] text-slate-400 font-black uppercase">{crit}</div>
                                    <div class="text-lg font-black text-slate-700">{exp['evaluaciones'][nombre_item][crit]}</div>
                                </div>
                                ''' for crit in criterios])}
                            </div>
                        </div>
                        """ for nombre_item in exp['evaluaciones']])}
                    </div>
                </div>
                ''' for idx, exp in enumerate(expertos_evaluaciones)])}
            </div>
        </div>

        <!-- Footer -->
        <footer class="mt-12 pt-8 border-t border-slate-200 text-center">
            <p class="text-slate-400 text-xs font-bold uppercase tracking-widest">
                Juicio de Expertos - Análisis V de Aiken © 2025
            </p>
        </footer>
    </div>

    <script>
        const expertosData = {evaluaciones_json};
        const resultadosData = {resultados_json};
        const criterios = {criterios_json};

        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            document.getElementById('btn-' + tabId).classList.add('active');
        }}

        function exportToExcel() {{
            const wb = XLSX.utils.book_new();
            const nExp = expertosData.length;
            const nItems = resultadosData.length;
            const critCount = criterios.length;
            
            // --- HOJA 1: DATOS DE ENTRADA (TRANSCRIPCIÓN) ---
            // Esta hoja va primero porque la Matriz la referencia
            const ws_datos_data = [
                ["TRANSCRIPCIÓN DE CUESTIONARIOS - EDITABLE"],
                ["Modifique los valores aquí y la Matriz se actualizará"],
                [],
                ["Indicador", "Criterio", ...expertosData.map(e => e.nombre)]
            ];

            // Poblar datos de entrada (filas desde la 5 en adelante)
            resultadosData.forEach((res, resIdx) => {{
                criterios.forEach((crit, critIdx) => {{
                    const row = [res.nombre, crit];
                    expertosData.forEach(exp => {{
                        row.push(exp.evaluaciones[res.nombre][crit]);
                    }});
                    ws_datos_data.push(row);
                }});
            }});

            const ws_datos = XLSX.utils.aoa_to_sheet(ws_datos_data);
            XLSX.utils.book_append_sheet(wb, ws_datos, "Datos");

            // --- HOJA 2: MATRIZ CON FÓRMULAS ---
            const ws_matriz_data = [
                ["CALCULADORA DINÁMICA V DE AIKEN"],
                ["N° Expertos:", nExp, "", "Fórmula V = S / [n × (c-1)]"],
                ["Escala Mín:", 1, "", "S = Σ(ri) - n×Mín"],
                ["Escala Máx:", 4],
                [],
                ["Indicador", "Criterio", "Suma Notas", "S (Σri - n×Mín)", "V de Aiken", "Estado"]
            ];

            const ws_matriz = XLSX.utils.aoa_to_sheet(ws_matriz_data);

            // Añadir fórmulas fila por fila
            let matrizRow = 7; // Fila 7 en Excel (después del encabezado)
            let datosRow = 5;  // Fila 5 en la hoja Datos (primera fila de datos)
            
            for (let i = 0; i < nItems * critCount; i++) {{
                // Columnas en Datos: A=Indicador, B=Criterio, C,D,E...=Expertos
                const colInicioExp = "C";
                const colFinExp = String.fromCharCode(67 + nExp - 1); // C + (nExp-1)
                
                // Fórmulas
                const fIndicador = `Datos!A${{datosRow}}`;
                const fCriterio = `Datos!B${{datosRow}}`;
                const fSumaNotas = `SUM(Datos!${{colInicioExp}}${{datosRow}}:${{colFinExp}}${{datosRow}})`;
                const fS = `C${{matrizRow}} - ($B$2 * $B$3)`;  // SumaNotas - (nExp * Min)
                const fV = `D${{matrizRow}} / ($B$2 * ($B$4 - $B$3))`;  // S / (n * (Max-Min))
                const fEstado = `IF(E${{matrizRow}}>=0.7,"ACEPTABLE","REVISAR")`;

                // Insertar fila con fórmulas
                XLSX.utils.sheet_add_aoa(ws_matriz, [[
                    {{ f: fIndicador }},
                    {{ f: fCriterio }},
                    {{ f: fSumaNotas }},
                    {{ f: fS }},
                    {{ f: fV }},
                    {{ f: fEstado }}
                ]], {{ origin: "A" + matrizRow }});

                matrizRow++;
                datosRow++;
            }}

            // Añadir fila de PROMEDIO GLOBAL al final
            const ultimaFila = matrizRow;
            XLSX.utils.sheet_add_aoa(ws_matriz, [[
                "PROMEDIO GLOBAL", "", "", "", 
                {{ f: `AVERAGE(E7:E${{ultimaFila - 1}})` }},
                {{ f: `IF(E${{ultimaFila}}>=0.7,"VÁLIDO","REVISAR")` }}
            ]], {{ origin: "A" + ultimaFila }});

            XLSX.utils.book_append_sheet(wb, ws_matriz, "Matriz Aiken");
            XLSX.writeFile(wb, "Analisis_V_Aiken_Dinamico.xlsx");
        }}
    </script>
</body>
</html>
    """
    with open("reporte_aiken.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Reporte generado con éxito: reporte_aiken.html")

if __name__ == "__main__":
    # 1. Definir los indicadores de la tesis
    nombres_items = [
        "Porcentaje de ocupación",
        "Días promedio de anticipación",
        "Porcentaje de no-shows"
    ]
    
    # 2. Definir los criterios de validación
    criterios = ["Claridad", "Pertinencia", "Relevancia"]

    # 3. Ingresar las calificaciones de cada experto (De 1 a 4)
    expertos_evaluaciones = [
        {
            "nombre": "Dr. Juan Pérez (Experto 1)",
            "evaluaciones": {
                "Porcentaje de ocupación": {"Claridad": 4, "Pertinencia": 4, "Relevancia": 4},
                "Días promedio de anticipación": {"Claridad": 3, "Pertinencia": 4, "Relevancia": 4},
                "Porcentaje de no-shows": {"Claridad": 4, "Pertinencia": 4, "Relevancia": 4}
            }
        },
        {
            "nombre": "Mg. María García (Experta 2)",
            "evaluaciones": {
                "Porcentaje de ocupación": {"Claridad": 4, "Pertinencia": 4, "Relevancia": 4},
                "Días promedio de anticipación": {"Claridad": 4, "Pertinencia": 4, "Relevancia": 4},
                "Porcentaje de no-shows": {"Claridad": 4, "Pertinencia": 4, "Relevancia": 4}
            }
        },
        {
            "nombre": "Ing. Carlos Ruiz (Experto 3)",
            "evaluaciones": {
                "Porcentaje de ocupación": {"Claridad": 3, "Pertinencia": 4, "Relevancia": 4},
                "Días promedio de anticipación": {"Claridad": 4, "Pertinencia": 3, "Relevancia": 4},
                "Porcentaje de no-shows": {"Claridad": 4, "Pertinencia": 4, "Relevancia": 4}
            }
        }
    ]
    
    # 4. Procesar y Generar
    resultados = calcular_v_aiken(expertos_evaluaciones, nombres_items, criterios, valor_minimo=1, valor_maximo=4)
    generar_html(resultados, expertos_evaluaciones)
