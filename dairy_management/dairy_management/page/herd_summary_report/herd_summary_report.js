frappe.pages["herd-summary-report"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Dairy Reports Dashboard"),
		single_column: true,
	});

	const charts = [];
	const report_cache = new Map();

	const body = $(`
		<div class="dm-dashboard">
			<div class="dm-banner">
				<div>
					<div class="dm-kicker">Dairy Management</div>
					<h3>${__("All module reports")}</h3>
					<p>${__("One dashboard: KPIs from Herd Summary, then Apex charts for every report in this module.")}</p>
				</div>
				<div class="dm-banner-actions">
					<button type="button" class="dm-btn dm-btn-ghost dm-refresh">${__("Refresh")}</button>
				</div>
			</div>
			<div class="dm-kpis"></div>
			<div id="dm-report-charts" class="dm-report-grid"></div>
		</div>
	`);

	const style = `
		.dm-dashboard { font-family: Inter, sans-serif; }
		.dm-banner {
			background: linear-gradient(135deg,#14532d,#16a34a);
			color: #fff;
			border-radius: 16px;
			padding: 16px;
			display: flex;
			justify-content: space-between;
			gap: 12px;
			align-items: center;
			margin-bottom: 12px;
		}
		.dm-banner h3 { margin: 2px 0; }
		.dm-banner p { margin: 0; opacity: .9; }
		.dm-kicker { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; opacity: .85; }
		.dm-banner-actions { display: flex; gap: 8px; align-items: center; }
		.dm-btn {
			background: #fff;
			color: #14532d;
			border: 0;
			padding: 8px 12px;
			border-radius: 999px;
			font-weight: 600;
			cursor: pointer;
		}
		.dm-btn-ghost { background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.35); }
		.dm-kpis {
			display: grid;
			grid-template-columns: repeat(auto-fit,minmax(180px,1fr));
			gap: 10px;
			margin-bottom: 12px;
		}
		.dm-kpi { border: 1px solid #e5e7eb; border-radius: 12px; padding: 10px; background: #fff; }
		.dm-kpi .value { font-size: 22px; font-weight: 700; }
		.dm-kpi .label { color: #6b7280; font-size: 12px; margin-top: 2px; }
		.dm-report-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit,minmax(360px,1fr));
			gap: 12px;
		}
		.dm-rpt-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; background: #fff; }
		.dm-rpt-head { display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; margin-bottom: 8px; }
		.dm-rpt-title { margin: 0; font-size: 15px; }
		.dm-rpt-link { font-size: 12px; color: #14532d; text-decoration: none; white-space: nowrap; }
		.dm-chart { min-height: 280px; }
		.dm-chart-status { font-size: 12px; color: #6b7280; margin-top: 6px; }
	`;

	if (!document.getElementById("dm-dashboard-style")) {
		$("<style id='dm-dashboard-style'>").text(style).appendTo("head");
	}

	$(page.body).empty().append(body);

	const to_number = (value) => {
		if (value === null || value === undefined || value === "") return 0;
		const n = Number(value);
		return Number.isFinite(n) ? n : 0;
	};

	const format_value = (value, decimals) => {
		if (typeof format_number === "function") {
			return format_number(value, null, decimals);
		}
		return to_number(value).toFixed(decimals);
	};

	const slugify = (value) =>
		String(value || "")
			.toLowerCase()
			.replace(/[^a-z0-9]+/g, "-")
			.replace(/^-+|-+$/g, "");

	const destroy_charts = () => {
		charts.forEach((c) => {
			try {
				c.destroy();
			} catch (e) {
				// ignore
			}
		});
		charts.length = 0;
	};

	const load_apex = () => {
		if (window.ApexCharts) return Promise.resolve();
		return new Promise((resolve, reject) => {
			const sources = [
				"/assets/management_dashboard/js/apexcharts.min.js",
				"https://cdn.jsdelivr.net/npm/apexcharts"
			];

			const try_load = (idx) => {
				if (idx >= sources.length) return reject(new Error("ApexCharts not available"));
				const script = document.createElement("script");
				script.src = sources[idx];
				script.onload = resolve;
				script.onerror = () => try_load(idx + 1);
				document.head.appendChild(script);
			};

			try_load(0);
		});
	};

	const frappe_call = (args) =>
		new Promise((resolve, reject) => {
			frappe.call({
				...args,
				callback: (r) => resolve(r.message),
				error: (r) => reject(r),
			});
		});

	const run_report = async (report_name) => {
		if (report_cache.has(report_name)) return report_cache.get(report_name);
		const message = await frappe_call({
			method: "frappe.desk.query_report.run",
			args: { report_name, filters: {} },
		});
		report_cache.set(report_name, message);
		return message;
	};

	const render_kpis_from_herd = (rows) => {
		const total = rows.length;
		const avg_weight = rows.reduce((a, r) => a + to_number(r.weight_kg), 0) / (total || 1);
		const lactating = rows.filter((r) => r.status === "Lactating").length;
		const dry = rows.filter((r) => r.status === "Dry" || r.status === "Dry Pregnant").length;
		const kpi_html = `
			<div class="dm-kpi"><div class="value">${total}</div><div class="label">${__("Animals in Herd Summary")}</div></div>
			<div class="dm-kpi"><div class="value">${lactating}</div><div class="label">${__("Lactating")}</div></div>
			<div class="dm-kpi"><div class="value">${dry}</div><div class="label">${__("Dry / Dry pregnant")}</div></div>
			<div class="dm-kpi"><div class="value">${format_value(avg_weight, 1)}</div><div class="label">${__("Avg weight (kg)")}</div></div>
		`;
		body.find(".dm-kpis").html(kpi_html);
	};

	const group_counts = (rows, key_field) => {
		const out = {};
		(rows || []).forEach((row) => {
			const k = row[key_field] || __("Not set");
			out[k] = (out[k] || 0) + 1;
		});
		return out;
	};

	const sort_keys = (obj) => Object.keys(obj).sort();

	const aggregate_sum = (rows, group_field, sum_fields, limit) => {
		const map = {};
		(rows || []).forEach((row) => {
			const g = row[group_field];
			if (!g) return;
			if (!map[g]) map[g] = {};
			sum_fields.forEach((f) => {
				map[g][f] = (map[g][f] || 0) + to_number(row[f]);
			});
		});
		let keys = sort_keys(map);
		if (group_field.toLowerCase().includes("date") && keys.length > 1) {
			keys = keys.sort();
		}
		if (limit && keys.length > limit) {
			keys = keys.slice(-limit);
		}
		return { keys, map };
	};

	const base_chart = (height = 280) => ({
		chart: { height, toolbar: { show: false }, fontFamily: "Inter, sans-serif" },
		dataLabels: { enabled: false },
		grid: { borderColor: "rgba(148,163,184,0.25)" },
		legend: { position: "top" },
		stroke: { width: 2, curve: "smooth" },
		tooltip: { shared: true },
	});

	const build_chart_options = (report_name, message) => {
		const rows = (message && message.result) || [];
		const name = report_name;

		if (!rows.length) return null;

		if (name === "Herd Summary Report") {
			const by_status = group_counts(rows, "status");
			const labels = sort_keys(by_status);
			return {
				chart: { ...base_chart().chart, type: "donut" },
				labels,
				series: labels.map((k) => by_status[k]),
				colors: ["#16a34a", "#22c55e", "#84cc16", "#f59e0b", "#ef4444", "#64748b"],
				legend: { position: "bottom" },
				title: { text: __("Animals by status"), align: "left", style: { fontSize: "13px" } },
			};
		}

		if (name === "Daily Milk Production Report") {
			const { keys, map } = aggregate_sum(rows, "recording_date", ["morning_l", "evening_l", "total_yield_l"], 45);
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "area", stacked: false },
				xaxis: { categories: keys, labels: { rotate: -45 } },
				series: [
					{ name: __("Morning (L)"), data: keys.map((k) => to_number(map[k].morning_l)) },
					{ name: __("Evening (L)"), data: keys.map((k) => to_number(map[k].evening_l)) },
					{ name: __("Total (L)"), data: keys.map((k) => to_number(map[k].total_yield_l)) },
				],
				colors: ["#2563eb", "#f59e0b", "#16a34a"],
			};
		}

		if (name === "Milk Dispatch and Revenue Report") {
			const { keys, map } = aggregate_sum(rows, "log_date", ["revenue"], 45);
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "bar" },
				xaxis: { categories: keys, labels: { rotate: -45 } },
				series: [{ name: __("Revenue"), data: keys.map((k) => to_number(map[k].revenue)) }],
				colors: ["#7c3aed"],
				plotOptions: { bar: { borderRadius: 6, columnWidth: "55%" } },
			};
		}

		if (name === "Breeding Performance Report") {
			const counts = group_counts(rows, "result");
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "donut" },
				labels: sort_keys(counts),
				series: sort_keys(counts).map((k) => counts[k]),
				colors: ["#22c55e", "#f97316", "#64748b", "#ef4444"],
			};
		}

		if (name === "Animal Health History Report") {
			const counts = group_counts(rows, "event_type");
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "bar" },
				xaxis: { categories: sort_keys(counts) },
				series: [{ name: __("Events"), data: sort_keys(counts).map((k) => counts[k]) }],
				colors: ["#0ea5e9"],
				plotOptions: { bar: { borderRadius: 6, columnWidth: "55%" } },
			};
		}

		if (name === "Vaccination Due Report") {
			const top = [...rows]
				.map((r) => ({ label: r.animal || __("No animal"), v: to_number(r.days_overdue) }))
				.sort((a, b) => b.v - a.v)
				.slice(0, 15);
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "bar" },
				xaxis: { categories: top.map((t) => t.label), labels: { rotate: -35 } },
				series: [{ name: __("Days overdue"), data: top.map((t) => t.v) }],
				colors: ["#ef4444"],
				plotOptions: { bar: { horizontal: true, borderRadius: 6 } },
			};
		}

		if (name === "Feed Cost Per Litre Report") {
			const { keys, map } = aggregate_sum(rows, "log_date", ["cost_per_litre", "total_feed_cost", "total_milk_l"], 45);
			return {
				...base_chart(300),
				chart: { ...base_chart(300).chart, type: "line" },
				xaxis: { categories: keys, labels: { rotate: -45 } },
				series: [
					{ name: __("Cost / L"), data: keys.map((k) => to_number(map[k].cost_per_litre)) },
					{ name: __("Milk (L)"), data: keys.map((k) => to_number(map[k].total_milk_l)) },
				],
				colors: ["#ef4444", "#16a34a"],
				yaxis: [
					{ title: { text: __("Cost / L") } },
					{ opposite: true, title: { text: __("Milk (L)") } },
				],
			};
		}

		if (name === "Equipment Maintenance Due Report") {
			const pts = rows
				.map((r) => ({
					label: r.equipment_name || __("Equipment"),
					v: to_number(r.days_to_service),
				}))
				.sort((a, b) => a.v - b.v)
				.slice(0, 18);
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "bar" },
				xaxis: { categories: pts.map((p) => p.label), labels: { rotate: -35 } },
				series: [{ name: __("Days to service"), data: pts.map((p) => p.v) }],
				colors: ["#0f766e"],
				plotOptions: { bar: { horizontal: true, borderRadius: 6 } },
			};
		}

		if (name === "Profit and Loss Summary Report") {
			const { keys, map } = aggregate_sum(rows, "period", ["total_income", "net_profit_loss"], 24);
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "line" },
				xaxis: { categories: keys, labels: { rotate: -35 } },
				series: [
					{ name: __("Total income"), data: keys.map((k) => to_number(map[k].total_income)) },
					{ name: __("Net P/L"), data: keys.map((k) => to_number(map[k].net_profit_loss)) },
				],
				colors: ["#16a34a", "#111827"],
			};
		}

		if (name === "Cost Per Animal Per Month") {
			const by_animal = {};
			rows.forEach((r) => {
				const a = r.animal || __("Unknown");
				by_animal[a] = (by_animal[a] || 0) + to_number(r.margin);
			});
			const top = sort_keys(by_animal)
				.map((k) => ({ label: k, v: by_animal[k] }))
				.sort((a, b) => b.v - a.v)
				.slice(0, 15);
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "bar" },
				xaxis: { categories: top.map((t) => t.label), labels: { rotate: -35 } },
				series: [{ name: __("Margin (sum)"), data: top.map((t) => t.v) }],
				colors: ["#2563eb"],
				plotOptions: { bar: { borderRadius: 6, columnWidth: "55%" } },
			};
		}

		if (name === "Milk Board Compliance Report") {
			const { keys, map } = aggregate_sum(rows, "recording_date", ["avg_scc", "total_yield_l"], 45);
			return {
				...base_chart(300),
				chart: { ...base_chart(300).chart, type: "line" },
				xaxis: { categories: keys, labels: { rotate: -45 } },
				series: [
					{ name: __("Avg SCC"), data: keys.map((k) => to_number(map[k].avg_scc)) },
					{ name: __("Total yield (L)"), data: keys.map((k) => to_number(map[k].total_yield_l)) },
				],
				colors: ["#ef4444", "#16a34a"],
				yaxis: [
					{ title: { text: __("SCC") } },
					{ opposite: true, title: { text: __("Litres") } },
				],
				annotations: {
					yaxis: [
						{
							y: 400000,
							borderColor: "#f97316",
							label: {
								borderColor: "#f97316",
								style: { color: "#fff", background: "#f97316" },
								text: __("SCC threshold (400k)"),
							},
						},
					],
				},
			};
		}

		if (name === "Herd Traceability Report") {
			const counts = group_counts(rows, "movement_type");
			return {
				...base_chart(),
				chart: { ...base_chart().chart, type: "bar" },
				xaxis: { categories: sort_keys(counts) },
				series: [{ name: __("Movements"), data: sort_keys(counts).map((k) => counts[k]) }],
				colors: ["#6366f1"],
				plotOptions: { bar: { borderRadius: 6, columnWidth: "55%" } },
			};
		}

		// Generic fallback: first numeric column summed by first column
		const first_key = Object.keys(rows[0] || {})[0];
		const numeric_field = Object.keys(rows[0] || {}).find((k) => {
			if (k === first_key) return false;
			const v = rows[0][k];
			return to_number(v) !== 0 || v === 0;
		});
		if (!first_key || !numeric_field) return null;
		const { keys, map } = aggregate_sum(rows, first_key, [numeric_field], 20);
		return {
			...base_chart(),
			chart: { ...base_chart().chart, type: "bar" },
			xaxis: { categories: keys, labels: { rotate: -35 } },
			series: [{ name: numeric_field, data: keys.map((k) => to_number(map[k][numeric_field])) }],
			colors: ["#64748b"],
			title: { text: `${numeric_field} by ${first_key}`, align: "left", style: { fontSize: "12px" } },
		};
	};

	const render_report_card = (meta) => {
		const slug = slugify(meta.name);
		const card = $(`
			<div class="dm-rpt-card" data-report="${frappe.utils.escape_html(meta.name)}">
				<div class="dm-rpt-head">
					<h4 class="dm-rpt-title">${frappe.utils.escape_html(meta.report_name || meta.name)}</h4>
					<a class="dm-rpt-link" href="/app/query-report/${encodeURIComponent(meta.name)}">${__("Open report")} →</a>
				</div>
				<div class="dm-chart" id="dm-chart-${slug}"></div>
				<div class="dm-chart-status">${__("Loading chart…")}</div>
			</div>
		`);
		body.find("#dm-report-charts").append(card);
		return card;
	};

	const render_chart_into_card = async (card, report_name, message) => {
		const status_el = card.find(".dm-chart-status");
		const chart_el = card.find(".dm-chart").get(0);
		const opts = build_chart_options(report_name, message);
		if (!opts) {
			status_el.text(__("No rows returned for this report."));
			return;
		}
		status_el.text("");
		const chart = new ApexCharts(chart_el, opts);
		charts.push(chart);
		await chart.render();
	};

	const refresh_dashboard = async () => {
		destroy_charts();
		report_cache.clear();
		body.find("#dm-report-charts").empty();

		try {
			const herd_message = await run_report("Herd Summary Report");
			const herd_rows = (herd_message && herd_message.result) || [];
			render_kpis_from_herd(herd_rows);

			const reports = await frappe_call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Report",
					fields: ["name", "report_name"],
					filters: { module: "Dairy Management" },
					limit_page_length: 200,
					order_by: "report_name asc",
				},
			});

			await load_apex();

			for (const rep of reports || []) {
				const card = render_report_card(rep);
				try {
					let message;
					if (rep.name === "Herd Summary Report") {
						message = herd_message;
					} else {
						message = await run_report(rep.name);
					}
					await render_chart_into_card(card, rep.name, message);
				} catch (e) {
					card.find(".dm-chart-status").text(__("Could not load this report for charting."));
				}
			}
		} catch (e) {
			frappe.show_alert({ message: __("Could not load dashboard data."), indicator: "red" });
		}
	};

	body.find(".dm-refresh").on("click", () => {
		refresh_dashboard();
	});

	refresh_dashboard();
};
