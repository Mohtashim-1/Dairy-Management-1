frappe.pages["herd-summary-report"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Herd Reports Dashboard",
		single_column: true,
	});

	const body = $(`
		<div class="dm-dashboard">
			<div class="dm-banner">
				<div>
					<div class="dm-kicker">Dairy Management</div>
					<h3>Reports & Analytics</h3>
					<p>Herd KPIs and report access from one dashboard.</p>
				</div>
				<a class="dm-btn" href="/app/query-report/Herd%20Summary%20Report">Open Tabular Report</a>
			</div>
			<div class="dm-kpis"></div>
			<div class="dm-charts">
				<div class="dm-card"><h4>Animals by Status</h4><div id="dm-status-chart"></div></div>
				<div class="dm-card"><h4>Animals by Breed</h4><div id="dm-breed-chart"></div></div>
			</div>
			<div class="dm-card">
				<h4>All Dairy Reports</h4>
				<div class="dm-report-links"></div>
			</div>
		</div>
	`);

	const style = `
		.dm-dashboard { font-family: Inter, sans-serif; }
		.dm-banner { background: linear-gradient(135deg,#14532d,#16a34a); color: #fff; border-radius: 16px; padding: 16px; display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 12px; }
		.dm-banner h3 { margin: 2px 0; }
		.dm-banner p { margin: 0; opacity: .9; }
		.dm-kicker { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; opacity: .85; }
		.dm-btn { background: #fff; color: #14532d; text-decoration: none; padding: 8px 12px; border-radius: 999px; font-weight: 600; }
		.dm-kpis { display: grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap: 10px; margin-bottom: 10px; }
		.dm-kpi { border: 1px solid #e5e7eb; border-radius: 12px; padding: 10px; background: #fff; }
		.dm-kpi .value { font-size: 22px; font-weight: 700; }
		.dm-kpi .label { color: #6b7280; font-size: 12px; margin-top: 2px; }
		.dm-charts { display: grid; grid-template-columns: repeat(auto-fit,minmax(340px,1fr)); gap: 10px; margin-bottom: 10px; }
		.dm-card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; background: #fff; }
		.dm-card h4 { margin: 0 0 10px 0; }
		.dm-report-links { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 8px; }
		.dm-report-links a { display: block; text-decoration: none; border: 1px solid #d1d5db; border-radius: 10px; padding: 10px; color: #111827; }
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

	const render_kpis = (rows) => {
		const total = rows.length;
		const avg_weight = rows.reduce((a, r) => a + to_number(r.weight_kg), 0) / (total || 1);
		const lactating = rows.filter((r) => r.status === "Lactating").length;
		const dry = rows.filter((r) => r.status === "Dry" || r.status === "Dry Pregnant").length;
		const kpi_html = `
			<div class="dm-kpi"><div class="value">${total}</div><div class="label">Total Animals</div></div>
			<div class="dm-kpi"><div class="value">${lactating}</div><div class="label">Lactating</div></div>
			<div class="dm-kpi"><div class="value">${dry}</div><div class="label">Dry / Dry Pregnant</div></div>
			<div class="dm-kpi"><div class="value">${format_value(avg_weight, 1)}</div><div class="label">Avg Weight (kg)</div></div>
		`;
		body.find(".dm-kpis").html(kpi_html);
	};

	const group_counts = (rows, key) => {
		const out = {};
		(rows || []).forEach((row) => {
			const label = row[key] || "Not Set";
			out[label] = (out[label] || 0) + 1;
		});
		return out;
	};

	const render_charts = async (rows) => {
		await load_apex();
		const status_counts = group_counts(rows, "status");
		const breed_counts = group_counts(rows, "breed");

		new ApexCharts(document.querySelector("#dm-status-chart"), {
			chart: { type: "donut", height: 320, toolbar: { show: false } },
			series: Object.values(status_counts),
			labels: Object.keys(status_counts),
			legend: { position: "bottom" }
		}).render();

		new ApexCharts(document.querySelector("#dm-breed-chart"), {
			chart: { type: "bar", height: 320, toolbar: { show: false } },
			series: [{ name: "Animals", data: Object.values(breed_counts) }],
			xaxis: { categories: Object.keys(breed_counts) },
			plotOptions: { bar: { borderRadius: 5 } }
		}).render();
	};

	const render_report_links = () => {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Report",
				fields: ["name", "report_name"],
				filters: { module: "Dairy Management" },
				limit_page_length: 100,
				order_by: "name asc"
			},
			callback: function (r) {
				const reports = r.message || [];
				const html = reports.length
					? reports.map((d) => `<a href="/app/query-report/${encodeURIComponent(d.name)}">${frappe.utils.escape_html(d.report_name || d.name)}</a>`).join("")
					: "<div>No reports found in Dairy Management module.</div>";
				body.find(".dm-report-links").html(html);
			}
		});
	};

	frappe.call({
		method: "frappe.desk.query_report.run",
		args: { report_name: "Herd Summary Report" },
		callback: function (r) {
			const rows = (r.message && r.message.result) || [];
			render_kpis(rows);
			render_report_links();
			render_charts(rows).catch(() => {
				frappe.show_alert({ message: __("Could not load ApexCharts"), indicator: "orange" });
			});
		}
	});
};