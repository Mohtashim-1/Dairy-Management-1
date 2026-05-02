// Copyright (c) 2026, mohtashim and contributors
// For license information, please see license.txt

frappe.pages["milk-recording-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Milk Recording Dashboard"),
		single_column: true,
	});

	const body = $(`
		<div class="dm-milk-dash">
			<p class="text-muted">${__("Live summary of milk entries. Use Refresh after recording.")}</p>
			<div class="dm-milk-kpis row"></div>
			<div class="dm-milk-sessions small text-muted" style="margin-top:8px"></div>
			<div style="margin-top:16px">
				<a class="btn btn-primary" href="/app/milk-recording/new">${__("New Milk Recording")}</a>
				<a class="btn btn-default" href="/app/milk-recording">${__("Milk Recording List")}</a>
			</div>
		</div>
	`);

	$(page.body).empty().append(body);

	const render = (data) => {
		const t = data.today || {};
		const kpis = [
			{ label: __("Today total (L)"), value: flt(t.total_l) },
			{ label: __("Recordings today"), value: cint(t.recordings) },
			{ label: __("Last 7 days total (L)"), value: flt(data.last_7_days_total_l) },
		];
		const $row = page.body.find(".dm-milk-kpis").empty();
		kpis.forEach((k) => {
			$row.append(
				`<div class="col-md-4"><div class="well" style="padding:12px">
					<div style="font-size:22px;font-weight:700">${k.value}</div>
					<div class="text-muted">${k.label}</div>
				</div></div>`
			);
		});
		const lines = (data.session_split || [])
			.map((s) => `${__(s.session)}: ${flt(s.litres)} L`)
			.join(" · ");
		page.body.find(".dm-milk-sessions").text(
			lines ? `${__("Today by session")}: ${lines}` : __("No recordings for today.")
		);
	};

	const load = () => {
		frappe.call({
			method: "dairy_management.dairy_dashboard.get_milk_recording_dashboard_data",
			callback(r) {
				if (r.message) {
					render(r.message);
				}
			},
		});
	};

	load();
	page.set_secondary_action(__("Refresh"), () => load());

	function flt(v) {
		if (v === null || v === undefined || v === "") return 0;
		const n = parseFloat(v);
		return isNaN(n) ? 0 : Math.round(n * 100) / 100;
	}
	function cint(v) {
		return parseInt(v, 10) || 0;
	}
};
