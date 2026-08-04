import { useEffect, useState } from "react";
import { todayIST } from "@/utils/date";
import api from "@/services/api";
import { useAuthStore } from "@/services/authStore";

const FIELD_GROUPS = [
  {
    title: "Savings Bank",
    fields: [
      { name: "sb_opened", label: "SB Accounts Opened" },
      { name: "sb_closed", label: "SB Accounts Closed" },
      { name: "net_accounts", label: "Net Accounts" },
    ],
  },
  {
    title: "PLI / Insurance",
    fields: [
      { name: "pli_policies", label: "PLI Policies" },
      { name: "sum_assured", label: "Sum Assured", step: "0.01" },
      { name: "premium", label: "Premium Collected", step: "0.01" },
    ],
  },
  {
    title: "Mail & Logistics",
    fields: [
      { name: "speed_post_document", label: "Speed Post - Documents" },
      { name: "speed_post_parcel", label: "Speed Post - Parcels" },
      { name: "business_post", label: "Business Post" },
      { name: "logistics", label: "Logistics" },
      { name: "international_letter", label: "International Letter Mail" },
    ],
  },
  {
    title: "Aadhaar",
    fields: [
      { name: "aadhaar_transactions", label: "Aadhaar Transactions" },
      { name: "aadhaar_amount", label: "Aadhaar Amount", step: "0.01" },
    ],
  },
];

const NUMERIC_FIELDS = FIELD_GROUPS.flatMap((g) => g.fields.map((f) => f.name));

function emptyForm(today: string): Record<string, any> {
  const base: Record<string, any> = { report_date: today, office_id: "", office_name: "", office_code: "" };
  NUMERIC_FIELDS.forEach((name) => {
    base[name] = "";
  });
  return base;
}

export default function DailyMonitoringPage() {
  const { user } = useAuthStore();
  const today = todayIST();

  const [loadingOffices, setLoadingOffices] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [offices, setOffices] = useState<any[]>([]);
  const [form, setForm] = useState(emptyForm(today));
  const [errors, setErrors] = useState<Record<string, string | undefined>>({});
  const [notice, setNotice] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [existingReport, setExistingReport] = useState<Record<string, any> | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);

  useEffect(() => {
    if (user?.role === "OFFICE_ADMIN" && user.office_id) {
      loadMyOffice();
    } else {
      loadOffices();
    }
  }, [user]);

  async function loadMyOffice() {
    try {
      const res = await api.get(`/offices/${user?.office_id}`);
      const office = res.data.data;

      setForm(prev => ({
        ...prev,
        office_id: office.id,
        office_name: office.office_name,
        office_code: office.office_code,
      }));
    } catch (e) {
      console.error(e);
      setNotice({
        type: "error",
        message: "Unable to load your office profile."
      });
    }
  }

  useEffect(() => {
    if (form.office_id && form.report_date) {
      checkExistingReport();
    } else {
      setExistingReport(null);
      setIsEditMode(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.office_id, form.report_date]);

  async function loadOffices() {
    try {
      setLoadingOffices(true);
      const res = await api.get("/offices?page_size=100");
      setOffices(res.data.data || []);
    } catch (e) {
      console.error(e);
      setNotice({ type: "error", message: "Unable to load offices. Please refresh the page." });
    } finally {
      setLoadingOffices(false);
    }
  }

  async function checkExistingReport() {
    try {
      const res = await api.get("/daily-reports/", {
        params: { report_date: form.report_date, office_id: form.office_id },
      });
      const reports = res.data || [];
      const match = reports.find((r: any) => r.office_id === form.office_id);
      if (match) {
        setExistingReport(match);
      } else {
        setExistingReport(null);
        setIsEditMode(false);
      }
    } catch (e) {
      console.error(e);
    }
  }

  function loadReportIntoForm(report: Record<string, any>) {
    const next = { ...form };
    Object.keys(next).forEach((key) => {
      if (report[key] !== undefined && report[key] !== null) {
        next[key] = String(report[key]);
      }
    });
    setForm(next);
    setIsEditMode(true);
    setNotice(null);
  }

  function handleOfficeChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const officeId = e.target.value;
    const selected: any = offices.find((o: any) => o.id === officeId);
    setForm((prev) => ({
      ...prev,
      office_id: officeId,
      office_name: selected ? selected.office_name : "",
      office_code: selected ? selected.office_code : "",
    }));
    setErrors((prev) => ({ ...prev, office_id: undefined }));
  }

  function handleDateChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, report_date: e.target.value }));
  }

  function update(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  function validate() {
    const next: Record<string, string> = {};
    if (!form.office_id) {
      next.office_id = "Please select an office.";
    }
    if (!form.report_date) {
      next.report_date = "Please select a date.";
    }
    NUMERIC_FIELDS.forEach((name) => {
      const value = form[name];
      if (value === "" || value === null || value === undefined) {
        next[name] = "Required.";
        return;
      }
      const num = Number(value);
      if (Number.isNaN(num) || num < 0) {
        next[name] = "Must be a valid non-negative number.";
      }
    });
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  function buildPayload() {
    const payload: Record<string, string | number | undefined> = {
      report_date: form.report_date,
      office_id: form.office_id,
      office_name: form.office_name,
      office_code: form.office_code || undefined,
    };
    NUMERIC_FIELDS.forEach((name) => {
      const isDecimal = ["sum_assured", "premium", "aadhaar_amount"].includes(name);
      payload[name] = isDecimal ? parseFloat(form[name] || "0") : parseInt(form[name] || "0", 10);
    });
    return payload;
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setNotice(null);

    if (!validate()) {
      setNotice({ type: "error", message: "Please fix the highlighted fields before submitting." });
      return;
    }

    if (existingReport && !isEditMode) {
      setNotice({
        type: "error",
        message: "A report for this office and date already exists. Click 'Edit Existing Report' to update it.",
      });
      return;
    }

    try {
      setSubmitting(true);
      await api.post("/daily-reports/", buildPayload());
      setNotice({
        type: "success",
        message: isEditMode ? "Report updated successfully." : "Report submitted successfully.",
      });
      await checkExistingReport();
    } catch (err: any) {
      console.error(err);
      const backendMessage = err?.response?.data?.error?.message || err?.response?.data?.detail;
      setNotice({ type: "error", message: backendMessage || "Submission failed. Please try again." });
    } finally {
      setSubmitting(false);
    }
  }

  function startEdit() {
    if (existingReport) {
      loadReportIntoForm(existingReport);
    }
  }

  function startNew() {
    setForm(emptyForm(today));
    setIsEditMode(false);
    setExistingReport(null);
    setErrors({});
    setNotice(null);
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Daily Monitoring Report</h1>

      {notice && (
        <div
          className={`mb-4 p-3 rounded-lg border ${
            notice.type === "success"
              ? "bg-green-50 border-green-300 text-green-800"
              : "bg-red-50 border-red-300 text-red-800"
          }`}
        >
          {notice.message}
        </div>
      )}

      {existingReport && !isEditMode && (
        <div className="mb-4 p-3 rounded-lg border bg-yellow-50 border-yellow-300 text-yellow-800 flex items-center justify-between">
          <span>A report already exists for this office and date.</span>
          <button
            type="button"
            onClick={startEdit}
            className="ml-4 px-3 py-1 rounded-md bg-yellow-600 text-white text-sm"
          >
            Edit Existing Report
          </button>
        </div>
      )}

      {isEditMode && (
        <div className="mb-4 p-3 rounded-lg border bg-blue-50 border-blue-300 text-blue-800 flex items-center justify-between">
          <span>Editing existing report for {form.office_name || "selected office"}.</span>
          <button type="button" onClick={startNew} className="ml-4 px-3 py-1 rounded-md bg-blue-600 text-white text-sm">
            Start New Instead
          </button>
        </div>
      )}

      <form onSubmit={submit} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <input
              type="date"
              name="report_date"
              value={form.report_date}
              onChange={handleDateChange}
              className={`border rounded-lg p-3 w-full ${errors.report_date ? "border-red-500" : ""}`}
            />
            {errors.report_date && <p className="text-red-600 text-sm mt-1">{errors.report_date}</p>}
          </div>

          {user?.role === "OFFICE_ADMIN" ? (
            <div>
              <label className="block text-sm text-gray-600 mb-1">Office</label>
              <input
                type="text"
                value={form.office_name}
                readOnly
                className="border rounded-lg p-3 w-full bg-gray-100"
              />
            </div>
          ) : (
            <div>
              <select
                name="office_id"
                value={form.office_id}
                onChange={handleOfficeChange}
                className={`border rounded-lg p-3 w-full ${errors.office_id ? "border-red-500" : ""}`}
              >
                <option value="">{loadingOffices ? "Loading Offices..." : "Select Office"}</option>
                {offices.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.office_name}
                  </option>
                ))}
              </select>
              {errors.office_id && <p className="text-red-600 text-sm mt-1">{errors.office_id}</p>}
            </div>
          )}
        </div>

        {FIELD_GROUPS.map((group) => (
          <div key={group.title}>
            <h2 className="text-lg font-semibold mb-2">{group.title}</h2>
            <div className="grid grid-cols-3 gap-4">
              {group.fields.map((f) => (
                <div key={f.name}>
                  <label className="block text-sm text-gray-600 mb-1">{f.label}</label>
                  <input
                    type="number"
                    name={f.name}
                    min="0"
                    step={f.step || "1"}
                    value={form[f.name]}
                    onChange={update}
                    className={`border rounded-lg p-3 w-full ${errors[f.name] ? "border-red-500" : ""}`}
                  />
                  {errors[f.name] && <p className="text-red-600 text-sm mt-1">{errors[f.name]}</p>}
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 rounded-lg bg-blue-600 text-white font-medium disabled:opacity-50"
          >
            {submitting ? "Submitting..." : isEditMode ? "Update Report" : "Submit Report"}
          </button>
          {isEditMode && (
            <button type="button" onClick={startNew} className="px-6 py-3 rounded-lg border">
              Cancel Edit
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
